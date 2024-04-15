import time
import socket
from threading import Thread

class ControlMotor(Thread):
    def __init__(self):
        super().__init__()
        
        self.AZ = 50
        self.ALT = 80
        
        self.dx, self.dy = None, None
        
        self.server_url = '172.23.161.159'
        
        self.running = True
        
        self.current = time.time()
        
    def run(self):
        while self.running:
            if self.dx and self.dy:
                self.AZ, self.ALT = self.angles_cal(self.AZ, self.ALT, (self.dx, self.dy))
                self.send_angles_api([self.AZ, self.ALT], 1)
                time.sleep(0.5)
        
    def angles_cal(self, AZ, ALT, distance):
        dis_x, dis_y = distance
        AZ, ALT = int(AZ), int(ALT)
        min_angle, max_angle = 0, 120
        
        if dis_x > 10:
            if dis_x < 200:
                if dis_x < 50:
                    AZ = max(min(AZ + 2, max_angle), min_angle)
                else:
                    AZ = max(min(AZ + 4, max_angle), min_angle)
            else:
                AZ = max(min(AZ + 1, max_angle), min_angle)
        elif dis_x < -10:
            if dis_x > -200:
                if dis_x > -50:
                    AZ = max(min(AZ - 2, max_angle), min_angle)
                else:
                    AZ = max(min(AZ - 4, max_angle), min_angle)
            else:
                AZ = max(min(AZ - 1, max_angle), min_angle)
        else:
            # print('should not update AZ')
            pass
                
        if dis_y > 10:
            if dis_y < 200:    
                if dis_y < 50:
                    ALT = max(min(ALT - 2, max_angle), min_angle)
                else:
                    ALT = max(min(ALT - 4, max_angle), min_angle)
            else:
                ALT = max(min(ALT - 1, max_angle), min_angle)
        elif dis_y < -10:
            if dis_y > -200:
                if dis_y > -50:
                    ALT = max(min(ALT + 2, max_angle), min_angle)
                else:
                    ALT = max(min(ALT + 4, max_angle), min_angle)
            else:
                ALT = max(min(ALT + 1, max_angle), min_angle)
        else:
            # print('should not update AZ')
            pass
        
        # print(f'calculated angles {AZ, ALT}')
        return AZ, ALT
    
    def send_angles_api(self, angles: list[int], laser_signal: int) -> None:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_url, 12345))
        data_to_send = f"{angles[0]},{angles[1]},{laser_signal}"
        client_socket.send(data_to_send.encode())
        client_socket.close()
        
    def get_distance(self, data):
        print(f'get distance: {data}')
        self.dx, self.dy = data[0], data[1]
        
    def stop(self):
        self.running = False