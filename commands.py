import time
import serial


class System_Commands():
    def __init__(self, serial_port='COM5', baud_rate=9600):
        self.connection = serial.Serial(serial_port, baud_rate)
        time.sleep(5)
        self.connection.write(b'<D1H>')

    def warning_yellow(self, command='OFF'):
        self.command = command
        if self.command == 'ON':
            self.connection.write(b'<D2H>')

        else:
            self.connection.write(b'<D2L>')

    def warning_red(self, command='OFF'):
        self.command = command
        if self.command == 'ON':
            self.connection.write(b'<D2H>')

        else:
            self.connection.write(b'<D2L>')

    def read_thermocouple_1(self):
        self.connection.write(b'<T1>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def read_flow_temp(self):
        self.connection.write(b'<ST>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def read_flow_press(self):
        self.connection.write(b'<SP>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def read_flow_humidity(self):
        self.connection.write(b'<SH>')
        a = self.connection.readline().decode('ascii')
        return float(a)
    
    def read_MICS5524(self):
        self.connection.write(b'<SM>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def close(self):
        self.connection.write(b'<D1L>')
        self.connection.close()
