import pyqtgraph as pg
from PySide6 import QtCore


class Main_Graph(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None, limit=60):
        super().__init__(parent=parent, show=True)

        self.parent = parent
        self.limit = limit
        self.setBackground('w')

        self.plotting_control = {'TEMPERATURE':False}

        self.time_data = []

        self.thermocouple_1_data = []
               
    def plot_data(self):
        if self.plotting_control['TEMPERATURE']:
            self.thermocouple_1_plotItem.setData(self.time_data, self.thermocouple_1_data)

    def add_temperature(self):
        self.clear()

        for key in self.plotting_control.keys():
            self.plotting_control[key] = False
        
        self.plotting_control['TEMPERATURE'] = True

        self.thermocouple_1_fig = self.addPlot(0, 0, 1, 1, title='Themocouple 1')
        self.thermocouple_1_fig.showGrid(x=True, y=True)
        self.thermocouple_1_fig.setLabels(left='temp., Celcius', bottom='Time, s')
        

        self.thermocouple_1_plotItem = self.thermocouple_1_fig.plot([],
                                                                [],
                                                                pen=pg.mkPen(color=(130, 130, 255),
                                                                         width=2,
                                                                         style=QtCore.Qt.SolidLine),
                                                                symbolBrush=(130, 130, 255),
                                                                symbolSize=7,
                                                                symbol='o')