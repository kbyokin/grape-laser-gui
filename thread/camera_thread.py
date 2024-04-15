from threading import Lock, Thread
import time
import pyrealsense2.pyrealsense2 as rs
import cv2
import numpy as np

class CameraThread(Thread):
    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.frame_lock = Lock() # Lock thread to self.latest_frame
        self.latest_frame = None
        self.latest_depth_frame = None
        self.running = True
        
        # try:
        #     # Initiate Realsense settings
        #     self.pipeline = rs.pipeline()
        #     self.config = rs.config()
            
        #     self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        #     self.config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
        #     self.pipeline.start(self.config)
            
        #     align_to = rs.stream.color
        #     self.align = rs.align(align_to)
            
        #     self.use_realsense = True
        # except Exception as e:
        #     print(f"Failed to start RealSense pipeline: {e}")
        #     self.use_realsense = False
        
        self.use_realsense = False
        
    def run(self):
        if self.use_realsense:
            try:
                while self.running:
                    # try:
                    #     frames = self.pipeline.wait_for_frames(5000)
                    # except Exception as e:
                    #     print(f'Timeout or error waiting for frames: {e}')
                    #     continue
                    
                    frames = self.pipeline.wait_for_frames(5000)
                    
                    color_frame = frames.get_color_frame()
                    depth_frame = frames.get_depth_frame()
                    
                    # ! Could not retrive any frames --> Further investigation needed
                    # aligned_frames = self.align.process(frames)
                    # time.sleep(0.03)
                    # depth_frame = aligned_frames.get_depth_frame()
                    # color_frame = aligned_frames.get_color_frame()
                    
                    if not color_frame or not depth_frame:
                        continue
                    
                    # Convert images to numpy arrays --> and convert BGR to RGB
                    frame = np.asanyarray(color_frame.get_data())[:, :, ::-1]
                    depth_frame = np.asanyarray(depth_frame.get_data())
                    
                    with self.frame_lock:
                        self.latest_frame = frame
                        self.latest_depth_frame = depth_frame
            finally:
                self.pipeline.stop()
        else:
            cap = cv2.VideoCapture(self.camera_id)
            if not cap.isOpened():
                print("Error: Unable to open camera.")
                return
            try:
                while self.running:
                    ret, frame = cap.read()
                    if ret:
                        with self.frame_lock:
                            self.latest_frame = frame
                    else:
                        print("Error: Unable to read frame from camera.")
                        break
            finally:
                cap.release()
    
    def get_latest_frame(self):
        with self.frame_lock:
            return self.latest_frame
        
    def get_latest_depth_frame(self):
        with self.frame_lock:
            return self.latest_depth_frame
        
    def stop(self):
        self.running = False
        self.join()