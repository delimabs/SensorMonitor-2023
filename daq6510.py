from pkg_resources import ResourceManager
import pyvisa


class DAQ6510():
    def __init__(self):
        self.visa = pyvisa.ResourceManager()
        self.instrument = pyvisa.ResourceManager.open_resource(self.visa, 'USB0::0x05E6::0x6510::04519791::INSTR')

    def find_instruments(self):
        return self.visa.list_resources()

    def beep(self, frequency='1000'):
        self.instrument.write('*RST')
        self.instrument.write('SYSTem:BEEPer '+frequency+', 1')
        
    def find_instrument_addr(self):
        self.instrument.write('*RST')
        self.instrument = self.instrument.write('*IDN?')
        return self.instrument
        
    def measure_voltage_front(self):
        self.instrument.write('*RST')
        self.instrument.write('MEAS:VOLT:DC?')
        reading = self.instrument.query('TRAC:DATA? 1, 1, "defbuffer1", READ')
        return reading

    def measure_resistance_front(self):
        self.instrument.write('*RST')
        self.instrument.write('MEAS:RES?')
        reading = self.instrument.query('TRAC:DATA? 1, 1, "defbuffer1", READ')
        return reading

    def read_ch_1(self):
        self.instrument.write(':*RST')
        self.instrument.write(':SENSe:FUNCtion "RESistance", (@101)')
        self.instrument.write(':ROUTe:CHANnel:MULTiple:CLOSe (@101)')
        self.instrument.write(':SENSe:COUNt 5')
        self.instrument.write('TRAC:TRIG')
        self.instrument.write(':ROUTe:SCAN:CREate (@101)')
        self.instrument.write(':INIT')
        self.instrument.write(':*WAI')
        results = self.instrument.query(':TRAC:DATA? 1, 1, "defbuffer1", READ,').split(',')
        return results[0]

    def read_mult_res(self, slot='1', ch_numbers=['01', '02', '11', '12']):
        self.ch_str_list = '@'

        for index, element in enumerate(ch_numbers):
            
            if index < len(ch_numbers)-1:
                self.ch_str_list = self.ch_str_list+slot+element+', '

            elif index == len(ch_numbers)-1:
                self.ch_str_list = self.ch_str_list+slot+element

        self.instrument.write('*RST')
        self.instrument.write('SENSe:FUNCtion "RESistance", ('+self.ch_str_list+')')
        self.instrument.write('ROUTe:CHANnel:MULTiple:CLOSe ('+self.ch_str_list+')')
        self.instrument.write('SENSe:COUNt 5')
        self.instrument.write('TRAC:TRIG')
        self.instrument.write('ROUTe:SCAN:CREate ('+self.ch_str_list+')')
        self.instrument.write('INIT')
        self.instrument.write('*WAI')
        readings = self.instrument.query(f'TRAC:DATA? 1, {len(ch_numbers)}, "defbuffer1", READ,').split(',')
        resistance_results = []
        
        for element in readings:
            resistance_results.append(float(element))
        
        return resistance_results
