import pyqtgraph as pg
from PySide6 import QtCore


class Main_Graph(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None, limit=3600):
        super().__init__(parent=parent, show=True)

        self.parent = parent
        self.limit = limit
        self.setBackground('w')

        self.plotting_control = {
                         'op_temp_1': False,
                         'op_temp_2': False,
                         'BME_temp': False,
                         'BME_press': False,
                         'BME_humid': False,
                         'MICS5524': False,
                         'Resistance': False,
                         'VOVG': False
                         }

        self.time_data = []

        self.thermocouple_1_data = []

        self.bme_temp_data = []
        self.bme_press_data = []
        self.bme_humid_data = []

        self.mics_data = []

        self.VOVG_furnace_data = []
        self.VOVG_sample_flow_data = []

        self.resistance_data = []
               
    def plot_data(self):
        if self.plotting_control['op_temp_1']:
            self.thermocouple_1_plotItem.setData(self.time_data, self.thermocouple_1_data)
        
        elif self.plotting_control['BME_temp']:
            self.bme_temp_plotItem.setData(self.time_data, self.bme_temp_data)
        
        elif self.plotting_control['BME_press']:
            self.bme_press_plotItem.setData(self.time_data, self.bme_press_data)
        
        elif self.plotting_control['BME_humid']:
            self.bme_humid_plotItem.setData(self.time_data, self.bme_humid_data)
        
        elif self.plotting_control['MICS5524']:
            self.mics_plotItem.setData(self.time_data, self.mics_data)
        
        elif self.plotting_control['VOVG']:
            self.VOVG_furnace_plotItem.setData(self.time_data, self.VOVG_furnace_data)
            self.VOVG_sample_flow_plotItem.setData(self.time_data, self.VOVG_sample_flow_data)
        
        elif self.plotting_control['Resistance']:
            self.ch1_plot_item.setData(self.time_data, self.resistance_data)
             
    def add_thermo_1(self):
        self.clear()

        for key in self.plotting_control.keys():
            self.plotting_control[key] = False
        
        self.plotting_control['op_temp_1'] = True

        self.thermocouple_1_fig = self.addPlot(0, 0, 1, 1, title='Thermocouple 1')
        self.thermocouple_1_fig.showGrid(x=True, y=True)
        self.thermocouple_1_fig.setLabels(left='temp., Celsius', bottom='Time, min')
        
        self.thermocouple_1_plotItem = self.thermocouple_1_fig.plot([],
                                                                [],
                                                                pen=pg.mkPen(color=(255, 130, 130),
                                                                         width=1,
                                                                         style=QtCore.Qt.DashLine),
                                                                symbolBrush=(130, 130, 255),
                                                                symbolSize=5,
                                                                symbol='o')

    def add_BME_temp(self):
        self.clear()

        for key in self.plotting_control.keys():
            self.plotting_control[key] = False
        
        self.plotting_control['BME_temp'] = True

        self.bme_temp_fig = self.addPlot(0, 0, 1, 1, title='Flow temperature')
        self.bme_temp_fig.showGrid(x=True, y=True)
        self.bme_temp_fig.setLabels(left='temp., Celsius', bottom='Time, min')
        
        self.bme_temp_plotItem = self.bme_temp_fig.plot([],
                                                        [],
                                                        pen=pg.mkPen(color=(255, 130, 130),
                                                                    width=1,
                                                                    style=QtCore.Qt.DashLine),
                                                            symbolBrush=(130, 130, 255),
                                                            symbolSize=5,
                                                            symbol='o')

    def add_BME_press(self):
        self.clear()

        for key in self.plotting_control.keys():
            self.plotting_control[key] = False
        
        self.plotting_control['BME_press'] = True

        self.bme_press_fig = self.addPlot(0, 0, 1, 1, title='Flow pressure')
        self.bme_press_fig.showGrid(x=True, y=True)
        self.bme_press_fig.setLabels(left='Pressure, kPa', bottom='Time, min')
        
        self.bme_press_plotItem = self.bme_press_fig.plot([],
                                                        [],
                                                        pen=pg.mkPen(color=(130, 255, 130),
                                                                    width=1,
                                                                    style=QtCore.Qt.DashLine),
                                                            symbolBrush=(130, 130, 255),
                                                            symbolSize=5,
                                                           symbol='o')

    def add_BME_humid(self):
        self.clear()

        for key in self.plotting_control.keys():
            self.plotting_control[key] = False
        
        self.plotting_control['BME_humid'] = True

        self.bme_humid_fig = self.addPlot(0, 0, 1, 1, title='Flow Humidity')
        self.bme_humid_fig.showGrid(x=True, y=True)
        self.bme_humid_fig.setLabels(left='Humidity, %', bottom='Time, min')
        
        self.bme_humid_plotItem = self.bme_humid_fig.plot([],
                                                        [],
                                                        pen=pg.mkPen(color=(130, 130, 255),
                                                                    width=1,
                                                                    style=QtCore.Qt.DashLine),
                                                            symbolBrush=(130, 130, 255),
                                                            symbolSize=5,
                                                            symbol='o')

    def add_MICS5524(self):
        self.clear()

        for key in self.plotting_control.keys():
            self.plotting_control[key] = False
        
        self.plotting_control['MICS5524'] = True

        self.mics_fig = self.addPlot(0, 0, 1, 1, title='MICS 5524 Sensor')
        self.mics_fig.showGrid(x=True, y=True)
        self.mics_fig.setLabels(left='Signal, a.u.', bottom='Time, min')
        
        self.mics_plotItem = self.mics_fig.plot([],
                                                [],
                                                pen=pg.mkPen(color=(0, 0, 0),
                                                            width=1,
                                                            style=QtCore.Qt.DashLine),
                                                symbolBrush=(130, 130, 255),
                                                symbolSize=7,
                                                symbol='o')  

    def add_VOVG(self):
        self.clear()
        for key in self.plotting_control.keys():
            self.plotting_control[key] = False
        
        self.plotting_control['VOVG'] = True
        
        self.VOVG_furnace_fig = self.addPlot(0, 0, 1, 1, title='OVG Furnace Temperature')
        self.VOVG_furnace_fig.showGrid(x=True, y=True)
        self.VOVG_furnace_fig.setLabels(left='Temperature (C)', bottom='Time, min')

        self.VOVG_sample_flow_fig = self.addPlot(0, 1, 1, 1, title='OVG sample flow')
        self.VOVG_sample_flow_fig.showGrid(x=True, y=True)
        self.VOVG_sample_flow_fig.setLabels(left='Sample flow (sccm)', bottom='Time, min')

        self.VOVG_furnace_plotItem = self.VOVG_furnace_fig.plot([],
                                                          [],
                                                          pen=pg.mkPen(color=(255, 130, 130),
                                                                       width=1,
                                                                       style=QtCore.Qt.DashLine),
                                                          symbolBrush=(
                                                              0, 0, 0),
                                                          symbolSize=5,
                                                          symbol='o')

        self.VOVG_sample_flow_plotItem = self.VOVG_sample_flow_fig.plot([],
                                                          [],
                                                          pen=pg.mkPen(color=(130, 130, 255),
                                                                       width=1,
                                                                       style=QtCore.Qt.DashLine),
                                                          symbolBrush=(
                                                              0, 0, 0),
                                                          symbolSize=5,
                                                          symbol='o')

    def add_resistance(self):
        self.clear()

        for key in self.plotting_control.keys():
            self.plotting_control[key] = False

        self.plotting_control['Resistance'] = True

        self.ch1_plot = self.addPlot(0, 0, 1, 1, title='Channel 1 Resistance')
        self.ch1_plot.showGrid(x=True, y=True)
        self.ch1_plot.setLabels(left='Resistance, kOhm', bottom='Time, min')

        self.ch1_plot_item = self.ch1_plot.plot([],
                                                        [],
                                                         pen=pg.mkPen(color=(0, 0, 0),
                                                                     width=1,
                                                                     style=QtCore.Qt.DashLine),
                                                            symbolBrush=(0, 0, 0),
                                                            symbolSize=5,
                                                            symbol='o')


