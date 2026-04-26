import cv2
import os
import sys
import time
import numpy as np
import json
import uuid

# Add SGG_Bench to path so we can import the standalone ONNX demo
sgg_bench_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SGG_Bench'))
sys.path.append(sgg_bench_path)
from standalone_onnx_demo import SGG_ONNX_Standalone

# How long a relation must persist before triggering an alert (seconds)
RELATION_THRESHOLDS = {
    'falling off':  5.0,   # Almost always dangerous
    'lying on':     5.0,   # Could be yoga, but unlikely for elderly
    'laying on':    5.0,
    'on':           5.0,   # Ambiguous, require more time
    'sitting on':  5.0,   # Give more time before alerting
    'touching':    5.0,
}

ALERT_COOLDOWN = 60.0      # Seconds between alerts
LEEWAY_SECONDS = 1.5       # Allow brief frame drops without resetting


class FallDetectionExplainer:
    def __init__(self, onnx_path, provider='CPUExecutionProvider'):
        self.sgg_model = SGG_ONNX_Standalone(
            onnx_path=onnx_path,
            provider=provider,
            rel_conf=0.05,
            box_conf=0.25
        )
        self.last_alert_time = None
        self.fall_resolved_time = None

    def analyze_frame(self, frame):
        frame_h, frame_w = frame.shape[:2]
        frame_area = frame_h * frame_w

        boxes, rels, full_rels, _ = self.sgg_model.predict(frame, visualize=True)

        if not full_rels:
            return "No", None, None, {}
        person_keywords = ['person', 'man', 'woman', 'boy', 'girl', 'child', 'human', 'body', 'people', 'patient']
        important_classes = person_keywords + ['floor', 'carpet', 'rug', 'ground', 'couch', 'bed', 'chair', 'table', 'desk']
        surface_keywords = ['floor', 'ground', 'carpet', 'rug', 'mat', 'tile', 'wood']

        # --- Ignore smaller overlapping person boxes ---
        ignored_person_indices = set()
        person_indices = []
        for i, box in enumerate(boxes):
            cls_name = self.sgg_model.obj_classes.get(int(box[4]), '?')
            if any(p in cls_name for p in person_keywords):
                person_indices.append(i)

        for i in person_indices:
            for j in person_indices:
                if i == j: continue
                xi1, yi1, xi2, yi2 = boxes[i][:4]
                xj1, yj1, xj2, yj2 = boxes[j][:4]
                area_i = (xi2 - xi1) * (yi2 - yi1)
                area_j = (xj2 - xj1) * (yj2 - yj1)
                if area_i < area_j:
                    inter_x1 = max(xi1, xj1)
                    inter_y1 = max(yi1, yj1)
                    inter_x2 = min(xi2, xj2)
                    inter_y2 = min(yi2, yj2)
                    if inter_x2 > inter_x1 and inter_y2 > inter_y1:
                        ignored_person_indices.add(i)

        # --- Build visualization ---
        keep_box_indices = []
        for i, box in enumerate(boxes):
            if i in ignored_person_indices:
                continue
            cls_name = self.sgg_model.obj_classes.get(int(box[4]), '?')
            if any(imp in cls_name for imp in important_classes):
                keep_box_indices.append(i)

        old_to_new = {old: new for new, old in enumerate(keep_box_indices)}
        vis_boxes = boxes[keep_box_indices]

        vis_rels = []
        for rel in rels:
            s, o = int(rel[0]), int(rel[1])
            if s in old_to_new and o in old_to_new:
                new_rel = rel.copy()
                new_rel[0], new_rel[1] = old_to_new[s], old_to_new[o]
                vis_rels.append(new_rel)

        vis_rels = np.array(vis_rels) if vis_rels else np.empty((0, 5))
        vis_image = self.sgg_model.visualize(frame.copy(), vis_boxes, vis_rels)

        # --- Filter relations: person interacting with ground surface ---
        filtered_rels = []
        for rel in full_rels:
            main_part = rel.split(':')[0]
            parts = main_part.split(' - ')
            if len(parts) == 3:
                subj_idx = int(parts[0].split('_')[0])
                if subj_idx in ignored_person_indices:
                    continue
                subj_cls = parts[0].split('_', 1)[-1]
                obj_cls = parts[2].split('_', 1)[-1]
                relation = parts[1]
                if (any(p in subj_cls for p in person_keywords) and
                        any(surf in obj_cls for surf in surface_keywords) and
                        relation in RELATION_THRESHOLDS):
                    filtered_rels.append(rel)

        if filtered_rels:
            print(f"Detected: {', '.join(filtered_rels)}")

        # --- Determine fall and which relation triggered it ---
        is_fall = False
        trigger_relation = None
        trigger_reason = "None"

        for rel_str in filtered_rels:
            main_part = rel_str.split(':')[0]
            parts = main_part.split(' - ')
            if len(parts) != 3:
                continue

            subj_idx = int(parts[0].split('_')[0])
            subj_cls = parts[0].split('_', 1)[-1]
            relation = parts[1]
            obj_cls = parts[2].split('_', 1)[-1]

            if not (any(p in subj_cls for p in person_keywords) and
                    any(surf in obj_cls for surf in surface_keywords)):
                continue

            x1, y1, x2, y2, cls_id, score = boxes[subj_idx]
            width, height = x2 - x1, y2 - y1
            box_area = width * height

            # Size sanity checks
            if not (height > (frame_h * 0.05) and
                    width > (frame_w * 0.15) and
                    (box_area / frame_area) < 0.4):
                continue

            # Explicit fall relations require aspect ratio > 1.2
            # Ambiguous relations require > 1.5
            if relation in ('lying on', 'laying on', 'falling off'):
                aspect_ok = (width / height) > 1.2
            else:
                aspect_ok = (width / height) > 1.5

            if aspect_ok:
                is_fall = True
                trigger_relation = relation
                trigger_reason = "SGG Relation"
                break

        # --- Fallback: bounding box aspect ratio only ---
        if not is_fall:
            for i, box in enumerate(boxes):
                if i in ignored_person_indices:
                    continue
                cls_name = self.sgg_model.obj_classes.get(int(box[4]), '?')
                if any(p in cls_name for p in person_keywords):
                    x1, y1, x2, y2, _, _ = box
                    width, height = x2 - x1, y2 - y1
                    box_area = width * height
                    if (height > (frame_h * 0.05) and
                            width > (frame_w * 0.15) and
                            (box_area / frame_area) < 0.4 and
                            (width / height) > 1.5):
                        is_fall = True
                        trigger_relation = 'lying on'
                        trigger_reason = "Bounding Box Fallback"
                        filtered_rels.append(f"{i}_{cls_name} - lying on - floor: (inferred by bounding box)")
                        break

        output = "Yes" if is_fall else "No"

        # --- Collect details ---
        details = {
            "full_relations": full_rels,
            "filtered_relations": filtered_rels,
            "trigger_reason": trigger_reason,
            "trigger_relation": trigger_relation,
            "person_boxes": []
        }
        for i, box in enumerate(boxes):
            if i in ignored_person_indices:
                continue
            cls_name = self.sgg_model.obj_classes.get(int(box[4]), '?')
            if any(p in cls_name for p in person_keywords):
                x1, y1, x2, y2, cls_id, score = box
                width, height = x2 - x1, y2 - y1
                details["person_boxes"].append({
                    "class": cls_name,
                    "confidence": float(score),
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "width": float(width),
                    "height": float(height),
                    "aspect_ratio": float(width / height) if height > 0 else 0.0
                })

        return output, vis_image, trigger_relation, details

    def run_webcam(self, camera_index=0, on_fall_callback=None):
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Error: Could not open webcam {camera_index}.")
            return

        print("Starting webcam feed. Press 'q' to exit.")

        relation_start_times = {}   # relation -> time when it started
        last_fall_time = None       # time of last confirmed fall frame
        last_alert_time = None      # time of last alert sent
        alert_sent = False          # has alert been sent for this fall session
        img_dir = os.path.join(os.path.dirname(__file__), "falls_images")
        json_dir = os.path.join(os.path.dirname(__file__), "falls_data")
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)

        event_history = []
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame from webcam.")
                break

            try:
                decision, annotated_img, trigger_relation, details = self.analyze_frame(frame)
            except Exception as e:
                print(f"Frame error: {e}")
                decision, annotated_img, trigger_relation, details = "No", frame.copy(), None, {}

            current_time = time.time()

            # --- Update event history (rolling 10s window) ---
            event_history = [e for e in event_history if current_time - e['timestamp'] <= 10.0]
            relations = details.get('filtered_relations')
            if not relations:
                person_rels = [r for r in details.get('full_relations', []) if 'person' in r.lower()]
                relations = person_rels[:5]
            if relations:
                if not event_history or event_history[-1]['scene_description'] != relations:
                    event_history.append({
                        "timestamp": current_time,
                        "scene_description": relations
                    })

            display_img = annotated_img if annotated_img is not None else frame.copy()

            if decision == 'Yes' and trigger_relation:
                last_fall_time = current_time

                # Start timer for this relation if not already started
                if trigger_relation not in relation_start_times:
                    relation_start_times[trigger_relation] = current_time
                    print(f"Started timer for: {trigger_relation}")

                required_duration = RELATION_THRESHOLDS.get(trigger_relation, 5.0)
                elapsed = current_time - relation_start_times[trigger_relation]

                cooldown_ok = (last_alert_time is None or
                               (current_time - last_alert_time) >= ALERT_COOLDOWN)

                if elapsed >= required_duration and not alert_sent and cooldown_ok:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    case_id = uuid.uuid4().hex[:8]
                    filename = os.path.join(img_dir, f"fall_{timestamp}_{case_id}.jpg")
                    json_filename = os.path.join(json_dir, f"fall_{timestamp}_{case_id}.json")

                    cv2.imwrite(filename, display_img)

                    # Build timeline
                    leading_up_to_fall = []
                    during_fall = []
                    fall_start = relation_start_times[trigger_relation]

                    for e in event_history:
                        desc = (", ".join(e['scene_description'])
                                if isinstance(e['scene_description'], list)
                                else e['scene_description'])
                        if not desc:
                            continue
                        time_offset = round(e['timestamp'] - fall_start, 2)
                        event_record = {
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S",
                                                       time.localtime(e['timestamp'])),
                            "relative_time": f"T{time_offset:+.2f}s",
                            "activity": desc
                        }
                        if e['timestamp'] < fall_start:
                            leading_up_to_fall.append(event_record)
                        else:
                            during_fall.append(event_record)

                    fall_data = {
                        "case_id": case_id,
                        "timestamp": timestamp,
                        "trigger_relation": trigger_relation,
                        "trigger_duration_seconds": round(elapsed, 1),
                        "situation_description": {
                            "leading_up_to_fall": leading_up_to_fall,
                            "during_fall": during_fall
                        },
                        "scene_details_at_capture": details
                    }

                    with open(json_filename, 'w') as f:
                        json.dump(fall_data, f, indent=4)

                    print(f"\n*** ALERT: {trigger_relation} for {elapsed:.1f}s! ***")
                    print(f"Saved: {filename}")

                    if on_fall_callback:
                        on_fall_callback(fall_data, screenshot_path=filename)

                    last_alert_time = current_time
                    alert_sent = True

            else:
                # Reset if no fall detected for > leeway
                if last_fall_time is None or (current_time - last_fall_time) > LEEWAY_SECONDS:
                    relation_start_times.clear()
                    alert_sent = False
                    last_fall_time = None

            # --- Display ---
            display_decision = "Yes" if (
                decision == 'Yes' or
                (last_fall_time is not None and
                 (current_time - last_fall_time) <= LEEWAY_SECONDS)
            ) else "No"

            color = (0, 0, 255) if display_decision == 'Yes' else (0, 255, 0)
            cv2.putText(display_img, f"Fall Detected: {display_decision}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # Show active relation timers on screen
            y_offset = 80
            for rel, start in relation_start_times.items():
                elapsed = current_time - start
                required = RELATION_THRESHOLDS.get(rel, 5.0)
                cv2.putText(display_img,
                            f"{rel}: {elapsed:.1f}s / {required:.1f}s",
                            (20, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                y_offset += 30

            cv2.imshow('SlipWatch (Press q to quit)', display_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    onnx_model_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'SGG_Bench', 'yolov8m', 'model.onnx')
    )

    if not os.path.exists(onnx_model_path):
        print(f"Please download the model first to {onnx_model_path}")
        sys.exit(1)

    detector = FallDetectionExplainer(onnx_path=onnx_model_path)
    detector.run_webcam()
