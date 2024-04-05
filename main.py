from threading import Lock
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout

from thread.control_motors import ControlMotor
from thread.grape_prediction import GrapeDetection
from ui.image_viewer import ImageViewer
from ui.graph import SplineChart

from thread.camera_thread import CameraThread

def main():
    """
    Threads Initialization
    """
    camera_thread = CameraThread()
    camera_thread.start()
    
    prediction_lock = Lock()
    predictions = {}
    
    angle_lock = Lock()
    angles = []
    
    grape_model_path = "../berry_thinning/models/detection/yolov5s_2cls15_best.pt"
    removal_model_path = "../berry_thinning/models/removal/resnet18_bbox_aug_True_ratio1-8_bs-8_lr-0.001_epoch-3000 (1).pth"
    grape_detection = GrapeDetection(camera_thread, predictions, prediction_lock, grape_model_path, removal_model_path)
    grape_detection.start()
    
    control_motor = ControlMotor(camera_thread, predictions, prediction_lock)
    control_motor.start()
    # control_motor = []
    
    """
    GUI
    """
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Laser Controller GUI")
    
    screen_size = QApplication.primaryScreen().size()
    screen_w, screen_h = screen_size.width(), screen_size.height()
    main_window.resize(int(screen_w * .8), int(screen_h * .8))
    
    dx_chart = SplineChart()
    dx_chart.setFixedSize(800, 300)
    dy_chart = SplineChart(chart_color='green')
    dy_chart.setFixedSize(800, 300)
    
    image_viewer = ImageViewer(camera_thread, predictions, prediction_lock, angles, angle_lock, control_motor)
    
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    layout.addWidget(image_viewer)
    
    chart_layout = QHBoxLayout()
    chart_layout.addWidget(dx_chart)
    chart_layout.addWidget(dy_chart)
    
    layout.addLayout(chart_layout)
    
    image_viewer.dx_data.connect(dx_chart.update_values)
    image_viewer.dy_data.connect(dy_chart.update_values)
    
    image_viewer.distance.connect(control_motor.get_distance)
    
    main_window.show()
    ret = app.exec()
    camera_thread.stop()
    camera_thread.join()
    grape_detection.stop()
    grape_detection.join()
    control_motor.stop()
    control_motor.join()
    sys.exit(ret)
    
if __name__ == "__main__":
    main()