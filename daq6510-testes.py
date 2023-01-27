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

#EXAMPLES

#1
# reading = multimeter.write('MEAS:VOLT:DC?')
#2
# reading = multimeter.write('MEAS:CURR?')
#3
# reading = multimeter.write('MEAS:RES?')
#4
# multimeter.write('MEAS:VOLT:DC?')
#5
# multimeter.write('MEAS:RES?')
#6
# multimeter.write('READ:VOLT')
#7
# multimeter.write(':SYSTem:BEEPer 300, 1')


"""
#READ ONE CHANNEL
multimeter.write('*RST')
multimeter.write('SENSe:FUNCtion "RESistance", (@111)')
multimeter.write('ROUTe:CLOSe (@111)')
multimeter.write('READ?')
print(multimeter.query('TRAC:DATA? 1, 1, "defbuffer1", READ'))
"""



### READ FOUR CHANNELS
multimeter.write('*RST')
multimeter.write('SENSe:FUNCtion "RESistance", (@101, 102, 111, 112)')
multimeter.write('ROUTe:CHANnel:MULTiple:CLOSe (@101, 102, 111, 112)')
multimeter.write('SENSe:COUNt 5')
multimeter.write('TRAC:TRIG')
multimeter.write('ROUTe:SCAN:CREate (@101, 102, 111, 112)')
multimeter.write('INIT')
multimeter.write('*WAI')
# print(multimeter.query('TRAC:DATA? 1, 4, "defbuffer1", READ,'))
# print(multimeter.write('TRAC:ACT?'))

results = multimeter.query('TRAC:DATA? 1, 4, "defbuffer1", READ,').split(',')

print(results)
test = []

for element in results:
    test.append(float(element))

    
print(test)

