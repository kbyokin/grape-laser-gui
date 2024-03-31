import time
import datetime
from threading import Thread
import cv2

import torch
from torchvision import transforms

from PIL import Image
import numpy as np
import torchvision.transforms.functional as F

class PadToSquare:
    def __init__(self, fill=(0, 0, 0), padding_mode='constant'):
        self.fill = fill
        self.padding_mode = padding_mode

    def __call__(self, img):
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        w, h = img.size
        max_wh = np.max([w, h])
        hp = int((max_wh - w) / 2)
        vp = int((max_wh - h) / 2)
        padding = (hp, vp, hp, vp)
        return F.pad(img, padding, self.fill, self.padding_mode) # type: ignore

class GrapeDetection(Thread):
    def __init__(self, camera_thread, predictions, prediction_lock, grape_detection_path, removal_path):
        super().__init__()
        self.camera_thread = camera_thread
        self.grape_detection_path = grape_detection_path
        self.removal_path = removal_path
        
        self.grape_detection_model = torch.hub.load('ultralytics/yolov5', 'custom', grape_detection_path)
        self.removal_path_model = torch.load(removal_path, map_location=torch.device('cpu'))
        self.removal_path_model = self.removal_path_model.eval()
        
        self.prediction_lock = prediction_lock  # Lock to ensure thread-safe access to self.predictions
        self.predictions = predictions
        self.running = True
        
        self.berry_removing_transforms = transforms.Compose([
            PadToSquare(fill=(0, 0, 0)),  # Black padding
            transforms.Resize([224, 224]),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], inplace=True),
        ])
        
        self.get_max_remove_index = lambda classification_output: max(range(len(classification_output)), key=lambda i: classification_output[i][1])
        
    def create_cutting_input(self, berry_bbox_xyxy, selected_bunch_bbox, bgr_image, idx):
        target_image = bgr_image.copy()
        berry_bbox_xyxy = [int(coord) for coord in berry_bbox_xyxy]
        selected_bunch_bbox = [int(coord) for coord in selected_bunch_bbox]
        target_image[berry_bbox_xyxy[1]:berry_bbox_xyxy[3], berry_bbox_xyxy[0]:berry_bbox_xyxy[2], :] = (255, 255, 255)
        target_image = target_image[selected_bunch_bbox[1]:selected_bunch_bbox[3], selected_bunch_bbox[0]:selected_bunch_bbox[2], :]
        
        # formatted_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # cv2.imwrite(f'./cutting_pred_images/{formatted_datetime}_{idx}.jpg', target_image)
        
        return self.berry_removing_transforms(target_image) 
    
    def run(self):
        while self.running:
            frame = self.camera_thread.get_latest_frame()
            pred = self.grape_detection_model(frame)
            pred = pred.xyxy[0].cpu().numpy()
            classes = pred[:, 5]
            bunch_indices = classes == 0
            berry_indices = classes == 1
            
            bunch_boxes = pred[bunch_indices][:, :4]
            berry_boxes = pred[berry_indices][:, :4]
            
            # Preprocess removing inputs
            if len(bunch_boxes) > 0:
                selected_bunch_bbox = bunch_boxes[0]
                
                cutting_pred_images = [self.create_cutting_input(berry_box, selected_bunch_bbox, frame.copy(), idx) for idx, berry_box in enumerate(berry_boxes)]
                batch_cutting_pred_image = torch.stack(cutting_pred_images)
                with torch.no_grad():
                    output_removing_berries = self.removal_path_model(batch_cutting_pred_image)
            
                format_result = {
                    'bunch': bunch_boxes.tolist(),
                    'berry': berry_boxes.tolist(),
                    'remove': berry_boxes[self.get_max_remove_index(output_removing_berries)]
                }
            else:
                format_result = {
                    'bunch': [],
                    'berry': [],
                    'remove': []
                }
            
            
            # print(f"bunch: {len(pred[bunch_indices].tolist())}")
            # print(f"berry: {len(pred[berry_indices].tolist())}")
            
            with self.prediction_lock:
                self.predictions.clear()
                self.predictions.update(format_result)
        
            # time.sleep(5)
            
            
    def get_latest_prediction(self):
        return self.predictions
        
    def stop(self):
        self.running = False