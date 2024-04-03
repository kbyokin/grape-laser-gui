import sys
import random
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
import PySide6.QtCharts as QtCharts
from PySide6.QtGui import QColor
from PySide6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-time Plot with PySide6")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and layout for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add a chart view to the layout
        self.chart_view = QtCharts.QChartView()
        layout.addWidget(self.chart_view)

        # Add a button to start and stop updating the plot
        self.button = QPushButton("Start/Stop")
        layout.addWidget(self.button)

        # Connect the button to start/stop updating the plot
        self.button.clicked.connect(self.toggle_update)

        # Initialize timer for updating plot data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.update_interval = 1000  # Update interval in milliseconds

        # Initialize data for plotting
        self.x_data = []
        self.y_data = []

        # Create a chart and series
        self.chart = QtCharts.QChart()
        # self.series = QtCharts.QSplineSeries()
        self.series = QtCharts.QLineSeries()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        
        # Set the line color
        pen = self.series.pen()
        pen.setColor(QColor("blue"))  # Change the color here
        self.series.setPen(pen)

        # Set the chart on the chart view
        self.chart_view.setChart(self.chart)

        # Start the timer
        self.timer.start(self.update_interval)

    def update_plot(self):
        # Generate random data
        self.x_data.append(len(self.x_data))
        self.y_data.append(random.uniform(0, 300))

        # Limit data points to show only the latest ones
        max_display_points = 50
        if len(self.x_data) > max_display_points:
            self.x_data = self.x_data[-max_display_points:]
            self.y_data = self.y_data[-max_display_points:]

        # Clear and update the series
        self.series.clear()
        for x, y in zip(self.x_data, self.y_data):
            self.series.append(x, y)

        # Notify the chart that the data has changed
        self.chart_view.chart().axisX().setRange(0, len(self.x_data))
        self.chart_view.chart().axisY().setRange(min(self.y_data), max(self.y_data))
        self.chart_view.update()

    def toggle_update(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText("Start")
        else:
            self.timer.start(self.update_interval)
            self.button.setText("Stop")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())