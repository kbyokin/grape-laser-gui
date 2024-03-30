from os import remove
from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QApplication, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer, QDateTime, QSize, Slot

import cv2

class ImageViewer(QWidget):
    def __init__(self, camera_thread, predictions, prediction_lock):
        super().__init__()
        self.camera_thread = camera_thread
        self.predictions = predictions
        self.prediction_lock = prediction_lock
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
        
    def update_image(self):
        frame = self.camera_thread.get_latest_frame()
        if frame is not None:
            draw_image = frame.copy()
            w, h, ch = draw_image.shape
            cv2.circle(draw_image, (int(h // 2), int(w // 2)), 10, (0, 0, 255), 2)
            
            
            with self.prediction_lock:
                if self.predictions:
                    print(self.predictions)
                    remove_xyxy = self.predictions['remove']
                    if len(self.predictions['bunch']) > 0:
                        x1, y1, x2, y2 = map(int, remove_xyxy)
                        cv2.rectangle(draw_image, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    
            rgb_image = cv2.cvtColor(draw_image, cv2.COLOR_BGR2RGB)
            w, h, ch = rgb_image.shape
            bytes_per_line = ch * h
            qt_image = QImage(rgb_image.data, h, w, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)        # Scale the pixmap to fit the QLabel size
                    
        else:
            print('counld not retreive frame')