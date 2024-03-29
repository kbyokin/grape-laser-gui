from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QApplication, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer, QDateTime, QSize, Slot

import cv2

class ImageViewer(QWidget):
    def __init__(self, camera_thread):
        super().__init__()
        self.camera_thread = camera_thread
        
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
        draw_image = frame.copy()
        print(frame.shape)
        if frame is not None:
            rgb_image = cv2.cvtColor(draw_image, cv2.COLOR_BGR2RGB)
            w, h, ch = rgb_image.shape
            bytes_per_line = ch * h
            qt_image = QImage(rgb_image.data, h, w, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)        # Scale the pixmap to fit the QLabel size