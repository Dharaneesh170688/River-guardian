import cv2
import json
import os
import glob
import numpy as np

def visualize_frames(debug_dir):
    image_files = glob.glob(os.path.join(debug_dir, "*.jpg"))
    
    if not image_files:
        print(f"No JPG files found in {debug_dir}")
        return

    # Typical 17-keypoint skeleton connections (COCO format)
    # Nose, L/R Eye, L/R Ear, L/R Shoulder, L/R Elbow, L/R Wrist, L/R Hip, L/R Knee, L/R Ankle
    skeleton = [
        (0, 1), (0, 2), (1, 3), (2, 4),  # Head
        (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # Torso and Arms
        (5, 11), (6, 12), (11, 12),  # Torso
        (11, 13), (13, 15), (12, 14), (14, 16)  # Legs
    ]
    
    for img_path in image_files:
        json_path = img_path.replace(".jpg", ".json")
        if not os.path.exists(json_path):
            print(f"Skipping {img_path}: No matching JSON")
            continue
            
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        h, w = img.shape[:2]
        
        with open(json_path, 'r') as f:
            keypoints = json.load(f)
            
        pts = []
        for i, kp in enumerate(keypoints):
            # Keypoints might be normalized (0-1) or absolute.
            # If they are normalized, multiply by w, h
            x = kp['x']
            y = kp['y']
            if x <= 1.0 and y <= 1.0:
                x = int(x * w)
                y = int(y * h)
            else:
                x = int(x)
                y = int(y)
                
            pts.append((x, y, kp['score']))
            
            # Draw keypoint
            color = (0, 255, 0) if kp['score'] > 0.5 else (0, 0, 255)
            cv2.circle(img, (x, y), 5, color, -1)
            
        # Draw skeleton
        for connection in skeleton:
            if connection[0] < len(pts) and connection[1] < len(pts):
                pt1 = pts[connection[0]]
                pt2 = pts[connection[1]]
                if pt1[2] > 0.5 and pt2[2] > 0.5:
                    cv2.line(img, (pt1[0], pt1[1]), (pt2[0], pt2[1]), (255, 255, 0), 2)
                    
        out_path = img_path.replace(".jpg", "_annotated.png")
        cv2.imwrite(out_path, img)
        print(f"Saved {out_path}")

if __name__ == "__main__":
    debug_dir = "./debug_frames"
    if not os.path.exists(debug_dir):
        print(f"Please run: adb pull /sdcard/Android/data/<your.package>/files/debug_frames {debug_dir}")
    else:
        visualize_frames(debug_dir)
