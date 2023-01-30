from pkg_resources import ResourceManager
import pyvisa
import time

sistema = pyvisa.ResourceManager()

# finds out the address of the instrument
# print(sistema.list_resources())

multimeter = pyvisa.ResourceManager.open_resource(sistema, 'USB0::0x05E6::0x6510::04519791::INSTR')

""" multimeter.write('*IDN?')
print(multimeter.read()) """

# multimeter.write('*RST')
""" reading = multimeter.write('MEAS:VOLT:DC?')
print(multimeter.read()) """
# print(multimeter.query('TRAC:DATA? 1, 1, "defbuffer1", READ'))



#READ ONE CHANNEL
multimeter.write('*RST')
multimeter.write('SENSe:FUNCtion "RESistance", (@101)')
multimeter.write('ROUTe:CLOSe (@101)')
multimeter.write('READ?')
print(multimeter.query('TRAC:DATA? 1, 1, "defbuffer1", READ'))




