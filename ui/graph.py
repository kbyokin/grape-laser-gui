import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QColor, QPalette
import PySide6.QtCharts as QtCharts

class SplineChart(QWidget):
    def __init__(self, chart_color="blue"):
        super().__init__()
        layout = QVBoxLayout(self)
        self.chart_view = QtCharts.QChartView(self)
        layout.addWidget(self.chart_view)
        
        # Interval to update chart
        self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_plot)
        self.update_interval = 1000 # ms
        
        self.x_data = []
        self.y_data = []
        self.max_display_points = 50
        
        # create chart
        self.chart = QtCharts.QChart()
        self.series = QtCharts.QSplineSeries()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        
        # Set the line color
        pen = self.series.pen()
        pen.setColor(QColor(chart_color))  # Change the color here
        self.series.setPen(pen)
        
        self.chart_view.setChart(self.chart)
        
        self.timer.start(self.update_interval)

    def update_plot(self):
        print('plot')
        # Generate random data
        self.x_data.append(len(self.x_data))
        self.y_data.append(random.uniform(0, 300))

        # Limit data points to show only the latest ones
        max_display_points = 50
        if len(self.x_data) > max_display_points:
            self.x_data.clear()
            self.y_data.clear()
            # self.x_data = self.x_data[-max_display_points:]
            # self.y_data = self.y_data[-max_display_points:]

        # Clear and update the series
        self.series.clear()
        for x, y in zip(self.x_data, self.y_data):
            self.series.append(x, y)

        # Notify the chart that the data has changed
        self.chart_view.chart().axisX().setRange(0, len(self.x_data))
        self.chart_view.chart().axisY().setRange(-300, 300)
        self.chart_view.update()
    
    def update_values(self, data):
        self.x_data.append(len(self.x_data))
        self.y_data.append(data)
        # Limit data points to show only the latest ones
        max_display_points = 200
        if len(self.x_data) > max_display_points:
            self.x_data.clear()
            self.y_data.clear()
            # self.x_data = self.x_data[-max_display_points:]
            # self.y_data = self.y_data[-max_display_points:]

        # Clear and update the series
        self.series.clear()
        for x, y in zip(self.x_data, self.y_data):
            self.series.append(x, y)

        # Notify the chart that the data has changed
        self.chart_view.chart().axisX().setRange(0, len(self.x_data))
        self.chart_view.chart().axisY().setRange(-300, 300)
        self.chart_view.update()
        
        
    def clear_data(self):
        self.x_data.clear()
        self.y_data.clear()