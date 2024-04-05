import time
import socket
from threading import Thread
from PySide6.QtCore import Qt, QTimer

class ControlMotor(Thread):
    def __init__(self, camera_thread, predictions, prediction_lock):
        super().__init__()
        self.camera_thread = camera_thread
        self.predictions = predictions
        self.prediction_lock = prediction_lock
        
        self.AZ = 50
        self.ALT = 80
        
        
        self.server_url = '172.23.161.159'
        
        self.running = True
        
        self.current = time.time()
        
        # self.send_angles_api()
        
    # def run(self):
    #     while self.running:
    #         frame = self.camera_thread.get_latest_frame()
    #         if frame is not None:
    #             frame_w, frame_h, _ = frame.shape
    #             image_center = [(frame_h // 2), (frame_w // 2)]
    #             with self.prediction_lock:
    #                 if self.predictions:
    #                     if len(self.predictions["bunch"]):
    #                         # cal distance
    #                         removing_pred = self.predictions["bunch"][0]
    #                         # removing_pred = self.predictions["remove"]
    #                         x1, y1, x2, y2 = map(int, removing_pred)
    #                         removing_center = (int(x1+x2) // 2, int(y1+y2) // 2)
    #                         dis_x, dis_y = image_center[0] - removing_center[0], image_center[1] -  removing_center[1]
                            
                            
                            
    #                         self.prev = time.time()
    #                         if self.current - self.prev <= -4:
    #                             angles = self.angles_cal((dis_x, dis_y))
    #                             self.AZ, self.ALT = angles
    #                             print(dis_x)
    #                             print(angles)
    #                             # print(self.current - self.prev)
    #                             # self.info_label.append(f"{self.get_datetime_formatted()} -- INFO -- No grape detected")
    #                             self.current = time.time()
    #                             self.send_angles_api()
    
    # def angles_cal(self, distance):
    #     dis_x, dis_y = distance
    #     AZ, ALT = self.AZ, self.ALT
    #     min_angle, max_angle = 0, 120
        
    #     if dis_x > 5:
    #         if dis_x < 50:
    #             AZ = max(min(AZ + 1, max_angle), min_angle)
    #         # elif dis_x < 50:
    #         #     AZ = max(min(AZ - 1, max_angle), min_angle)
    #         else:
    #             AZ = max(min(AZ + 5, max_angle), min_angle)
    #     elif dis_x < -5:
    #         if dis_x > -50:
    #             AZ = max(min(AZ - 1, max_angle), min_angle)
    #         else:
    #             AZ = max(min(AZ - 5, max_angle), min_angle)
    #     else:
    #         # print('should not update AZ')
    #         pass
                
    #     if dis_y > 5:
    #         if dis_y < 50:
    #             ALT = max(min(ALT - 1, max_angle), min_angle)
    #         else:
    #             ALT = max(min(ALT - 5, max_angle), min_angle)
    #     elif dis_y < -5:
    #         if dis_y > -50:
    #             ALT = max(min(ALT + 1, max_angle), min_angle)
    #         else:
    #             ALT = max(min(ALT + 5, max_angle), min_angle)
    #     else:
    #         # print('should not update AZ')
    #         pass
        
    #     # print(f'calculated angles {AZ, ALT}')
    #     return AZ, ALT
    
    # def send_angles_api(self):
    #     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_socket.connect((self.server_url, 12345))
    #     data_to_send = f"{self.AZ},{self.ALT}"
    #     client_socket.send(data_to_send.encode())
    #     client_socket.close()
        
        
    def angles_cal(self, AZ, ALT, distance):
        dis_x, dis_y = distance
        AZ, ALT = int(AZ), int(ALT)
        min_angle, max_angle = 0, 120
        
        if dis_x > 10:
            if dis_x < 50:
                AZ = max(min(AZ + 2, max_angle), min_angle)
            # elif dis_x < 50:
            #     AZ = max(min(AZ - 1, max_angle), min_angle)
            else:
                AZ = max(min(AZ + 1, max_angle), min_angle)
        elif dis_x < -10:
            if dis_x > -50:
                AZ = max(min(AZ - 2, max_angle), min_angle)
            else:
                AZ = max(min(AZ - 1, max_angle), min_angle)
        else:
            # print('should not update AZ')
            pass
                
        if dis_y > 10:
            if dis_y < 50:
                ALT = max(min(ALT - 2, max_angle), min_angle)
            else:
                ALT = max(min(ALT - 1, max_angle), min_angle)
        elif dis_y < -10:
            if dis_y > -50:
                ALT = max(min(ALT + 2, max_angle), min_angle)
            else:
                ALT = max(min(ALT + 1, max_angle), min_angle)
        else:
            # print('should not update AZ')
            pass
        
        # print(f'calculated angles {AZ, ALT}')
        return AZ, ALT
    
    def send_angles_api(self, angles, laser_signal):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_url, 12345))
        data_to_send = f"{angles[0]},{angles[1]},{laser_signal}"
        client_socket.send(data_to_send.encode())
        client_socket.close()
        
    def stop(self):
        self.running = False