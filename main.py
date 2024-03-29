import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from ui.image_viewer import ImageViewer

from thread.camera_thread import CameraThread

def main():
    camera_thread = CameraThread()
    camera_thread.start()
    
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Laser Controller GUI")
    
    screen_size = QApplication.primaryScreen().size()
    screen_w, screen_h = screen_size.width(), screen_size.height()
    main_window.resize(int(screen_w * .8), int(screen_h * .8))
    
    image_viewer = ImageViewer(camera_thread)
    main_window.setCentralWidget(image_viewer)
    main_window.show()
    ret = app.exec()
    camera_thread.stop()
    camera_thread.join()
    sys.exit(ret)
    
if __name__ == "__main__":
    main()