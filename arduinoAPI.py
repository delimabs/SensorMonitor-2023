import serial
import time


class Arduino():
    def __init__(self, serial_port='COM5', baud_rate=115200):
        self.connection = serial.Serial(serial_port, baud_rate)
        time.sleep(1)
        self.connection.write(b'<L1H>')

    def warningYellow(self, period=0.1):
        self.connection.write(b'<L2H>')
        time.sleep(period)
        self.connection.write(b'<L2L>')

    def warningRed(self, period=0.1):
        self.connection.write(b'<L3H>')
        time.sleep(period)
        self.connection.write(b'<L3L>')

    def readTemp(self):
        self.connection.write(b'<ST>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def readPress(self):
        self.connection.write(b'<SP>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def readHum(self):
        self.connection.write(b'<SH>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def readRes(self):
        self.connection.write(b'<RR>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def readMQ3(self):
        self.connection.write(b'<RM>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def readLight(self):
        self.connection.write(b'<RL>')
        a = self.connection.readline().decode('ascii')
        return float(a)

    def sendVoltage(self, voltage):
        number = voltage*255/5

        if number >= 100:
            convert = (f'{number:.0f}').encode()

        elif number < 100 and number >= 10:
            convert = ('0'+f'{number:.0f}').encode()

        elif number < 10 and number >= 1:
            convert = ('00'+f'{number:.0f}').encode()

        else:
            convert = '000'.encode()

        self.connection.write(b'<V'+convert+b'>')

    def close(self):
        self.connection.write(b'<L1L>')
        self.connection.close()


if __name__ == '__main__':
    test = Arduino()
    test.warningYellow()