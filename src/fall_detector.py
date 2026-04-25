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

class FallDetectionExplainer:
    def __init__(self, onnx_path, provider='CPUExecutionProvider'):
        self.sgg_model = SGG_ONNX_Standalone(
            onnx_path=onnx_path, 
            provider=provider, 
            rel_conf=0.05,
            box_conf=0.25
        )

    def analyze_frame(self, frame):
        frame_h, frame_w = frame.shape[:2]
        frame_area = frame_h * frame_w

        boxes, rels, full_rels, _ = self.sgg_model.predict(frame, visualize=True)
        
        if not full_rels:
            return "No relations detected.", None, frame.copy(), {}
            
        person_keywords = ['person', 'man', 'woman', 'boy', 'girl', 'child', 'human', 'body', 'people', 'patient']
        important_classes = person_keywords + ['floor', 'carpet', 'rug', 'ground', 'couch', 'bed', 'chair', 'table', 'desk']
        
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
            if s in old_to_new and o in old_to_new:
                new_rel = rel.copy()
                new_rel[0], new_rel[1] = old_to_new[s], old_to_new[o]
                vis_rels.append(new_rel)
                
        vis_rels = np.array(vis_rels) if vis_rels else np.empty((0, 5))
        vis_image = self.sgg_model.visualize(frame.copy(), vis_boxes, vis_rels)
            
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
            
        scene_description = ", ".join(filtered_rels)
        if scene_description:
            print(f"Detected Scene Graph: {scene_description}")
        
        is_fall = False
        trigger_reason = "None"
        for rel_str in filtered_rels:
            main_part = rel_str.split(':')[0]
            parts = main_part.split(' - ')
            if len(parts) == 3:
                subj_idx = int(parts[0].split('_')[0])
                subj_cls = parts[0].split('_', 1)[-1]
                relation = parts[1]
                obj_cls = parts[2].split('_', 1)[-1]

                if any(p in subj_cls for p in person_keywords) and any(surf in obj_cls for surf in surface_keywords):
                    if relation in ('lying on', 'laying on', 'falling off', 'on', 'touching', 'sitting on'):
                        x1, y1, x2, y2, cls_id, score = boxes[subj_idx]
                        width, height = x2 - x1, y2 - y1
                        box_area = width * height
                        if height > (frame_h * 0.05) and width > (frame_w * 0.15) and (box_area / frame_area) < 0.4:
                            if relation in ('lying on', 'laying on', 'falling off') or (width / height) > 1.2:
                                is_fall = True
                                trigger_reason = "SGG Relation"
                                break

        if not is_fall:
            for i, box in enumerate(boxes):
                if i in ignored_person_indices:
                    continue
                cls_name = self.sgg_model.obj_classes.get(int(box[4]), '?')
                if any(p in cls_name for p in person_keywords):
                    x1, y1, x2, y2, _, _ = box
                    width, height = x2 - x1, y2 - y1
                    box_area = width * height
                    if height > (frame_h * 0.05) and width > (frame_w * 0.15) and (box_area / frame_area) < 0.4 and (width / height) > 1.2:
                        is_fall = True
                        trigger_reason = "Bounding Box Fallback"
                        filtered_rels.append(f"{i}_{cls_name} - lying on - floor: (inferred by bounding box)")
                        break

        output = "Yes" if is_fall else "No"

        details = {
            "full_relations": full_rels,
            "filtered_relations": filtered_rels,
            "trigger_reason": trigger_reason,
            "person_boxes": []
        }
        for i, box in enum