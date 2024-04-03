from threading import Lock, Thread
import time
import pyrealsense2.pyrealsense2 as rs
import cv2
import numpy as np

from grape_detection_ import GrapeDetection

camera_id=0
cap = cv2.VideoCapture(camera_id)
grape_model = GrapeDetection()
try:
    while True:
        ret, frame = cap.read()
        if ret:
            print(frame.shape)
            pred = grape_model.predict(frame)
            print(pred)
finally:
    cap.release()