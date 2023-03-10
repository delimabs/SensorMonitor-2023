import sys
import datetime
import time
import numpy as np
import pandas as pd
from PySide6 import QtCore
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QSpacerItem, QWidget, QPushButton,
                               QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QCheckBox,
                               QLabel, QSpinBox, QDoubleSpinBox, QDialog, QLineEdit, QFileDialog,
                               QSizePolicy, QDockWidget, QRadioButton, QMessageBox, QGroupBox)

from arduino_commands import Arduino_Commands
from VOVGInterface import VOVG_module
from daq6510 import DAQ6510
from main_graph import Main_Graph


class Main_Interface(QMainWindow):
    def __init__(self):
        """_summary_
        The init function reads the config file, sets the main boolean controllers,
        and call other functions to draw the graphical objects.
        """
        
        super().__init__()
        self.config = pd.read_csv('configurations.txt', sep=',')
        print(self.config['address'][0])
        
        self.setGeometry(50, 50, 1200, 600)
        self.setWindowTitle('Sensor Monitor 0.9d')
        self.title_font = QFont('Helvetica', 9)
        self.title_font.setBold(True)

        #This dictionary holds the variables for general control of the data flow
        self.general_control = {'controller_connection': False,
                                'VOVG_connection': False, 
                                'daq6510_connection': False,
                                'start_stop_control': False, 
                                'data_logging': False,
                                'sequence_running': False}

        self.period = 5000
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.new_data)  
        self.timer.setInterval(self.period)  # in milliseconds

        #Variables for sequence of events:
        self.step_counter = 1

        """
            Each step of the sequence will hold four values. 
            the first value is the wait time in min, 
            the second value is a boolean  used to turn the valve on/off
            the third changes the value of the V-OVG sample sample flow, 
            and the fourth changes the temperature of the V-OVG
        """ 
        self.sequence = {'1': [0,False,0,0], '2': [0,False,0,0], '3': [0,False,0,0],
                         '4': [0,False,0,0], '5': [0,False,0,0], '6': [0,False,0,0], 
                         '7': [0,False,0,0], '8': [0,False,0,0], '9': [0,False,0,0], 
                         '10': [0,False,0,0], '11': [0,False,0,0], '12': [0,False,0,0],
                         '13': [0,False,0,0], '14': [0,False,0,0], '15': [0,False,0,0], 
                         '16':[0,False,0,0],  '17': [0,False,0,0], '18': [0,False,0,0], 
                         '19': [0,False,0,0], '20': [0,False,0,0]}

        self.start_main_layout()
        self.start_main_menu()
        self.start_connection_board()
        self.start_op_temp_monitor()
        self.start_VOVG_monitor()
        self.start_flow_info_monitor()
        self.start_resistance_monitor()
        self.start_analyte_monitor()
        self.plot_control_menu()

    ### Main Menu     
    def start_main_menu(self):
        self.main_menu = self.menuBar()
        self.file_menu = self.main_menu.addMenu('File')
        
        self.log_action = self.file_menu.addAction('Log data')
        self.log_action.triggered.connect(self.open_log_dlg)

        self.sequence_menu = self.main_menu.addAction('Sequence')
        self.sequence_menu.triggered.connect(self.open_sequence_dlg)

        self.settings_menu = self.main_menu.addMenu('Settings')
        self.plot_action = self.settings_menu.addAction('Plot settings')
        self.plot_action.triggered.connect(self.open_plot_settings_dlg)

        self.VOVG_action = self.settings_menu.addAction('VOVG settings')
        self.VOVG_action.triggered.connect(self.VOVG_controller_dlg)

        self.install_probe_monitor = self.settings_menu.addAction('Install thermocouple')
    
        self.about_action = self.main_menu.addAction('About')
        self.exit_action = self.main_menu.addAction('Exit')
        
        self.exit_action.triggered.connect(sys.exit)

    ### Main Layout
    def start_main_layout(self):
        """
            This function creates the main layout of the GUI. #1 It defines the main graph
            as the central widget and a #2 dock layout with buttons and display areas for 
            each parameter being monitored. 
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
        self.dock_widget.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)
        self.dock_widget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dock_widget)

        self.dock_menu = QWidget(self.dock_widget)
        self.dock_widget.setWidget(self.dock_menu)
                
        #3 Dock menu widgets and separating lines
        #
        self.connect_board_widget = QWidget(self.dock_menu)
        #self.connect_board_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.probe_temp_monitor_widget = QWidget(self.dock_menu)
        self.flow_info_widget = QWidget(self.dock_menu)
        self.VOVG_monitor_widget = QWidget(self.dock_menu)
        self.resistance_monitor_widget = QWidget(self.dock_menu)
        self.analyte_monitor_widget = QWidget(self.dock_menu)
        self.commands_widget = QWidget(self.dock_menu)

        self.line1 = QFrame(self.dock_menu)
        self.line1.setFrameShape(QFrame.Shape.VLine)
        self.line1.setLineWidth(2)
        self.line2 = QFrame(self.dock_menu)
        self.line2.setFrameShape(QFrame.Shape.VLine)
        self.line2.setLineWidth(2)
        self.line3 = QFrame(self.dock_menu)
        self.line3.setFrameShape(QFrame.Shape.VLine)
        self.line3.setLineWidth(2)        
        self.line4 = QFrame(self.dock_menu)
        self.line4.setFrameShape(QFrame.Shape.VLine)
        self.line4.setLineWidth(2)        
        self.line5 = QFrame(self.dock_menu)
        self.line5.setFrameShape(QFrame.Shape.VLine)
        self.line5.setLineWidth(2)
        self.line6 = QFrame(self.dock_menu)          
        self.line6.setFrameShape(QFrame.Shape.VLine)
        self.line6.setLineWidth(2)  

        self.dock_layout =  QHBoxLayout(self.dock_menu)
        self.dock_layout.addWidget(self.connect_board_widget)

        self.dock_layout.addWidget(self.line1)
        self.dock_layout.addWidget(self.probe_temp_monitor_widget)
        self.dock_layout.addWidget(self.line2)
        self.dock_layout.addWidget(self.VOVG_monitor_widget)
        self.dock_layout.addWidget(self.line3)
        self.dock_layout.addWidget(self.flow_info_widget)
        self.dock_layout.addWidget(self.line4)
        self.dock_layout.addWidget(self.resistance_monitor_widget)
        self.dock_layout.addWidget(self.line5)        
        self.dock_layout.addWidget(self.analyte_monitor_widget)
        self.dock_layout.addWidget(self.line6)
        self.dock_layout.addWidget(self.commands_widget)

        # self.spacer_1 = QSpacerItem(0,0, hData = QSizePolicy.Minimum, vData = QSizePolicy.Expanding)
        # self.dock_layout.addSpacerItem(self.spacer_1)

    ### Dock menu objects
    def start_connection_board(self):
        """
            This board contains three buttons that should run the communication
            procedure to interface the PC with the arduino board, the OVG furnace,
            and the multichannel Keithley multimeter; 
        """

        self.connect_lbl = QLabel(self.connect_board_widget)
        self.connect_lbl.setText('INSTRUMENTS')
        self.connect_lbl.setFont(self.title_font)
        self.connect_lbl.setAlignment( QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        
        self.controller_connect_btn = QPushButton(self.connect_board_widget)
        self.controller_connect_btn.setText('Controller')
        self.controller_connect_btn.clicked.connect(self.system_connection)

        self.controller_status_lbl = QLabel(self.connect_board_widget)
        self.controller_status_lbl.setText('OFF')
        self.controller_status_lbl.setFixedSize(65, 20)
        self.controller_status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.controller_status_lbl.setStyleSheet("background-color: rgb(250, 80, 80);")
        
        self.VOVG_connect_btn = QPushButton(self.connect_board_widget)
        self.VOVG_connect_btn.setText('V-OVG')
        self.VOVG_connect_btn.clicked.connect(self.VOVG_connect)

        self.VOVG_status_lbl = QLabel(self.connect_board_widget)
        self.VOVG_status_lbl.setText('OFF')
        self.VOVG_status_lbl.setFixedSize(65, 20)
        self.VOVG_status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.VOVG_status_lbl.setStyleSheet("background-color: rgb(250, 80, 80);")

        self.start_daq_btn = QPushButton(self.connect_board_widget)
        self.start_daq_btn.setText('Keithley DAQ')
        self.start_daq_btn.clicked.connect(self.daq6510_connect)

        self.status_daq_lbl = QLabel(self.connect_board_widget)
        self.status_daq_lbl.setText('OFF')
        self.status_daq_lbl.setFixedSize(65, 20)
        self.status_daq_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.status_daq_lbl.setStyleSheet("background-color: rgb(250, 80, 80);")

        # Layout
        self.connection_board_layout = QGridLayout(self.connect_board_widget)
        self.connection_board_layout.addWidget(self.connect_lbl, 0, 0, 1, 2)
        self.connection_board_layout.addItem(QSpacerItem(1, 20), 1, 0, 1, 2)
        self.connection_board_layout.addWidget(self.controller_connect_btn, 2, 0, 1, 1)
        self.connection_board_layout.addWidget(self.controller_status_lbl, 2, 1, 1, 1)
        self.connection_board_layout.addWidget(self.VOVG_connect_btn, 3, 0, 1, 1)
        self.connection_board_layout.addWidget(self.VOVG_status_lbl, 3, 1, 1, 1)
        self.connection_board_layout.addWidget(self.start_daq_btn, 4, 0, 1, 1)
        self.connection_board_layout.addWidget(self.status_daq_lbl, 4, 1, 1, 1)

    def start_op_temp_monitor(self):
        """
            This function creates the visual objects related to the sensor
            operating temperature. It reads the thermocouple from arduino
            connected through SPI with a MAX 6675 chip.

            For the moment thermocouple 2 is not active.
        """

        self.op_temp_monitor_lbl = QLabel(self.probe_temp_monitor_widget)
        self.op_temp_monitor_lbl.setText('OPERATING TEMP.')
        self.op_temp_monitor_lbl.setFont(self.title_font)
        self.op_temp_monitor_lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.temp_cell_1_lbl = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_1_lbl.setText('Thermocouple 1: ')
        self.temp_cell_1_lbl.setAlignment(QtCore.Qt.AlignHCenter)

        self.temp_cell_1_reading = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_1_reading.setLineWidth(2)
        self.temp_cell_1_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.temp_cell_1_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.temp_cell_1_reading.setFixedWidth(60)
        self.temp_cell_1_reading.setText('000.00')

        self.temp_cell_2_lbl = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_2_lbl.setText('Thermocouple 2: ')
        self.temp_cell_2_lbl.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

        self.temp_cell_2_reading = QLabel(self.probe_temp_monitor_widget)
        self.temp_cell_2_reading.setLineWidth(2)
        self.temp_cell_2_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.temp_cell_2_reading.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.temp_cell_2_reading.setFixedWidth(60)
        self.temp_cell_2_reading.setText('000.00')

        self.probe_temp_show_btn = QPushButton(self.probe_temp_monitor_widget)
        self.probe_temp_show_btn.setText('Show')
        self.probe_temp_show_btn.clicked.connect(self.main_graph.add_thermo_1)

        self.probe_temp_layout = QGridLayout(self.probe_temp_monitor_widget)
        self.probe_temp_layout.addWidget(self.op_temp_monitor_lbl, 0, 0, 1, 2)
        self.probe_temp_layout.addWidget(self.temp_cell_1_lbl, 1, 0, 1, 1)
        self.probe_temp_layout.addWidget(self.temp_cell_1_reading, 1, 1, 1, 1)
        self.probe_temp_layout.addWidget(self.temp_cell_2_lbl, 2, 0, 1, 1)
        self.probe_temp_layout.addWidget(self.temp_cell_2_reading, 2, 1, 1, 1)
        self.probe_temp_layout.addItem(QSpacerItem(1, 20), 3, 0, 1, 2)
        self.probe_temp_layout.addWidget(
            self.probe_temp_show_btn, 4, 0, 1, 2, QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

    def start_VOVG_monitor(self):
        """
            This function creates the visual objects for monitoring the 
            V-OVG furnace temperature and gas sample flow in standard 
            cubic centimeters
        """

        self.VOVG_Lbl = QLabel(self.VOVG_monitor_widget)
        self.VOVG_Lbl.setText('V-OVG')
        self.VOVG_Lbl.setFont(self.title_font)
        self.VOVG_Lbl.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.furnace_temp_lbl = QLabel(self.VOVG_monitor_widget)
        self.furnace_temp_lbl.setText('Furnace temp (C): ')

        self.sample_flow_lbl = QLabel(self.VOVG_monitor_widget)
        self.sample_flow_lbl.setText('Sample flow (sccm): ')

        self.furnace_temp_reading = QLabel(self.VOVG_monitor_widget)
        self.furnace_temp_reading.setLineWidth(2)
        self.furnace_temp_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.furnace_temp_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.furnace_temp_reading.setFixedWidth(60)
        self.furnace_temp_reading.setText('000.00')

        self.sample_flow_reading = QLabel(self.VOVG_monitor_widget)
        self.sample_flow_reading.setLineWidth(2)
        self.sample_flow_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.sample_flow_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.sample_flow_reading.setFixedWidth(60)
        self.sample_flow_reading.setText('000.00')

        self.VOVG_show_btn = QPushButton(self.VOVG_monitor_widget)
        self.VOVG_show_btn.setText('Show')
        self.VOVG_show_btn.clicked.connect(self.main_graph.add_VOVG)
        self.VOVG_show_btn.setDisabled(True)
        
        # Layout GridBox
        self.VOVG_board_layout = QGridLayout(self.VOVG_monitor_widget)
        self.VOVG_board_layout.addWidget(self.VOVG_Lbl, 0, 0, 1, 2)
        self.VOVG_board_layout.addWidget(self.furnace_temp_lbl, 1, 0, 1, 1)
        self.VOVG_board_layout.addWidget(self.furnace_temp_reading, 1, 1, 1, 1)
        self.VOVG_board_layout.addWidget(self.sample_flow_lbl, 2, 0, 1, 1)
        self.VOVG_board_layout.addWidget(self.sample_flow_reading, 2, 1, 1, 1)
        self.VOVG_board_layout.addItem(QSpacerItem(1, 20), 3, 0, 1, 2)
        self.VOVG_board_layout.addWidget(self.VOVG_show_btn, 4, 0, 1, 2,
                                         QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

    def start_flow_info_monitor(self):
        self.flow_info_lbl = QLabel(self.flow_info_widget)
        self.flow_info_lbl.setText('FLOW INFO')
        self.flow_info_lbl.setFont(self.title_font)
        self.flow_info_lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.flow_temp_opt = QRadioButton(self.flow_info_widget)
        self.flow_temp_opt.setText('Temp, C : ')
        self.flow_temp_opt.setChecked(True)

        self.flow_press_opt = QRadioButton(self.flow_info_widget)
        self.flow_press_opt.setText('Pressure, kPa : ')

        self.flow_humidity_opt = QRadioButton(self.flow_info_widget)
        self.flow_humidity_opt.setText('Humidity, % : ')

        self.flow_temp_reading = QLabel(self.flow_info_widget)
        self.flow_temp_reading.setLineWidth(2)
        self.flow_temp_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.flow_temp_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.flow_temp_reading.setFixedWidth(60)
        self.flow_temp_reading.setText('00.00')

        self.flow_press_reading = QLabel(self.flow_info_widget)
        self.flow_press_reading.setLineWidth(2)
        self.flow_press_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.flow_press_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.flow_press_reading.setFixedWidth(60)
        self.flow_press_reading.setText('00.00')

        self.flow_humidity_reading = QLabel(self.flow_info_widget)
        self.flow_humidity_reading.setLineWidth(2)
        self.flow_humidity_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.flow_humidity_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.flow_humidity_reading.setFixedWidth(60)
        self.flow_humidity_reading.setText('00.00')

        self.flow_info_show_btn = QPushButton(self.flow_info_widget)
        self.flow_info_show_btn.setText('Show')
        self.flow_info_show_btn.clicked.connect(self.show_bme)

        self.flow_info_layout = QGridLayout(self.flow_info_widget)
        self.flow_info_layout.addWidget(self.flow_info_lbl, 0, 0, 1, 2)
        self.flow_info_layout.addWidget(self.flow_temp_opt, 1, 0, 1, 1)
        self.flow_info_layout.addWidget(self.flow_press_opt, 2, 0, 1, 1)
        self.flow_info_layout.addWidget(self.flow_humidity_opt, 3, 0, 1, 1)
        self.flow_info_layout.addWidget(self.flow_temp_reading, 1, 1, 1, 1)
        self.flow_info_layout.addWidget(self.flow_press_reading, 2, 1, 1, 1)
        self.flow_info_layout.addWidget(self.flow_humidity_reading, 3, 1, 1, 1)
        self.flow_info_layout.addWidget(self.flow_info_show_btn, 4, 0, 1, 2, QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

    def show_bme(self):
        if self.flow_temp_opt.isChecked():
            self.main_graph.add_BME_temp()

        elif self.flow_press_opt.isChecked():
            self.main_graph.add_BME_press()

        elif self.flow_humidity_opt.isChecked():
            self.main_graph.add_BME_humid()

    def start_resistance_monitor(self):
        
        self.resistance_monitor_lbl = QLabel(self.resistance_monitor_widget)
        self.resistance_monitor_lbl.setText('RESISTANCE MONITOR')
        self.resistance_monitor_lbl.setFont(self.title_font)
        self.resistance_monitor_lbl.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.ch1_lbl = QLabel(self.resistance_monitor_widget)
        self.ch1_lbl.setText('Channel 1:')

        self.ch2_lbl = QLabel(self.resistance_monitor_widget)
        self.ch2_lbl.setText('Channel 2: ')

        self.ch1_reading = QLabel(self.resistance_monitor_widget)
        self.ch1_reading.setLineWidth(2)
        self.ch1_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.ch1_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.ch1_reading.setFixedWidth(70)
        self.ch1_reading.setText('000.00')

        self.ch2_reading = QLabel(self.resistance_monitor_widget)
        self.ch2_reading.setLineWidth(2)
        self.ch2_reading.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.ch2_reading.setAlignment(QtCore.Qt.AlignHCenter)
        self.ch2_reading.setFixedWidth(70)
        self.ch2_reading.setText('000.00')

        self.resistance_monitor_show_btn = QPushButton(self.resistance_monitor_widget)
        self.resistance_monitor_show_btn.setText('Show')
        self.resistance_monitor_show_btn.clicked.connect(self.main_graph.add_resistance)
        
        # Layout GridBox
        self.resistance_layout = QGridLayout(self.resistance_monitor_widget)
        self.resistance_layout.addWidget(self.resistance_monitor_lbl, 0, 0, 1, 2)
        self.resistance_layout.addWidget(self.ch1_lbl, 1, 0, 1, 1)
        self.resistance_layout.addWidget(self.ch1_reading, 1, 1, 1, 1)
        self.resistance_layout.addWidget(self.ch2_lbl, 2, 0, 1, 1)
        self.resistance_layout.addWidget(self.ch2_reading, 2, 1, 1, 1)
        self.resistance_layout.addItem(QSpacerItem(1, 20), 3, 0, 1, 2)
        self.resistance_layout.addWidget(self.resistance_monitor_show_btn, 4, 0, 1, 2,
                                         QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

    def start_analyte_monitor(self):
        self.analyte_monitor_lbl = QLabel(self.analyte_monitor_widget)
        self.analyte_monitor_lbl.setText('ANALYTE MONITOR')
        self.analyte_monitor_lbl.setFont(self.title_font)
        self.analyte_monitor_lbl.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.analyte_unit_lbl = QLabel(self.analyte_monitor_widget)
        self.analyte_unit_lbl.setText('MICS 5524')

        self.analyte_reading_lbl = QLabel(self.analyte_monitor_widget)
        self.analyte_reading_lbl.setLineWidth(2)
        self.analyte_reading_lbl.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.analyte_reading_lbl.setFixedWidth(70)
        self.analyte_reading_lbl.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.analyte_reading_lbl.setText('0000.00')

        self.analyte_show_btn = QPushButton(self.analyte_monitor_widget)
        self.analyte_show_btn.setText('Show')
        self.analyte_show_btn.clicked.connect(self.main_graph.add_MICS5524)

        self.analyte_layout = QGridLayout(self.analyte_monitor_widget)
        self.analyte_layout.addWidget(self.analyte_monitor_lbl, 0, 0, 1, 1)
        self.analyte_layout.addWidget(
            self.analyte_unit_lbl, 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.analyte_layout.addWidget(
            self.analyte_reading_lbl, 2, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.analyte_layout.addItem(QSpacerItem(1, 20), 3, 0, 1, 1)
        self.analyte_layout.addWidget(
            self.analyte_show_btn, 4, 0, 1, 1, QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

    def plot_control_menu(self):
        """
            This function creates the buttons to control
            plotting behavior. The user can clean the plot,
            restart the plot and start or stop it.
        """
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
    
    ### Logging options
    def open_log_dlg(self):
        self.log_dlg = QDialog()
        self.log_dlg.resize(400, 200)
        self.log_dlg.setWindowTitle('Start data logging')

        self.main_log_layout = QGridLayout(self.log_dlg)

        self.all_selected = False
        
        self.log_lbl_1 = QLabel(self.log_dlg)
        self.log_lbl_1.setText('Choose the variables to LOG:')

        # first column
        self.flow_temp_check = QCheckBox('Flow Temperature', self.log_dlg)
        self.flow_press_check = QCheckBox('Flow Pressure', self.log_dlg)
        self.flow_humid_check = QCheckBox('Flow Humidity', self.log_dlg)

        # second column
        self.ch1_check = QCheckBox('ch1 Resistance', self.log_dlg)
        self.ch2_check = QCheckBox('ch2 Resistance', self.log_dlg)
        
        # third column
        self.VOVG_temp_check = QCheckBox('VOVG Temperature (C)', self.log_dlg)
        self.VOVG_sample_flow_check = QCheckBox('VOVG Sample Flow (sccm)', self.log_dlg)
        self.thermo_1_check = QCheckBox('Thermocouple 1', self.log_dlg)
        self.thermo_2_check = QCheckBox('Thermocouple 2', self.log_dlg)

        # fourth column
        self.MICS5524_check = QCheckBox('MICS5524', self.log_dlg)


        self.thermo_2_check.setDisabled(True)
        self.ch1_check.setDisabled(True)
        self.ch2_check.setDisabled(True)

        if self.general_control['VOVG_connection']:
            self.VOVG_temp_check.setDisabled(False)
            self.VOVG_sample_flow_check.setDisabled(False)
        else:
            self.VOVG_temp_check.setDisabled(False)
            self.VOVG_sample_flow_check.setDisabled(False)
        
        if self.general_control['daq6510_connection']:
            self.ch1_check.setDisabled(False)
        else:
            self.ch1_check.setDisabled(True)


        # objects line 1 under columns
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
        self.select_all_btn.clicked.connect(self.select_all_log_dlg)
       
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

        self.main_log_layout.addWidget(self.flow_temp_check, 1, 0, 1, 1)
        self.main_log_layout.addWidget(self.flow_press_check, 2, 0, 1, 1)
        self.main_log_layout.addWidget(self.flow_humid_check, 3, 0, 1, 1)
        self.main_log_layout.addWidget(self.MICS5524_check, 4, 0, 1, 1)

        self.main_log_layout.addWidget(self.VOVG_temp_check, 1, 1, 1, 1)
        self.main_log_layout.addWidget(self.VOVG_sample_flow_check, 2, 1, 1, 1)
        self.main_log_layout.addWidget(self.thermo_1_check, 3, 1, 1, 1)
        self.main_log_layout.addWidget(self.thermo_2_check, 4, 1, 1, 1)

        self.main_log_layout.addWidget(self.ch1_check, 1, 2, 1, 1)
        self.main_log_layout.addWidget(self.ch2_check, 2, 2, 1, 1)

        self.main_log_layout.addWidget(self.user_lbl, 7, 0, 1, 1)
        self.main_log_layout.addWidget(self.user_input, 7, 1, 1, 3)

        self.main_log_layout.addWidget(self.permeation_tube_lbl, 8, 0, 1, 1)
        self.main_log_layout.addWidget(self.permeation_tube_input, 8, 1, 1, 3)

        self.main_log_layout.addWidget(self.btn_log_widget, 9, 1, 1, 3)

        self.log_dlg.exec()

    def select_all_log_dlg(self):
        if self.all_selected:
            self.all_selected = False
            self.select_all_btn.setText('Select All')

            for selected_btn in (self.flow_temp_check, self.flow_press_check, self.flow_humid_check,
                                self.ch1_check, self.ch2_check, self.MICS5524_check, self.VOVG_temp_check, 
                                self.VOVG_sample_flow_check, self.thermo_1_check, self.thermo_2_check):
                
                if selected_btn.isEnabled():
                    selected_btn.setChecked(False)

        elif not self.all_selected:
            self.all_selected = True
            self.select_all_btn.setText('Unselect All')

            for selected_btn in (self.flow_temp_check, self.flow_press_check, self.flow_humid_check,
                                self.ch1_check, self.ch2_check, self.MICS5524_check, self.VOVG_temp_check, 
                                self.VOVG_sample_flow_check, self.thermo_1_check, self.thermo_2_check):
                
                if selected_btn.isEnabled():
                    selected_btn.setChecked(True)

    def create_log_file(self):
        
        self.log_directory = QFileDialog.getExistingDirectory(self.log_dlg)
        
        self.user_name = self.user_input.text()
        self.date = datetime.datetime.now().strftime("%m-%d-%Y_%Hh%Mmin")
        self.tube_info = self.permeation_tube_input.text()
        self.log_file_name = f'{self.log_directory}' + \
            f'/{self.user_name}'+f'_{self.date}'+'.txt'
        
        self.header_string = f'User: {self.user_name}\nDate: {self.date}\nPerm. tube info: {self.tube_info}'

        self.first_line = []
        self.create_first_log_line()
    
        np.savetxt(self.log_file_name, np.column_stack(self.first_line),
                   fmt='%s', delimiter='   ', header=self.header_string)

        self.general_control['data_logging'] = True

    def create_first_log_line(self):
        self.first_line.append('Time_(min)')

        if self.flow_temp_check.isChecked():
            self.first_line.append('flow_temp_C')

        if self.flow_press_check.isChecked():
            self.first_line.append('flow_press_kPa')

        if self.flow_humid_check.isChecked():
            self.first_line.append('flow_humid_%')
        
        if self.MICS5524_check.isChecked():
            self.first_line.append('MICS5524_signal_a.u.')
        
        if self.thermo_1_check.isChecked():
            self.first_line.append('thermocouple_1')
        
        if self.thermo_2_check.isChecked():
            self.first_line.append('thermocouple_2')
        
        if self.VOVG_temp_check.isChecked():
            self.first_line.append('VOVG_temp_C')

        if self.VOVG_sample_flow_check.isChecked():
            self.first_line.append('VOVG_sample_flow_sccm')

        if self.ch1_check.isChecked():
            self.first_line.append('ch1_resist_Ohm')

        if self.ch2_check.isChecked():
            self.first_line.append('ch2_resist_Ohm')

    def log_data(self):
        self.writing_data = open(self.log_file_name, 'a')

        self.writing_data.write(f'{self.time_read:.4f}'+'   ')

        if self.flow_temp_check.isChecked():
            self.writing_data.write(f'{self.flow_temp_read:.2f}'+'  ')
        
        if self.flow_press_check.isChecked():
            self.writing_data.write(f'{self.flow_press_read:.2f}'+'  ')

        if self.flow_humid_check.isChecked():
            self.writing_data.write(f'{self.flow_humid_read:.2f}'+'  ')

        if self.MICS5524_check.isChecked():
            self.writing_data.write(f'{self.analyte_read:.2f}'+'  ')

        if self.thermo_1_check.isChecked():
            self.writing_data.write(f'{self.thermocouple_1_read:.2f}'+'  ')
        
        if self.VOVG_temp_check.isChecked():
            self.writing_data.write(f'{self.furnace_temp_read:.3f}'+'  ')

        if self.VOVG_sample_flow_check.isChecked():
            self.writing_data.write(f'{self.sample_flow_read:.3f}'+'  ')
        
        if self.ch1_check.isChecked():
            self.writing_data.write(f'{self.resistance_read:.5f}')


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

    ### OwlStone V-OVG vapor generator
    def VOVG_controller_dlg(self):
        self.VOVG_dlg = QDialog()
        self.VOVG_dlg.setWindowTitle('V-OVG settings')

        self.VOVG_dlg_lbl = QLabel(self.VOVG_dlg)
        self.VOVG_dlg_lbl.setText('Set furnace temperature and sample flow:')

        self.VOVG_furnace_lbl = QLabel(self.VOVG_dlg)
        self.VOVG_furnace_lbl.setText('Furnace temperature (C): ')
        
        self.VOVG_furnace_input = QDoubleSpinBox(self.VOVG_dlg)
        self.VOVG_furnace_input.setMinimum(25)
        self.VOVG_furnace_input.setMaximum(100)
        self.VOVG_furnace_input.setValue(25)
        self.VOVG_furnace_input.setFixedSize(65, 30)

        self.VOVG_sample_flow_lbl = QLabel(self.VOVG_dlg)
        self.VOVG_sample_flow_lbl.setText('Sample flow (sccm): ')

        self.VOVG_sample_flow_input = QDoubleSpinBox(self.VOVG_dlg)
        self.VOVG_sample_flow_input.setMinimum(0)
        self.VOVG_sample_flow_input.setMaximum(250)
        self.VOVG_sample_flow_input.setValue(20)
        self.VOVG_sample_flow_input.setFixedSize(65, 30)
        
        self.VOVG_btn_widget = QWidget(self.VOVG_dlg)
        
        self.VOVG_dlg_set_btn = QPushButton(self.VOVG_btn_widget)
        self.VOVG_dlg_set_btn.setText('Set')
        self.VOVG_dlg_set_btn.clicked.connect(self.VOVG_set_settings)
        
        self.VOVG_dlg_cancel_btn  = QPushButton(self.VOVG_btn_widget)
        self.VOVG_dlg_cancel_btn.setText('Cancel')
        self.VOVG_dlg_cancel_btn.clicked.connect(self.VOVG_dlg.reject)

        self.VOVG_btn_layout = QHBoxLayout(self.VOVG_btn_widget)
        self.VOVG_btn_layout.addWidget(self.VOVG_dlg_set_btn)
        self.VOVG_btn_layout.addWidget(self.VOVG_dlg_cancel_btn)

        self.VOVG_dlg_main_layout = QGridLayout(self.VOVG_dlg)
        self.VOVG_dlg_main_layout.addWidget(self.VOVG_dlg_lbl, 0, 0, 1, 2)
        self.VOVG_dlg_main_layout.addWidget(self.VOVG_furnace_lbl, 1, 0, 1, 1)
        self.VOVG_dlg_main_layout.addWidget(self.VOVG_furnace_input, 1, 1, 1, 1)
        self.VOVG_dlg_main_layout.addWidget(self.VOVG_sample_flow_lbl, 2, 0, 1, 1)
        self.VOVG_dlg_main_layout.addWidget(self.VOVG_sample_flow_input, 2, 1, 1, 1)
        self.VOVG_dlg_main_layout.addWidget(self.VOVG_btn_widget, 3, 0, 1, 2)

        self.VOVG_dlg.exec()

    def VOVG_connect(self):
        if not self.general_control['VOVG_connection']: 
            self.general_control['VOVG_connection'] = True
            self.VOVG_instrument = VOVG_module(serial_port=self.config['address'][1])
            self.VOVG_show_btn.setDisabled(False)
            self.start_stop_btn.setDisabled(False)
            self.VOVG_status_lbl.setText('ON')
            self.VOVG_status_lbl.setStyleSheet("background-color: rgb(80, 250, 80);")
            
        else:
            self.general_control['VOVG_connection'] = False
            self.VOVG_show_btn.setDisabled(True)
            self.VOVG_status_lbl.setText('OFF')
            self.VOVG_status_lbl.setStyleSheet("background-color: rgb(250, 80, 80);")

    def VOVG_set_settings(self):
        """
        This routine changes the set point of the OVG furnace and mass flow
        controller after the dialog box of the OVG settings
        """
        furnace_temp_set_point = float(self.VOVG_furnace_input.text())
        sample_flow_set_point = float(self.VOVG_sample_flow_input.text())/10

        self.VOVG_instrument.set_furnace_temp(furnace_temp_set_point)
        self.VOVG_instrument.set_sample_flow(sample_flow_set_point)

    ### DAQ6510
    def daq6510_connect(self):
        if not self.general_control['daq6510_connection']:
            self.general_control['daq6510_connection'] = True
            self.multimeter = DAQ6510()
            self.multimeter.beep()
            self.status_daq_lbl.setText('ON')
            self.status_daq_lbl.setStyleSheet("background-color: rgb(80, 250, 80);")
            
        else:
            self.general_control['daq6510_connection'] = False
            self.status_daq_lbl.setText('OFF')
            self.status_daq_lbl.setStyleSheet("background-color: rgb(250, 80, 80);")

    ### Controlling and Acquisition
    def system_connection(self):

        if self.general_control['controller_connection']:
            self.general_control['controller_connection'] = False
            self.arduino.close()
            self.start_stop_btn.setDisabled(True)
            self.controller_status_lbl.setText('OFF')
            self.controller_status_lbl.setStyleSheet("background-color: rgb(250, 80, 80);")

        else:
            self.arduino = Arduino_Commands(serial_port=self.config['address'][0])
            self.general_control['controller_connection'] = True

            self.start_stop_btn.setDisabled(False)
            self.controller_status_lbl.setText('ON')
            self.controller_status_lbl.setStyleSheet(
                        "background-color: rgb(80, 250, 80);")  
    
    def start_stop_data(self):
        if self.start_stop_btn.text() == 'Start':
            self.timer.start()
            self.start_stop_btn.setText('Stop')

        elif self.start_stop_btn.text() == 'Stop':
            self.start_stop_btn.setText('Start')
            self.timer.stop()

    def new_data(self):
        
        if len(self.main_graph.time_data) == 0:
            self.time_read = 0

        else:
            self.time_read = self.main_graph.time_data[-1] + \
                self.period/60000

        self.main_graph.time_data.append(self.time_read)
        
        if self.general_control['controller_connection']:
            self.thermocouple_1_read = self.arduino.read_thermocouple_1()
            self.flow_temp_read = self.arduino.read_flow_temp()
            self.flow_press_read = self.arduino.read_flow_press()/1000
            self.flow_humid_read = self.arduino.read_flow_humidity()
            self.analyte_read = self.arduino.read_MICS5524()

            self.main_graph.thermocouple_1_data.append(self.thermocouple_1_read)
            self.main_graph.bme_temp_data.append(self.flow_temp_read)
            self.main_graph.bme_press_data.append(self.flow_press_read)
            self.main_graph.bme_humid_data.append(self.flow_humid_read)
            self.main_graph.mics_data.append(self.analyte_read)
     
        if self.general_control['VOVG_connection']:
            self.furnace_temp_read = self.VOVG_instrument.read_furnace_temp()
            time.sleep(0.01)
            self.sample_flow_read = self.VOVG_instrument.read_sample_flow()*10
            time.sleep(0.01)

            self.furnace_temp_reading.setText(f'{self.furnace_temp_read:.2f}')
            self.sample_flow_reading.setText(f'{self.sample_flow_read:.2f}')

            self.main_graph.VOVG_furnace_data.append(self.furnace_temp_read)
            self.main_graph.VOVG_sample_flow_data.append(self.sample_flow_read)

        if self.general_control['daq6510_connection']:
            self.resistance_read = float(self.multimeter.read_ch_1())

            self.main_graph.resistance_data.append(self.resistance_read)

        self.update_top_widget() 
        
        if self.general_control['data_logging']:
            self.log_data()

        if self.general_control['sequence_running']:
            self.run_event()

        if len(self.main_graph.time_data) > self.main_graph.limit:
            self.main_graph.time_data.pop(0)
            
            if self.general_control['controller_connection']:
                self.main_graph.thermocouple_1_data.pop(0)
                self.main_graph.bme_temp_data.pop(0)
                self.main_graph.bme_press_data.pop(0)
                self.main_graph.bme_humid_data.pop(0)
                self.main_graph.mics_data.pop(0)

            if self.general_control['VOVG_connection']:
                self.main_graph.VOVG_furnace_data.pop(0)
                self.main_graph.VOVG_sample_flow_data.pop(0)

            if self.general_control['daq6510_connection']:
                self.main_graph.resistance_data.pop(0)
    
        self.main_graph.plot_data()

    def update_top_widget(self):
        if self.general_control['controller_connection']:
            self.temp_cell_1_reading.setText(f'{self.thermocouple_1_read:.2f}')
            self.flow_temp_reading.setText(f'{self.flow_temp_read:.2f}')
            self.flow_press_reading.setText(f'{self.flow_press_read:.2f}')
            self.flow_humidity_reading.setText(f'{self.flow_humid_read:.2f}')
            self.analyte_reading_lbl.setText(f'{self.analyte_read:.2f}')
        
        if self.general_control['VOVG_connection']:
            self.furnace_temp_reading.setText(f'{self.furnace_temp_read:.2f}')
            self.sample_flow_reading.setText(f'{self.sample_flow_read:.2f}')
        
        if self.general_control['daq6510_connection']:
            self.ch1_reading.setText(f'{self.resistance_read:.3f}')

    """SEQUENCE OF EVENTS"""
    def open_sequence_dlg(self):
        """
            This function creates the dialog box to define how
            the experiment will run. The user has the possibility 
            to choose what events the system will carry out at a 
            specific time. The possible events are open or close
            the exposure valve and also to change the set points
            of sample flow and furnace temperature from V-OVG. 
        """
        self.seq_dlg = QDialog()
        self.seq_dlg.resize(400, 700)
        self.seq_dlg.setWindowTitle('Define sequence of events')

        self.step_counter = 1

        #1. Create objects inside a group box
        self.upper_group_box = QGroupBox(self.seq_dlg)
        self.upper_group_box.setTitle('Define command: ')

        self.step_lbl = QLabel(self.upper_group_box)
        self.step_lbl.setText('Step '+f'{self.step_counter}:')

        self.wait_time_lbl = QLabel(self.upper_group_box)
        self.wait_time_lbl.setText('Wait (min): ')

        self.wait_time_input = QLineEdit(self.upper_group_box)
        self.wait_time_input.setFixedSize(75, 20)

        self.valve_on_cmd = QRadioButton(self.upper_group_box)
        self.valve_on_cmd.setText('Open valve')

        self.valve_off_cmd = QRadioButton(self.upper_group_box)
        self.valve_off_cmd.setText('Close valve')
        self.valve_off_cmd.setChecked(True)
        
        self.VOVG_flow_cmd_lbl = QLabel(self.upper_group_box)
        self.VOVG_flow_cmd_lbl.setText('Set V-OVG flow (sccm): ')
        self.VOVG_flow_seq_input = QLineEdit(self.upper_group_box)
        self.VOVG_flow_seq_input.setPlaceholderText(str(0))
        self.VOVG_flow_seq_input.setFixedSize(75, 20)

        self.VOVG_temp_cmd_lbl = QLabel(self.upper_group_box)
        self.VOVG_temp_cmd_lbl.setText('Set V-OVG temp (C): ')
        self.VOVG_temp_seq_input = QLineEdit(self.upper_group_box)
        self.VOVG_temp_seq_input.setPlaceholderText(str(25))
        self.VOVG_temp_seq_input.setFixedSize(75, 20)

        #Layout
        self.upper_group_box_layout = QGridLayout(self.upper_group_box)
        self.upper_group_box_layout.addWidget(self.step_lbl, 0, 0, 1, 2)
        self.upper_group_box_layout.addWidget(self.wait_time_lbl, 1, 0, 1, 1)
        self.upper_group_box_layout.addWidget(self.wait_time_input, 1, 1, 1, 1)
        self.upper_group_box_layout.addWidget(self.valve_on_cmd, 2, 0, 1, 2)
        self.upper_group_box_layout.addWidget(self.valve_off_cmd, 3, 0, 1, 2)
        self.upper_group_box_layout.addWidget(self.VOVG_flow_cmd_lbl, 4, 0, 1, 1)
        self.upper_group_box_layout.addWidget(self.VOVG_flow_seq_input, 4, 1, 1, 1)
        self.upper_group_box_layout.addWidget(self.VOVG_temp_cmd_lbl, 5, 0, 1, 1)
        self.upper_group_box_layout.addWidget(self.VOVG_temp_seq_input, 5, 1, 1, 1)

        #3. Buttons to add or erase events
        self.btn_box_seq = QWidget(self.seq_dlg)

        self.add_cmd_btn = QPushButton(self.btn_box_seq)
        self.add_cmd_btn.setText('Add event')
        self.add_cmd_btn.clicked.connect(self.add_event)

        self.erase_cmd_btn = QPushButton(self.btn_box_seq)
        self.erase_cmd_btn.setText('Erase event')
        self.erase_cmd_btn.clicked.connect(self.erase_event)

        self.btn_box_seq_layout = QVBoxLayout(self.btn_box_seq)
        self.btn_box_seq_layout.addWidget(self.add_cmd_btn)
        self.btn_box_seq_layout.addWidget(self.erase_cmd_btn)

        self.seq_lbl = QLabel(self.seq_dlg)
        self.seq_lbl.setText('Sequence:')

        #4. This box shows the user what is the full sequence
        self.full_seq_box = QLabel(self.seq_dlg)
        self.full_seq_box.setLineWidth(2)
        self.full_seq_box.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.full_seq_box.setAlignment(QtCore.Qt.AlignHCenter)
        self.full_seq_box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        #5. Buttons to RUN or cancel
        self.run_seq_btn = QPushButton(self.seq_dlg)
        self.run_seq_btn.setText('Run')
        self.run_seq_btn.clicked.connect(self.run_sequence)

        self.cancel_seq_btn = QPushButton(self.seq_dlg)
        self.cancel_seq_btn.setText('Cancel')
        self.cancel_seq_btn.clicked.connect(self.seq_dlg.reject)

        self.sequence_str = ''
        self.list_of_events = []

        self.seq_dlg_main_layout = QGridLayout(self.seq_dlg)
        self.seq_dlg_main_layout.addWidget(self.upper_group_box, 0, 0, 3, 2, alignment=(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter))
        self.seq_dlg_main_layout.addWidget(self.btn_box_seq, 1, 2, 1, 1, alignment=(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter))
        self.seq_dlg_main_layout.addWidget(self.seq_lbl, 3, 0, 1, 3)
        self.seq_dlg_main_layout.addWidget(self.full_seq_box, 4, 0, 20, 3)
        self.seq_dlg_main_layout.addWidget(self.run_seq_btn, 24, 1, 1, 1)        
        self.seq_dlg_main_layout.addWidget(self.cancel_seq_btn, 24, 2, 1, 1)  

        self.seq_dlg.exec()   
    
    def add_event(self):
        """
            This function defines a event. It changes the values
            on the sequence dictionary and show the user the commands
            in the sequence box.
        """
        try:
            if self.step_counter <= 20:
                wait = float(self.wait_time_input.text())

                if self.valve_on_cmd.isChecked():
                    valve_open = True
                elif self.valve_off_cmd.isChecked():
                    valve_open = False

                VOVG_flow = float(self.VOVG_flow_seq_input.text())
                VOVG_furnace = float(self.VOVG_temp_seq_input.text())

                if self.step_counter == 1:
                    self.sequence[f'{self.step_counter}'][0] = wait
                else:
                    self.sequence[f'{self.step_counter}'][0] = wait+self.sequence[f'{self.step_counter-1}'][0]
                
                self.sequence[f'{self.step_counter}'][1] = valve_open
                self.sequence[f'{self.step_counter}'][2] = VOVG_flow
                self.sequence[f'{self.step_counter}'][3] = VOVG_furnace

                if self.valve_on_cmd.isChecked():
                    seq_str_line = f'Step {self.step_counter}: wait {wait} min, OPEN valve, set Sample Flow to {VOVG_flow} sccm and OVG furnace set to {VOVG_furnace} C\n'
                
                elif self.valve_off_cmd.isChecked():
                    seq_str_line = f'Step {self.step_counter}: wait {wait} min, CLOSE valve, set Sample Flow to {VOVG_flow} sccm and OVG furnace set to {VOVG_furnace} C\n'
                    
                self.sequence_str = self.sequence_str+seq_str_line

                self.full_seq_box.setText(self.sequence_str)
                self.list_of_events.append(seq_str_line)

                self.step_counter  = self.step_counter + 1
                self.step_lbl.setText('Step '+f'{self.step_counter}:')

            else:
                self.warning_dlg('Number max of events is 20!')
        
        except ValueError:
            self.warning_dlg('Please, enter all sequence values!')
        
    def erase_event(self):
        """
            This function deletes the last event defined by the user
        """
        
        self.step_counter  = self.step_counter - 1
        self.step_lbl.setText('Step '+f'{self.step_counter}:')
        
        if self.step_counter >= 1:

            self.sequence_str = ''

            self.list_of_events[self.step_counter-1] = ''

            self.sequence[f'{self.step_counter}'][0] = 0
            self.sequence[f'{self.step_counter}'][1] = False
            self.sequence[f'{self.step_counter}'][2] = 0
            self.sequence[f'{self.step_counter}'][3] = 0

        elif self.step_counter == 0:
            self.warning_dlg('Minimum number of events is 1!')
            self.step_counter = 1

        for i in range(self.step_counter):
            self.sequence_str = self.sequence_str + self.list_of_events[i]

        self.full_seq_box.setText('')
        self.full_seq_box.setText(self.sequence_str)
    
    def run_sequence(self):
        """
            After defining the sequence of events, the user
            runs it by restarting the plot (time values start on 0).
            If the user didn't start the plotting, the system will
            start the timer and the data.
        """
        self.restart_plot()
        
        if self.start_stop_btn.text() == 'Start':
            self.timer.start()
            # self.timer.timeout.connect(self.new_data)  
            self.start_stop_btn.setText('Stop')

        self.step_counter = 1
        self.seq_dlg.accept()
        self.general_control['sequence_running'] = True
        
    def run_event(self):
        """
            First, this function verifies whether the wait
            time set by the user is 0 in the actual step. 
            If it is 0, it stops the time and considers 
            that the sequence is finished.
            
            Then, it compares the actual time reading with
            the wait time registered in the sequence

            Then it takes action considering the other values in
            the sequence dictionary. The first one is related to 
            turning the exposure valve on and off, the second is
            the V-VOG sample flow  and the last one is related
            to V-VOG furnace temperature.
        """
        if self.sequence[f'{self.step_counter}'][0] == 0:

            self.timer.stop()
            self.general_control['sequence_running'] = False
            self.start_stop_btn.setText('Start')
            self.warning_dlg('Sequence complete!')

        elif self.time_read >= self.sequence[f'{self.step_counter}'][0]:

            if self.sequence[f'{self.step_counter}'][1]:
                self.arduino.exposure_valve(command='OPEN')
                self.arduino.warning_yellow(command='ON')

            elif not self.sequence[f'{self.step_counter}'][1]:
                self.arduino.exposure_valve(command='CLOSE')
                self.arduino.warning_yellow(command='OFF')
               
            sample_flow_set_point = float(self.sequence[f'{self.step_counter}'][2])/10
            furnace_temp_set_point = float(self.sequence[f'{self.step_counter}'][3])

            self.VOVG_instrument.set_furnace_temp(furnace_temp_set_point)
            time.sleep(0.01)
            self.VOVG_instrument.set_sample_flow(sample_flow_set_point)
            time.sleep(0.01)
            self.step_counter = self.step_counter + 1

    def restart_plot(self):
        self.main_graph.time_data.clear()       
        self.main_graph.thermocouple_1_data.clear()
        self.main_graph.bme_temp_data.clear()
        self.main_graph.bme_press_data.clear()
        self.main_graph.bme_humid_data.clear()
        self.main_graph.mics_data.clear()
        self.main_graph.VOVG_furnace_data.clear()
        self.main_graph.VOVG_sample_flow_data.clear()
        self.main_graph.resistance_data.clear()    

    def clear_plot(self):
        self.last_point = self.main_graph.time_data[-1]
        self.restart_plot()
        self.main_graph.time_data.append(self.last_point)
        
        if self.general_control['controller_connection']:
            self.main_graph.thermocouple_1_data.append(self.arduino.read_thermocouple_1())
            self.main_graph.bme_temp_data.append(self.arduino.read_flow_temp())
            self.main_graph.bme_press_data.append(self.arduino.read_flow_press())
            self.main_graph.bme_humid_data.append(self.arduino.read_flow_humidity())
            self.main_graph.mics_data.append(self.arduino.read_MICS5524())

        if self.general_control['VOVG_connection']:
            self.main_graph.VOVG_furnace_data.append(float(self.VOVG_instrument.read_furnace_temp()))
            self.main_graph.VOVG_sample_flow_data.append(float(self.VOVG_instrument.read_furnace_temp())*10)
        
        if self.general_control['daq6510_connection']:
            self.main_graph.resistance_data.append(float(self.multimeter.read_ch_res(slot='1',
                                                            ch_number='01')))
    
    def warning_dlg(self, message='Warning!'):
        """
            Warning box for error handling.
        """
        self.message = message
        self.warningBox = QMessageBox()
        self.warningBox.setIcon(QMessageBox.Warning)
        self.warningBox.setWindowTitle('Warning')
        self.warningBox.setText(self.message)
        self.warningBox.exec()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main_Interface()
    window.show()
    app.exec()