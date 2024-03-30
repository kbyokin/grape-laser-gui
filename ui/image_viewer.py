import time
from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QApplication, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer, QDateTime, QSize, Slot

import cv2
from matplotlib.mlab import angle_spectrum

class ImageViewer(QWidget):
    def __init__(self, camera_thread, predictions, prediction_lock, angles, angle_lock, control_motor):
        super().__init__()
        self.camera_thread = camera_thread
        self.predictions = predictions
        self.prediction_lock = prediction_lock
        self.angles = angles
        self.angle_lock = angle_lock
        self.control_motors = control_motor
        layout = QVBoxLayout(self)
        # self.setLayout(layout)
        
        self.image_label = QLabel()
        self.image_title = QLabel("test")
        
        layout.addWidget(self.image_label)
        layout.addWidget(self.image_title)
        
        # Get screen size
        timer = QTimer(self)
        timer.timeout.connect(self.update_image)
        timer.start(30)     # update image every 30ms
        
        self.current = time.time()
        
    def update_image(self):
        frame = self.camera_thread.get_latest_frame()
        if frame is not None:
            draw_image = frame.copy()
            w, h, ch = draw_image.shape
            image_center = [(h // 2), (w // 2)]
            cv2.circle(draw_image, (int(h // 2), int(w // 2)), 10, (0, 0, 255), 2)
            
            
            with self.prediction_lock:
                if self.predictions:
                    # print(self.predictions)
                    if len(self.predictions['bunch']) > 0:
                        remove_xyxy = self.predictions["bunch"][0]
                        # remove_xyxy = self.predictions["remove"]
                        x1, y1, x2, y2 = map(int, remove_xyxy)
                        removing_center = (int(x1+x2) // 2, int(y1+y2) // 2)
                        cv2.circle(draw_image, removing_center, 2, (0, 0, 255), -1)
                        cv2.rectangle(draw_image, (x1, y1), (x2, y2), (0, 255, 255), 2)
                        
                        self.prev = time.time()
                        if self.current - self.prev <= -1:
                            dis_x, dis_y = image_center[0] - removing_center[0], image_center[1] -  removing_center[1]
                        
                            with self.angle_lock:
                                if len(self.angles) > 0:
                                    print(f'self angles: {self.angles}')
                                    # calculate angle
                                    angles = self.control_motors.angles_cal(self.angles[0], self.angles[1], (dis_x, dis_y))
                                    self.angles = [angles[0], angles[1]]
                                    self.control_motors.send_angles_api(self.angles)
                                else:
                                    print(self.angles)
                                    self.angles = ['50', '80']
                                    self.control_motors.send_angles_api(self.angles)
                    
            rgb_image = cv2.cvtColor(draw_image, cv2.COLOR_BGR2RGB)
            w, h, ch = rgb_image.shape
            bytes_per_line = ch * h
            qt_image = QImage(rgb_image.data, h, w, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)        # Scale the pixmap to fit the QLabel size
                    
        else:
            print('counld not retreive frame')