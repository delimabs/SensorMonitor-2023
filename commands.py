import time
import serial


class System_Commands():
    def __init__(self, serial_port='COM5', baud_rate=9600):
        self.connection = serial.Serial(serial_port, baud_rate)
        time.sleep(1)
        
    def read_thermocouple(self):
        self.connection.write(b'<RT>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def close(self):
        self.connection.close()