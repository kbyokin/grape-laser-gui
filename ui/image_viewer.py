import os
from pathlib import Path
import time
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, QDateTime
import pygame
import cv2

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
        
        # self.remove_timer = QTimer(self)
        # self.remove_timer.timeout.connect(self.update_remove_xyxy)
        # self.remove_timer.start(20000)
        
        self.move_motor = QTimer(self)
        self.move_motor.timeout.connect(self.update_motors)
        self.move_motor.start(500)
        
        self.current = time.time()
        
        self.current_frame = 100
        
        self.remove_xyxy_ = None
        self.x_prime = 0
        self.y_prime = 0
        
        self.removing_history = []
        
        self.dis_x, self.dis_y = 0, 0
        
        self.AZ = 50
        self.ALT = 80
        self.laser_signal = 1
        # send data to API when initilize class
        self.control_motors.send_angles_api([self.AZ, self.ALT], self.laser_signal)
        
        self.mp3_file_path = "/Users/kb/Developer/laser_control_gui/mp3/cutberry.mp3"
        
        self.save_video()
        
    def save_video(self):
        self.save_path = f"./experiments/{self.get_datetime()}"
        os.mkdir(self.save_path)
        save_at = Path(self.save_path)
        save_at.mkdir(parents=True, exist_ok=True)
        print(f"save at: {self.save_path}")
        
    def get_datetime(self):
        current_datetime = QDateTime.currentDateTime()                
        date_formatted =current_datetime.toString("yyyy-MM-dd HH:mm:ss")
        return date_formatted
        
    def update_image(self):
        frame = self.camera_thread.get_latest_frame()
        if frame is not None:
            draw_image = frame.copy()
            w, h, ch = draw_image.shape
            image_center = [(h // 2), (w // 2)]
            cv2.circle(draw_image, (int(h // 2), int(w // 2)), 10, (0, 0, 255), 2)
            cv2.putText(draw_image, self.get_datetime(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                        
            with self.prediction_lock:
                if self.predictions:
                    # print(self.predictions)
                    if len(self.predictions['bunch']) > 0:
                        """
                        Draw rectangle on Grape bunch
                        """
                        bunch_xyxy = self.predictions["bunch"][:4]
                        bunch_x1, bunch_y1, bunch_x2, bunch_y2 = map(int, bunch_xyxy)
                        cv2.rectangle(draw_image, (bunch_x1, bunch_y1), (bunch_x2, bunch_y2), (0, 255, 255), 2)
                        
                        # initial point
                        if self.remove_xyxy_ is None:
                            if len(self.predictions['remove']) > 0:
                                print('initiate points')
                                self.remove_xyxy_ = self.predictions["remove"][:4]      # for breaking the loop
                                remove_xyxy = self.predictions["remove"][:4]
                                removing_x1, removing_y1, removing_x2, removing_y2 = map(int, remove_xyxy)
                                removing_center = (int(removing_x1+removing_x2) // 2, int(removing_y1+removing_y2) // 2)
                                
                                # x_coor, y_coor = removing_center[0], removing_center[1]
                                self.x_prime = (removing_center[0] - bunch_x1) / (bunch_x2 - bunch_x1)
                                self.y_prime = (removing_center[1] - bunch_y1) / (bunch_y2 - bunch_y1)
                                x_coor = int(((bunch_x2 - bunch_x1) * self.x_prime) + bunch_x1)
                                y_coor = int(((bunch_y2 - bunch_y1) * self.y_prime) + bunch_y1)
                                
                                self.removing_history.append([x_coor, y_coor])
                                
                                print(f'initiate: {bunch_xyxy, remove_xyxy}')
                                
                                # cv2.rectangle(draw_image, (remove_xyxy[0], remove_xyxy[1]), (remove_xyxy[2], remove_xyxy[3]), (0, 255, 255), 2)
                                                                            
                        # draw removing berry with normalize points
                        if self.remove_xyxy_ is not None:
                            remove_xyxy = self.predictions["remove"]
                            removing_x1, removing_y1, removing_x2, removing_y2 = map(int, remove_xyxy)
                            removing_center = (int(removing_x1+removing_x2) // 2, int(removing_y1+removing_y2) // 2)
                            
                            # x_coor, y_coor = removing_center[0], removing_center[1]
                            
                            x_coor = int(((bunch_x2 - bunch_x1) * self.x_prime) + bunch_x1)
                            y_coor = int(((bunch_y2 - bunch_y1) * self.y_prime) + bunch_y1)
                            
                            self.removing_history.append([x_coor, y_coor])
                            
                            self.dis_x, self.dis_y = image_center[0] - x_coor, image_center[1] - y_coor
                                
                            # self.AZ, self.ALT = self.control_motors.angles_cal(self.AZ, self.ALT, (self.dis_x, self.dis_y))
                            # print(f'AZ: {self.AZ}, ALT: {self.ALT}')
                            # self.control_motors.send_angles_api([self.AZ, self.ALT])
                            
                            # print(f"xyxy_: {self.remove_xyxy_}")
                            # print(f'bunch xyxy: {bunch_xyxy}')
                            # print(f"x y coor: {x_coor, y_coor}")
                            
                            # cv2.rectangle(draw_image, (removing_x1, removing_y1), (removing_x2, removing_y2), (0, 255, 255), 2)
                            
                        cv2.circle(draw_image, (x_coor, y_coor), 2, (0, 0, 255), -1)
                        
                        if len(self.removing_history) > 2:
                            for indx in range(len(self.removing_history)):
                                if indx + 1 < len(self.removing_history):
                                    cv2.line(draw_image, (self.removing_history[indx][0], self.removing_history[indx][1]), (self.removing_history[indx + 1][0], self.removing_history[indx + 1][1]), (255, 0, 0))
                        
                        
                        if -10 <= self.dis_x <= 10 and -10 <= self.dis_y <= 10:
                            self.laser_signal = 1
                            self.play_track(self.mp3_file_path)
                            self.update_remove_xyxy()
                            
                        self.image_title.setText(f'dis_x, dis_y: {self.dis_x, self.dis_y}')

                        
                        
            rgb_image = cv2.cvtColor(draw_image, cv2.COLOR_BGR2RGB)
            # cv2.imwrite(f'{self.save_path}/{self.current_frame}.jpg', rgb_image[:, :, ::-1])
            self.current_frame += 1
            w, h, ch = rgb_image.shape
            bytes_per_line = ch * h
            qt_image = QImage(rgb_image.data, h, w, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)        # Scale the pixmap to fit the QLabel size
                    
        else:
            print('counld not retreive frame')
    
    def normalize_bunch(self, bunch_xyxy, remove_xyxy, remove_center):
        min_x, min_y, max_x, max_y = map(int, bunch_xyxy)
        
        x_prime = (remove_center[0] - min_x) / (max_x - min_x)
        y_prime = (remove_center[1] - min_y) / (max_y - min_y)
        
        x_coor = int(((max_x - min_x) * x_prime) + min_x)
        y_coor = int(((max_y - min_y) * y_prime) + min_y)
        
        return x_coor, y_coor
            
    def update_remove_xyxy(self):
        if self.predictions["remove"] is not None:
            print('update remove xyxy')
            bunch_x1, bunch_y1, bunch_x2, bunch_y2 = map(int, self.predictions['bunch'][:4])
            remove_xyxy = self.predictions["remove"][:4]
            removing_x1, removing_y1, removing_x2, removing_y2 = map(int, remove_xyxy)
            removing_center = (int(removing_x1+removing_x2) // 2, int(removing_y1+removing_y2) // 2)
            self.x_prime = (removing_center[0] - bunch_x1) / (bunch_x2 - bunch_x1)
            self.y_prime = (removing_center[1] - bunch_y1) / (bunch_y2 - bunch_y1)
            
            self.removing_history.clear()
            self.remove_xyxy_ = self.predictions["remove"]
            self.laser_signal = 0
            
    def update_motors(self):
        self.AZ, self.ALT = self.control_motors.angles_cal(self.AZ, self.ALT, (self.dis_x, self.dis_y))
        print(f'AZ: {self.AZ}, ALT: {self.ALT}')
        self.control_motors.send_angles_api([self.AZ, self.ALT], self.laser_signal)
        
    def play_track(self, file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()