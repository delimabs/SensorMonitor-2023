import sys
import datetime
import numpy as np
import pandas as pd
from PySide6 import QtCore
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QSpacerItem, QWidget, QPushButton,
                               QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QCheckBox,
                               QLabel, QSpinBox, QDoubleSpinBox, QDialog, QLineEdit, QFileDialog,
                               QSizePolicy,QDockWidget)

from commands import System_Commands
from main_graph import Main_Graph


class Main_Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = pd.read_csv('configurations.txt', sep=',')
        print(self.config)
        
        self.setGeometry(50, 50, 1200, 600)
        self.setWindowTitle('Sensor Monitor 0.9d')
        self.title_font = QFont('Helvetica', 9)
        self.title_font.setBold(True)

        #This dictionary holds the variables for general control of the data flow
        self.general_control = {'controller_connection': False, \
                                'flow_on': False, 'start_stop_control': False, 'log_on': False}
        
        #NEEDS TO SUBSTITUTE THESE VARIABLES 
        self.controller_connection = False
        self.controller_flow = False
        self.start_stop_control = False
        self.log_running = False
        
        self.period = 1000
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.period)  # in milliseconds

        self.start_main_layout()
        self.start_main_menu()
        self.start_connection_board()
        self.start_op_temp_monitor()
        self.plot_control_menu()
     
    def start_main_menu(self):
        self.main_menu = self.menuBar()
        self.file_menu = self.main_menu.addMenu('File')
        
        self.log_action = self.file_menu.addAction('Log data')
        self.log_action.triggered.connect(self.open_log_dlg)

        self.sequence_menu = self.main_menu.addMenu('Sequence')

        self.settings_menu = self.main_menu.addMenu('Settings')
        self.plot_action = self.settings_menu.addAction('Plot settings')
        self.plot_action.triggered.connect(self.open_plot_settings_dlg)

        self.install_probe_monitor = self.settings_menu.addAction('Install thermocouple')
    
        self.about_action = self.main_menu.addAction('About')
        self.exit_action = self.main_menu.addAction('Exit')
        
        self.exit_action.triggered.connect(sys.exit)

    def start_main_layout(self):
        """
        This function creates the main layout of the GUI. It defines the main graph
        as the central widget and a top layout with buttons and display areas for 
        each parameter being measured. 
        """

        self.setWindowTitle('Thermocouple monitor 0.9d')

        #1 Create central widget and insert a main_graph object in it
        #
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_graph = Main_Graph(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.main_graph)

        #2 Create a dock menu with all widgets inside it
        #
        self.dock_widget = QDockWidget(self)
        self.dock_widget.setWindowTitle('Menu')
        self.dock_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.dock_widget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_widget)

        self.dock_menu = QWidget(self.dock_widget)
        self.dock_widget.setWidget(self.dock_menu)
                
        #2.1 Creating widgets and separating lines
        self.connect_board_widget = QWidget(self.dock_menu)
        self.connect_board_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.line1 = QFrame(self.dock_menu)
        self.line1.setFrameShape(QFrame.Shape.HLine)
        self.line1.setLineWidth(2)

        self.probe_temp_monitor_widget = QWidget(self.dock_menu)

        self.line2 = QFrame(self.dock_menu)
        self.line2.setFrameShape(QFrame.Shape.HLine)
        self.line2.setLineWidth(2)   

        self.commands_widget = QWidget(self.dock_menu)

        self.dock_layout =  QVBoxLayout(self.dock_menu)
        self.dock_layout.addWidget(self.connect_board_widget, alignment=QtCore.Qt.Alignment(QtCore.Qt.AlignCenter))
        self.dock_layout.addWidget(self.line1)
        self.dock_layout.addWidget(self.probe_temp_monitor_widget)
        self.dock_layout.addWidget(self.line2)
        self.dock_layout.addWidget(self.commands_widget)
        self.spacer_1 = QSpacerItem(0,0, hData = QSizePolicy.Minimum, vData = QSizePolicy.Expanding)
        self.dock_layout.addSpacerItem(self.spacer_1)
              
    def test(self):
        print('dunha')
        print(self.dockOptions)

    def start_connection_board(self):       
        self.system_conn_btn = QPushButton(self.connect_board_widget)
        self.system_conn_btn.setText('Connect')
        #self.system_conn_btn.clicked.connect(self.system_connection)
        
        self.controller_status_lbl = QLabel(self.connect_board_widget)
        self.controller_status_lbl.setText('OFF')
        self.controller_status_lbl.setFixedSize(60, 20)
        
        self.controller_status_lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.controller_status_lbl.setStyleSheet("background-color: rgb(250, 80, 80);")

        # Layout
        self.connection_board_layout = QVBoxLayout(self.connect_board_widget)
        self.connection_board_layout.addWidget(self.system_conn_btn)
        self.connection_board_layout.addWidget(self.controller_status_lbl, alignment=QtCore.Qt.Alignment(QtCore.Qt.AlignCenter))

    def start_op_temp_monitor(self):
        self.temp_cell_1_lbl = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_1_lbl.setText('Thermocouple 1:')
        self.temp_cell_1_lbl.setAlignment(QtCore.Qt.AlignHCenter)

        self.temp_cell_1_reading = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_1_reading.setLineWidth(1)
        self.temp_cell_1_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.temp_cell_1_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.temp_cell_1_reading.setFixedWidth(60)
        self.temp_cell_1_reading.setText('000.00')

        self.temp_cell_2_lbl = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_2_lbl.setText('Thermocouple 2:')
        self.temp_cell_2_lbl.setAlignment(QtCore.Qt.AlignHCenter)

        self.ing = QLabel(self.probe_temp_monitor_widget)
        self.ing.setLineWidth(1)
        self.ing.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.ing.setAlignment(QtCore.Qt.AlignHCenter)
        self.ing.setFixedWidth(60)
        self.ing.setText('000.00')

        self.probe_temp_show_btn = QPushButton(self.probe_temp_monitor_widget)
        self.probe_temp_show_btn.setText('Show')
        self.probe_temp_show_btn.clicked.connect(self.main_graph.add_temperature)

        self.probe_temp_layout = QGridLayout(self.probe_temp_monitor_widget)
        self.probe_temp_layout.addWidget(self.temp_cell_1_lbl, 1, 0, 1, 1)
        self.probe_temp_layout.addWidget(self.temp_cell_1_reading, 1, 1, 1, 1)
        self.probe_temp_layout.addWidget(self.temp_cell_2_lbl, 2, 0, 1, 1)
        self.probe_temp_layout.addWidget(self.ing, 2, 1, 1, 1)
        self.probe_temp_layout.addItem(QSpacerItem(1, 20), 3, 0, 1, 2)
        self.probe_temp_layout.addWidget(
            self.probe_temp_show_btn, 4, 0, 1, 2, QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

    def plot_control_menu(self):
        # CREATING commands Buttons
        # -------------------------

        self.start_stop_btn = QPushButton(self.commands_widget)
        self.start_stop_btn.setText('Start')
        self.start_stop_btn.setDisabled(True)
        # self.start_stop_btn.clicked.connect(self.start_stop_data)

        self.restart_btn = QPushButton(self.commands_widget)
        self.restart_btn.setText('Restart')
        # self.restart_btn.clicked.connect(self.restart_plot)

        self.clear_btn = QPushButton(self.commands_widget)
        self.clear_btn.setText('Clear')
        # self.clear_btn.clicked.connect(self.clear_plot)

        self.commands_menu_layout = QVBoxLayout(self.commands_widget)
        self.commands_menu_layout.addWidget(self.start_stop_btn)
        self.commands_menu_layout.addWidget(self.restart_btn)
        self.commands_menu_layout.addWidget(self.clear_btn)

    def start_connection_board(self):       
        self.system_conn_btn = QPushButton(self.connect_board_widget)
        self.system_conn_btn.setText('Connect')
        self.system_conn_btn.clicked.connect(self.system_connection)
        
        self.controller_status_lbl = QLabel(self.connect_board_widget)
        self.controller_status_lbl.setText('OFF')
        self.controller_status_lbl.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.controller_status_lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.controller_status_lbl.setStyleSheet("background-color: rgb(250, 80, 80);")

        # Layout
        self.connection_board_layout = QVBoxLayout(self.connect_board_widget)
        self.connection_board_layout.addWidget(self.system_conn_btn)
        self.connection_board_layout.addWidget(self.controller_status_lbl)

    def start_op_temp_monitor(self):
        self.temp_cell_1_lbl = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_1_lbl.setText('Thermocouple 1:')
        self.temp_cell_1_lbl.setAlignment(QtCore.Qt.AlignHCenter)

        self.temp_cell_1_reading = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_1_reading.setLineWidth(1)
        self.temp_cell_1_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.temp_cell_1_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.temp_cell_1_reading.setFixedWidth(60)
        self.temp_cell_1_reading.setText('000.00')

        self.temp_cell_2_lbl = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_2_lbl.setText('Thermocouple 2:')
        self.temp_cell_2_lbl.setAlignment(QtCore.Qt.AlignHCenter)

        self.ing = QLabel(self.probe_temp_monitor_widget)
        self.ing.setLineWidth(1)
        self.ing.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.ing.setAlignment(QtCore.Qt.AlignHCenter)
        self.ing.setFixedWidth(60)
        self.ing.setText('000.00')

        self.probe_temp_show_btn = QPushButton(self.probe_temp_monitor_widget)
        self.probe_temp_show_btn.setText('Show')
        self.probe_temp_show_btn.clicked.connect(self.main_graph.add_temperature)

        self.probe_temp_layout = QGridLayout(self.probe_temp_monitor_widget)
        self.probe_temp_layout.addWidget(self.temp_cell_1_lbl, 1, 0, 1, 1)
        self.probe_temp_layout.addWidget(self.temp_cell_1_reading, 1, 1, 1, 1)
        self.probe_temp_layout.addWidget(self.temp_cell_2_lbl, 2, 0, 1, 1)
        self.probe_temp_layout.addWidget(self.ing, 2, 1, 1, 1)
        self.probe_temp_layout.addItem(QSpacerItem(1, 20), 3, 0, 1, 2)
        self.probe_temp_layout.addWidget(
            self.probe_temp_show_btn, 4, 0, 1, 2, QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

    def plot_control_menu(self):
        # CREATING commands Buttons
        # -------------------------

        self.start_stop_btn = QPushButton(self.commands_widget)
        self.start_stop_btn.setText('Start')
        self.start_stop_btn.setDisabled(True)
        self.start_stop_btn.clicked.connect(self.start_stop_data)

        self.restart_btn = QPushButton(self.commands_widget)
        self.restart_btn.setText('Restart')
        self.restart_btn.clicked.connect(self.restart_plot)

        self.clear_btn = QPushButton(self.commands_widget)
        self.clear_btn.setText('Clear')
        self.clear_btn.clicked.connect(self.clear_plot)

        self.commands_menu_layout = QVBoxLayout(self.commands_widget)
        self.commands_menu_layout.addWidget(self.start_stop_btn)
        self.commands_menu_layout.addWidget(self.restart_btn)
        self.commands_menu_layout.addWidget(self.clear_btn)
   
    def open_log_dlg(self):
        self.log_dlg = QDialog()
        self.log_dlg.resize(400, 200)
        self.log_dlg.setWindowTitle('Start data logging')

        self.main_log_layout = QGridLayout(self.log_dlg)

        self.allSelected = False
        
        self.log_lbl_1 = QLabel(self.log_dlg)
        self.log_lbl_1.setText('Choose the variables to LOG:')

        # first column

        self.temperature_check = QCheckBox('Flow Temperature', self.log_dlg)
        self.pressure_check = QCheckBox('Flow Pressure', self.log_dlg)
        self.humidity_check = QCheckBox('Flow Humidity', self.log_dlg)

        # second column
        self.ch1_check = QCheckBox('ch1 Resistance', self.log_dlg)
        self.ch2_check = QCheckBox('ch2 Resistance', self.log_dlg)
        self.ch3_check = QCheckBox('ch3 Resistance', self.log_dlg)
        self.ch4_check = QCheckBox('ch4 Resistance', self.log_dlg)
        
        # third column
        self.OVG4_temperature_check = QCheckBox('OVG4 Temperature (C)', self.log_dlg)
        self.OVG4_sample_flow_check = QCheckBox('OVG4 Sample Flow (sccm)', self.log_dlg)

        # fourth column
      
        self.MQ2_check = QCheckBox('MQ-2', self.log_dlg)
        self.MQ3_check = QCheckBox('MQ-3', self.log_dlg)
        self.MICS5524_check = QCheckBox('MICS5524', self.log_dlg)
        self.MICS6814_CO_check = QCheckBox('MICS6814-CO', self.log_dlg)
        self.MICS6814_NH3_check = QCheckBox('MICS6814-NH3', self.log_dlg)
        self.MICS6814_NO2_check = QCheckBox('MICS6814-NO2', self.log_dlg)
        
        self.MQ2_check.setDisabled(True)
        self.MQ3_check.setDisabled(True)
        self.MICS5524_check.setDisabled(True)
        self.MICS6814_CO_check.setDisabled(True)
        self.MICS6814_NH3_check.setDisabled(True)
        self.MICS6814_NO2_check.setDisabled(True)

        if self.analyte_sensor_control['MQ-2']:
            self.MQ2_check.setDisabled(False)

        elif self.analyte_sensor_control['MQ-3']:
            self.MQ3_check.setDisabled(False)
        
        elif self.analyte_sensor_control['MICS5524']:
            self.MICS5524_check.setDisabled(False)

        elif self.analyte_sensor_control['MICS6814-CO']:
            self.MICS6814_CO_check.setDisabled(False)

        elif self.analyte_sensor_control['MICS6814-NH3']:
            self.MICS6814_NH3_check.setDisabled(False)

        elif self.analyte_sensor_control['MICS6814-NO2']:
            self.MICS6814_NO2_check.setDisabled(False)

        # Line 1 under columns
        self.user_lbl = QLabel(self.log_dlg)
        self.user_lbl.setText('User: ')
        self.user_input = QLineEdit(self.log_dlg)
       
        # line 2
        self.permeation_tube_lbl = QLabel(self.log_dlg)
        self.permeation_tube_lbl.setText('Perm. tube info:')
        self.permeation_tube_input = QLineEdit(self.log_dlg)

        # line 3 buttons
        self.btn_log_widget = QWidget(self.log_dlg)

        self.select_all_btn = QPushButton(self.btn_log_widget)
        self.select_all_btn.setText('Select all')
        #  self.select_all_btn.clicked.connect(self.selectAllLogDlg)
       
        self.start_log_btn = QPushButton(self.btn_log_widget)
        self.start_log_btn.setText('Start')
        self.start_log_btn.clicked.connect(self.create_log_file)

        self.close_log_btn = QPushButton(self.btn_log_widget)
        self.close_log_btn.setText('Close')
        self.close_log_btn.clicked.connect(self.log_dlg.reject)
        
        self.btn_log_widget_layout = QHBoxLayout(self.btn_log_widget)
        self.btn_log_widget_layout.addWidget(self.select_all_btn)
        self.btn_log_widget_layout.addWidget(self.start_log_btn)
        self.btn_log_widget_layout.addWidget(self.close_log_btn)
    
        # main layout
        self.main_log_layout.addWidget(self.log_lbl_1, 0, 0, 1, 4)
        self.main_log_layout.addWidget(self.temperature_check, 1, 0, 1, 1)
        self.main_log_layout.addWidget(self.pressure_check, 2, 0, 1, 1)
        self.main_log_layout.addWidget(self.humidity_check, 3, 0, 1, 1)

        self.main_log_layout.addWidget(self.ch1_check, 1, 1, 1, 1)
        self.main_log_layout.addWidget(self.ch2_check, 2, 1, 1, 1)
        self.main_log_layout.addWidget(self.ch3_check, 3, 1, 1, 1)                                                       
        self.main_log_layout.addWidget(self.ch4_check, 4, 1, 1, 1)
        
        self.main_log_layout.addWidget(self.OVG4_temperature_check, 1, 2, 1, 1)
        self.main_log_layout.addWidget(self.MQ2_check, 2, 2, 1, 1)
        self.main_log_layout.addWidget(self.MQ3_check, 3, 2, 1, 1)
        self.main_log_layout.addWidget(self.MICS5524_check, 4, 2, 1, 1)
        
        self.main_log_layout.addWidget(self.OVG4_sample_flow_check, 1, 3, 1, 1)
        self.main_log_layout.addWidget(self.MICS6814_CO_check, 2, 3, 1, 1)
        self.main_log_layout.addWidget(self.MICS6814_NH3_check, 3, 3, 1, 1)
        self.main_log_layout.addWidget(self.MICS6814_NO2_check, 4, 3, 1, 1)
        
        self.main_log_layout.addWidget(self.user_lbl, 7, 0, 1, 1)
        self.main_log_layout.addWidget(self.user_input, 7, 1, 1, 3)

        self.main_log_layout.addWidget(self.permeation_tube_lbl, 8, 0, 1, 1)
        self.main_log_layout.addWidget(self.permeation_tube_input, 8, 1, 1, 3)

        self.main_log_layout.addWidget(self.btn_log_widget, 9, 1, 1, 3)

        self.log_dlg.exec()

    def select_all_log_dlg(self):
        if self.allSelected:
            self.allSelected = False
            self.selectAllBtn.setText('Select All')

            for selectedBtn in (self.temperatureCheck, self.pressureCheck, self.humidityCheck,
                                self.ch1Check, self.ch2Check, self.ch3Check, self.ch4Check,
                                self.MFC1Check, self.MFC2Check, self.MFC3Check, self.sensor1Check,
                                self.sensor2Check, self.sensor3Check, self.sensor4Check):

                selectedBtn.setChecked(False)

        elif not self.allSelected:
            self.allSelected = True
            self.selectAllBtn.setText('Unselect All')

            for selectedBtn in (self.temperatureCheck, self.pressureCheck, self.humidityCheck,
                                self.ch1Check, self.ch2Check, self.ch3Check, self.ch4Check,
                                self.MFC1Check, self.MFC2Check, self.MFC3Check, self.sensor1Check,
                                self.sensor2Check, self.sensor3Check, self.sensor4Check):

                selectedBtn.setChecked(True)

    def create_log_file(self):
        
        self.log_directory = QFileDialog.getExistingDirectory(self.log_dlg)
        
        self.user_name = self.user_input.text()
        self.date = datetime.datetime.now().strftime("%m-%d-%Y_%Hh%Mmin")
        self.log_file_name = f'{self.log_directory}' + \
            f'/{self.user_name}'+f'_{self.date}'+'.txt'
        
        self.header_string = f'User: {self.user_name}\nDate: {self.date}\n'

        self.first_line = []
        self.creating_first_log_line()
    
        np.savetxt(self.log_file_name, np.column_stack(self.first_line),
                   fmt='%s', delimiter='   ', header=self.header_string)

        self.log_running = True

    def creating_first_log_line(self):
        self.first_line.append('Time(s)')

        if self.temperature_check.isChecked():
            self.first_line.append('flowTemperature(C)')

        if self.pressure_check.isChecked():
            self.first_line.append('flowPressure(kPa)')

        if self.humidity_check.isChecked():
            self.first_line.append('flowHumidity(%)')

        if self.ch1_check.isChecked():
            self.first_line.append('ch1Resistance(ohm)')

        if self.ch2_check.isChecked():
            self.first_line.append('ch2Resistance(ohm)')

        if self.ch3_check.isChecked():
            self.first_line.append('ch3Resistance(ohm)')

        if self.ch4_check.isChecked():
            self.first_line.append('ch4Resistance(ohm)')

        if self.OVG4_temperature_check.isChecked():
            self.first_line.append('OVG4_temp(C)')

        if self.OVG4_sample_flow_check.isChecked():
            self.first_line.append('OVG4_sample_flow(sccm)')

        if self.MQ2_check.isChecked():
            self.first_line.append('MQ2_signal (a.u.)')
        
        if self.MQ3_check.isChecked():
            self.first_line.append('MQ3_signal(a.u.)')
        
        if self.MICS5524_check.isChecked():
            self.first_line.append('MICS5524_signal(a.u.)')

        if self.MICS6814_CO_check.isChecked():
            self.first_line.append('MICS6814_CO(a.u.)')

        if self.MICS6814_NH3_check.isChecked():
            self.first_line.append('MICS6814_NH3_signal(a.u.)')

        if self.MICS6814_NO2_check.isChecked():
            self.first_line.append('MICS6814_NO2_signal(a.u.)')

    def log_data(self):
        self.writing_data = open(window.log_file_name, 'a')

        self.writing_data.write(f'{self.time_read:.3f}'+'   ')

        if self.temperature_check.isChecked():
            self.writing_data.write(f'{self.flow_temp_read:.3f}'+'  ')
        
        if self.pressure_check.isChecked():
            self.writing_data.write(f'{self.flow_pres_read:.3f}'+'  ')

        if self.humidity_check.isChecked():
            self.writing_data.write(f'{self.flow_hum_read:.3f}'+'  ')

        if self.MQ3_check.isChecked():
            self.writing_data.write(f'{self.MQ3_read:.3f}'+'  ')

        if self.MICS5524_check.isChecked():
            self.writing_data.write(f'{self.MICS5524_read:.3f}'+'  ')

        if self.MICS6814_CO_check.isChecked():
            self.writing_data.write(f'{self.MICS6814_CO_read:.3f}'+'  ')

        if self.MICS6814_NH3_check.isChecked():
            self.writing_data.write(f'{self.MICS6814_NH3_read:.3f}'+'  ')

        if self.MICS6814_NO2_check.isChecked():
            self.writing_data.write(f'{self.MICS6814_NO2_read:.3f}'+'  ')

        self.writing_data.write('\n')
        self.writing_data.close()

    ### MAIN_GRAPH SETTINGS
    def open_plot_settings_dlg(self):
        # Create Plotting Objects configuration Dialog
        self.plot_settings_dlg = QDialog()
        self.plot_settings_dlg.setWindowTitle('Plot settings')

        self.freq_aq_lbl = QLabel(self.plot_settings_dlg)
        self.freq_aq_lbl.setText('One point each: ')

        self.freq_aq_input = QDoubleSpinBox(self.plot_settings_dlg)
        self.freq_aq_input.setMinimum(1)
        self.freq_aq_input.setMaximum(3600)
        self.freq_aq_input.setValue(1)
        self.freq_aq_input.setValue(self.period/1000)
        
         # Calculating Parameters
        self.points_per_second = 1/float(self.freq_aq_input.text())
        self.points_per_minute = self.points_per_second*60
        self.points_per_hour = self.points_per_second*3600

        self.points_per_second_lbl = QLabel(self.plot_settings_dlg)
        self.points_per_second_lbl.setText('Points per second:')
        self.points_per_second_value = QLabel(self.plot_settings_dlg)
        self.points_per_second_value.setText(f'{self.points_per_second}')
        
        self.points_per_minute_lbl = QLabel(self.plot_settings_dlg)
        self.points_per_minute_lbl.setText('Points per minute:')
        self.points_per_minute_value = QLabel(self.plot_settings_dlg)
        self.points_per_minute_value.setText(f'{self.points_per_minute}')

        self.points_per_hour_lbl = QLabel(self.plot_settings_dlg)
        self.points_per_hour_lbl.setText('Points per hour:')
        self.points_per_hour_value = QLabel(self.plot_settings_dlg)
        self.points_per_hour_value.setText(f'{self.points_per_hour}')

        self.show_x_last_points_lbl = QLabel(self.plot_settings_dlg)
        self.show_x_last_points_lbl.setText('Showing Last (points):')

        self.show_x_last_points_input = QSpinBox(self.plot_settings_dlg)
        self.show_x_last_points_input.setMinimum(10)
        self.show_x_last_points_input.setMaximum(6000)
        self.show_x_last_points_input.setValue(60)
        self.show_x_last_points_input.setValue(self.main_graph.limit)

        self.showing_x_minutes = (self.show_x_last_points_input.value()*(1/self.points_per_second))/60

        self.showing_x_minutes_lbl = QLabel(self.plot_settings_dlg)
        self.showing_x_minutes_lbl.setText('Showing (minutes): ')
        self.showing_x_minutes_value = QLabel(self.plot_settings_dlg)
        self.showing_x_minutes_value.setText(f'{self.showing_x_minutes}')

        self.plot_dlg_btn_widget = QWidget(self.plot_settings_dlg)
        self.set_plot_btn = QPushButton(self.plot_dlg_btn_widget)
        self.set_plot_btn.clicked.connect(self.set_plot_settings)
        self.set_plot_btn.setText('Set')
        
        self.close_plot_btn = QPushButton(self.plot_dlg_btn_widget)
        self.close_plot_btn.setText('Close')
        self.close_plot_btn.clicked.connect(self.plot_settings_dlg.close)
        
        self.plot_dlg_btn_widget_layout = QHBoxLayout(self.plot_dlg_btn_widget)
        self.plot_dlg_btn_widget_layout.addWidget(self.set_plot_btn )
        self.plot_dlg_btn_widget_layout.addWidget(self.close_plot_btn )

        self.plot_settings_dlg_layout = QGridLayout(self.plot_settings_dlg)
        self.plot_settings_dlg_layout.addWidget(self.freq_aq_lbl, 0, 0, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.freq_aq_input, 0, 1, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.points_per_second_lbl, 1, 0, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.points_per_second_value, 1, 1, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.points_per_minute_lbl, 2, 0, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.points_per_minute_value, 2, 1, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.points_per_hour_lbl, 3, 0, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.points_per_hour_value, 3, 1, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.show_x_last_points_lbl, 4, 0, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.show_x_last_points_input, 4, 1, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.showing_x_minutes_lbl, 5, 0, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.showing_x_minutes_value, 5, 1, 1, 1)
        self.plot_settings_dlg_layout.addWidget(self.plot_dlg_btn_widget, 6, 0, 1, 2)

        self.plot_settings_dlg.exec()

    def set_plot_settings(self):        
        # Calculating Parameters
        self.points_per_second = 1/float(self.freq_aq_input.text())
        self.points_per_minute = self.points_per_second*60
        self.points_per_hour = self.points_per_second*3600

        self.showing_x_minutes = (self.show_x_last_points_input.value()*(1/self.points_per_second))/60

        self.showing_x_minutes_value.setText(f'{self.showing_x_minutes}')
        self.points_per_second_value.setText(f'{self.points_per_second}')
        self.points_per_minute_value.setText(f'{self.points_per_minute}')
        self.points_per_hour_value.setText(f'{self.points_per_hour}')

        self.period = 1000/(self.points_per_second)
        self.timer.setInterval(self.period)
        self.main_graph.limit = self.show_x_last_points_input.value()

    def system_connection(self):
        if not self.controller_connection:
            self.controller_connection = True
            try:
                self.main_system = System_Commands()
                self.start_stop_btn.setDisabled(False)
                self.controller_status_lbl.setText('ON')
                self.controller_status_lbl.setStyleSheet(
                    "background-color: rgb(80, 250, 80);")  
            except:
                print('Not supported yet')

 

        else:
            self.controller_connection = False
            self.main_system.close()
            self.start_stop_btn.setDisabled(True)
            self.controller_status_lbl.setText('OFF')
            self.controller_status_lbl.setStyleSheet("background-color: rgb(250, 80, 80);")

    def start_stop_data(self):

        if self.start_stop_btn.text() == 'Start':
            self.timer.start()
            self.timer.timeout.connect(self.new_data)  
            self.start_stop_btn.setText('Stop')

        elif self.start_stop_btn.text() == 'Stop':
            self.start_stop_btn.setText('Start')
            self.timer.stop()

    def new_data(self):
        if len(self.main_graph.time_data) == 0:
            self.time_read = 0

        else:
            self.time_read = self.main_graph.time_data[-1] + \
                self.period/1000

        self.main_graph.time_data.append(self.time_read)

        if self.controller_connection:
            self.thermocouple_read = self.main_system.read_thermocouple()
            self.main_graph.thermocouple_1_data.append(self.thermocouple_read)

        self.update_top_widget() 
        
        if self.log_running:
            self.log_data()

        if len(self.main_graph.time_data) > self.main_graph.limit:
            self.main_graph.time_data.pop(0)
            
            if self.controller_connection:
                self.main_graph.thermocouple_1_data.pop(0)        

        self.main_graph.plot_data()

    def update_top_widget(self):
        if self.controller_connection:
            self.temp_cell_1_reading.setText(f'{self.thermocouple_read:.2f}')

    def restart_plot(self):
        self.main_graph.time_data.clear()       
        self.main_graph.thermocouple_1_data.clear()

    def clear_plot(self):
        self.last_point = self.main_graph.time_data[-1]
        self.restart_plot()
        self.main_graph.time_data.append(self.last_point)
        
        if self.controller_connection:
            self.main_graph.thermocouple_1_data.append(self.main_system.read_thermocouple())

    def warning_dlg(self, value='not supported yet'):
        self.value = value
        print('not supported yet')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main_Interface()
    window.show()
    app.exec()