import cv2
import os
import sys
import time
import numpy as np
import json
import subprocess
import uuid

# Add SGG_Bench to path so we can import the standalone ONNX demo
sgg_bench_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SGG_Bench'))
sys.path.append(sgg_bench_path)
from standalone_onnx_demo import SGG_ONNX_Standalone

class FallDetectionExplainer:
    def __init__(self, onnx_path, provider='CPUExecutionProvider'):
        # Initialize the SGG Bench model (IndoorVG or PSG recommended)
        self.sgg_model = SGG_ONNX_Standalone(
            onnx_path=onnx_path, 
            provider=provider, 
            rel_conf=0.05, # Lowered to get more relationship hits
            box_conf=0.25  # Lowered further to detect bodies in awkward poses or motion blur
        )

    def analyze_frame(self, frame):
        """
        Processes a single frame and extracts the scene graph.
        """
        frame_h, frame_w = frame.shape[:2]
        frame_area = frame_h * frame_w

        # 1. Run SGG Inference
        boxes, rels, full_rels, _ = self.sgg_model.predict(frame, visualize=True)
        
        if not full_rels:
            return "No relations detected.", None, frame.copy(), {}
            
        # --- Custom Visualization Filter ---
        # Only draw hitboxes for people, floors, and other common furniture/surfaces
        person_keywords = ['person', 'man', 'woman', 'boy', 'girl', 'child', 'human', 'body', 'people', 'patient']
        important_classes = person_keywords + ['floor', 'carpet', 'rug', 'ground', 'couch', 'bed', 'chair', 'table', 'desk']
        
        # Identify smaller person hitboxes that touch larger person hitboxes to ignore them
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
                    inter_x1, inter_y1 = max(xi1, xj1), max(yi1, yj1)
                    inter_x2, inter_y2 = min(xi2, xj2), min(yi2, yj2)
                    if inter_x2 > inter_x1 and inter_y2 > inter_y1:
                        # If they touch/intersect at all, ignore the smaller box
                        ignored_person_indices.add(i)

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
            # Only keep relationships where BOTH objects are in our important list
            if s in old_to_new and o in old_to_new:
                new_rel = rel.copy()
                new_rel[0], new_rel[1] = old_to_new[s], old_to_new[o]
                vis_rels.append(new_rel)
                
        vis_rels = np.array(vis_rels) if vis_rels else np.empty((0, 5))
        vis_image = self.sgg_model.visualize(frame.copy(), vis_boxes, vis_rels)
        # -----------------------------------
            
        # Filter to log relationships where a person is interacting with a ground surface
        target_relations = ['lying on', 'laying on', 'falling off', 'on', 'touching', 'sitting on']
        surface_keywords = ['floor', 'ground', 'carpet', 'rug', 'mat', 'tile', 'wood']
        
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
                if any(p in subj_cls for p in person_keywords) and any(surf in obj_cls for surf in surface_keywords):
                    if parts[1] in target_relations:
                        filtered_rels.append(rel)
            
        # Format the relations into a single descriptive string
        scene_description = ", ".join(filtered_rels)
        if scene_description:
            print(f"Detected Scene Graph: {scene_description}")
        
        # More robust fall detection: iterate through relations to find a person lying/laying on the floor.
        is_fall = False
        trigger_reason = "None"
        for rel_str in filtered_rels:
            # To explicitly ignore relations like 'wearing', we parse the triplet
            # and check each part individually for a more robust detection.
            # Format: "ID_subj_class - relation - ID_obj_class: (score)"
            main_part = rel_str.split(':')[0]
            parts = main_part.split(' - ')
            if len(parts) == 3:
                # e.g. "0_person" -> "person"
                subj_idx = int(parts[0].split('_')[0])
                subj_cls = parts[0].split('_', 1)[-1]
                relation = parts[1]
                # e.g. "1_floor-wood" -> "floor-wood"
                obj_cls = parts[2].split('_', 1)[-1]

                if any(p in subj_cls for p in person_keywords) and any(surf in obj_cls for surf in surface_keywords):
                    if relation in ('lying on', 'laying on', 'falling off', 'on', 'touching', 'sitting on'):
                        x1, y1, x2, y2, cls_id, score = boxes[subj_idx]
                        width, height = x2 - x1, y2 - y1
                        
                        # Guard against SGG model hallucinating explicit fall relations when standing upright.
                        # We ensure the box is significant in size but not taking up the entire screen (>40% area).
                        # Note: This area limit is ONLY applied to the person box, surfaces like the floor can be larger.
                        box_area = width * height
                        if height > (frame_h * 0.05) and width > (frame_w * 0.15) and (box_area / frame_area) < 0.4:
                            # Require aspect ratio > 1.2 only for ambiguous relations to avoid false positives.
                            if relation in ('lying on', 'laying on', 'falling off') or (width / height) > 1.2:
                                is_fall = True
                                trigger_reason = "SGG Relation"
                                break  # A fall is detected, no need to check further

        # 3. Ultimate Fallback: Check bounding boxes of all detected people directly.
        # Often, the SGG model detects the person but completely misses the "floor" as an object.
        if not is_fall:
            for i, box in enumerate(boxes):
                if i in ignored_person_indices:
                    continue
                cls_name = self.sgg_model.obj_classes.get(int(box[4]), '?')
                if any(p in cls_name for p in person_keywords):
                    x1, y1, x2, y2, _, _ = box
                    width, height = x2 - x1, y2 - y1
                    
                    box_area = width * height
                    # Size checks ignore small false positive boxes (like an isolated arm misclassified).
                    # We also ignore boxes covering >40% of the screen (person standing extremely close to camera).
                    if height > (frame_h * 0.05) and width > (frame_w * 0.15) and (box_area / frame_area) < 0.4 and (width / height) > 1.2:
                        is_fall = True
                        trigger_reason = "Bounding Box Fallback"
                        filtered_rels.append(f"{i}_{cls_name} - lying on - floor: (inferred by bounding box)")
                        break

        output = "Yes" if is_fall else "No"

        # Collect extensive details for the JSON log
        details = {
            "full_relations": full_rels,
            "filtered_relations": filtered_rels,
            "trigger_reason": trigger_reason,
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

        return output, vis_image, details

    def run_webcam(self, camera_index=0):
        """
        Runs the fall detection continuously on a webcam feed.
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Error: Could not open webcam {camera_index}.")
            return

        print("Starting webcam feed. Press 'q' to exit.")
        
        screenshot_taken = False
        fall_start_time = None
        last_fall_time = None
        leeway_seconds = 1.5  # Duration to keep progress if a frame is dropped
        
        # Create directories for saving falls data
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

            # Safely analyze frame, catching potential local variable error if no boxes are detected
            try:
                decision, annotated_img, details = self.analyze_frame(frame)
            except UnboundLocalError:
                decision, annotated_img, details = "No", frame.copy(), {}
            
            current_time = time.time()
            
            # Håll en rullande historik (senaste 10 sekunderna) av scenrelationer
            event_history = [e for e in event_history if current_time - e['timestamp'] <= 10.0]
            
            # Filtrera relationerna för att minska brus och spara tokens för LLM
            relations = details.get('filtered_relations')
            if not relations:
                # Fallback: Spara endast topp 5 relationer som involverar en person
                person_rels = [r for r in details.get('full_relations', []) if 'person' in r.lower()]
                relations = person_rels[:5]
                
            if relations:
                # Deduplicate: Only append if the scene description has actually changed
                if not event_history or event_history[-1]['scene_description'] != relations:
                    event_history.append({
                        "timestamp": current_time,
                        "scene_description": relations
                    })

            display_img = annotated_img if annotated_img is not None else frame.copy()
            
            # Check if fall has persisted for 3 second to take a screenshot and save details
            if decision == 'Yes':
                last_fall_time = current_time
                if fall_start_time is None:
                    fall_start_time = current_time
                elif not screenshot_taken and (current_time - fall_start_time) >= 3.0:
                    timestamp = time.strftime("%Y%m%d")
                    case_id = uuid.uuid4().hex[:8]
                    filename = os.path.join(img_dir, f"fall_detected_{timestamp}_{case_id}.jpg")
                    json_filename = os.path.join(json_dir, f"fall_detected_{timestamp}_{case_id}.json")
                    
                    cv2.imwrite(filename, display_img) # Saves the annotated image
                    
                    # Skapa en tidslinje som beskriver vad som hände innan och under fallet
                    leading_up_to_fall = []
                    during_fall = []
                    for e in event_history:
                        desc = ", ".join(e['scene_description']) if isinstance(e['scene_description'], list) else e['scene_description']
                        if not desc:
                            continue
                        # Beräkna tiden i förhållande till när fallet startade (ex. T-2.50s eller T+1.00s)
                        time_offset = round(e['timestamp'] - fall_start_time, 2)
                        
                        event_record = {
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e['timestamp'])),
                            "relative_time": f"T{time_offset:+.2f}s",
                            "activity": desc
                        }
                        
                        if e['timestamp'] < fall_start_time:
                            leading_up_to_fall.append(event_record)
                        else:
                            during_fall.append(event_record)
                            
                    # Spara den beskrivande situationen till JSON
                    fall_data = {
                        "case_id": case_id,
                        "timestamp": timestamp,
                        "situation_description": {
                            "leading_up_to_fall": leading_up_to_fall,
                            "during_fall": during_fall
                        },
                        "scene_details_at_capture": details
                    }
                    with open(json_filename, 'w') as f:
                        json.dump(fall_data, f, indent=4)
                        
                    print(f"*** ALERT: Fall detected for 1+ seconds! Saved {filename} & {json_filename} ***")
                    
                    # Trigger the LLM interpreter asynchronously
                    #interpreter_path = os.path.join(os.path.dirname(__file__), "llm_interpreter.py")
                    #subprocess.Popen([sys.executable, interpreter_path, "--json", json_filename, "--image", filename])
                    
                    screenshot_taken = True
            else:
                # Apply leeway: only reset if we haven't seen a fall for > leeway_seconds
                if last_fall_time is not None and (current_time - last_fall_time) > leeway_seconds:
                    fall_start_time = None
                    last_fall_time = None
                    screenshot_taken = False

            # Apply leeway to the UI display so the text doesn't flicker green/red
            display_decision = decision
            if decision == 'No' and last_fall_time is not None and (current_time - last_fall_time) <= leeway_seconds:
                display_decision = 'Yes'

            # Display the decision
            color = (0, 0, 255) if display_decision == 'Yes' else (0, 255, 0)
            cv2.putText(display_img, f"Fall Detected: {display_decision}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            cv2.imshow('Fall Detection (Press q to quit)', display_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Example Usage
    # Make sure to download the IndoorVG model first as it contains 'person', 'floor', and 'laying on'
    onnx_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SGG_Bench', 'react_indoorvg_yolov8m.onnx'))
    
    if not os.path.exists(onnx_model_path):
        print(f"Please download the model first to {onnx_model_path}")
        sys.exit(1)
        
    detector = FallDetectionExplainer(onnx_path=onnx_model_path)
    
    # Run continuously on the webcam
    detector.run_webcam()
