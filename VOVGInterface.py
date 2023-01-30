import minimalmodbus

class VOVG_module():
    def __init__(self, serial_port='COM5', baud_rate=9600, furnace_addr=3, sample_flow_addr=4):
        
        self.serial_port = serial_port
        
        self.baud_rate = baud_rate
        
        self.furnace_controller = minimalmodbus.Instrument(self.serial_port, furnace_addr)
        self.sample_flow_controller = minimalmodbus.Instrument(self.serial_port, sample_flow_addr)

        self.furnace_controller.serial.baudrate = self.baud_rate
        self.furnace_controller.serial.timeout  = 1

        self.sample_flow_controller.serial.baudrate = self.baud_rate
        self.sample_flow_controller.serial.timeout  = 1
    
    def read_furnace_temp(self):
        # read address 1, with 1 decimal point
        n =  self.furnace_controller.read_long(32770)

        if n >= 2 ** (32):
            raise ValueError("Number n is longer than prescribed parameters allows")
        
        sgn_len = 1
        exp_len = 8
        mant_len = 23

        sign = (n & (2 ** sgn_len - 1) * (2 ** (exp_len + mant_len))) >> (exp_len + mant_len)
        exponent_raw = (n & ((2 ** exp_len - 1) * (2 ** mant_len))) >> mant_len
        mantissa = n & (2 ** mant_len - 1)

        sign_mult = 1

        if sign == 1:
            sign_mult = -1

        if exponent_raw == 2 ** exp_len - 1:  # Could be Inf or NaN
            if mantissa == 2 ** mant_len - 1:
                return float('nan')  # NaN

            return sign_mult * float('inf')  # Inf

        exponent = exponent_raw - (2 ** (exp_len - 1) - 1)

        if exponent_raw == 0:
            mant_mult = 0  # Gradual Underflow
        else:
            mant_mult = 1

        for b in range(mant_len - 1, -1, -1):
            if mantissa & (2 ** b):
                mant_mult += 1 / (2 ** (mant_len - b))

        return sign_mult * (2 ** exponent) * mant_mult

    def read_sample_flow(self):
        # read address 1, with 1 decimal point
        a = self.sample_flow_controller.read_register(1, 1)
        return float(a)
    
    def set_furnace_SP1(self, value=25):
        # write in address 25 the entered value. Default is 25
        self.value=value
        self.furnace_controller.write_register(24, self.value, 1)

    def set_furnace_SP2():
        print('not supported yet')
    
    def set_sample_flow_SP1(self, value=0):
        self.value=value
        self.sample_flow_controller.write_register(24, self.value, 1)

    def ieee_754_conversion(n, sgn_len=1, exp_len=8, mant_len=23):
        """
        I am using the conversion function from AlexEshoo. 
        
        Available here:
        https://gist.github.com/AlexEshoo/d3edc53129ed010b0a5b693b88c7e0b5
        
        Converts an arbitrary precision Floating Point number.
        Note: Since the calculations made by python inherently use floats, the accuracy is poor at high precision.
        :param n: An unsigned integer of length `sgn_len` + `exp_len` + `mant_len` to be decoded as a float
        :param sgn_len: number of sign bits
        :param exp_len: number of exponent bits
        :param mant_len: number of mantissa bits
        :return: IEEE 754 Floating Point representation of the number `n`
        """
        if n >= 2 ** (sgn_len + exp_len + mant_len):
            raise ValueError("Number n is longer than prescribed parameters allows")

        sign = (n & (2 ** sgn_len - 1) * (2 ** (exp_len + mant_len))) >> (exp_len + mant_len)
        exponent_raw = (n & ((2 ** exp_len - 1) * (2 ** mant_len))) >> mant_len
        mantissa = n & (2 ** mant_len - 1)

        sign_mult = 1
        if sign == 1:
            sign_mult = -1

        if exponent_raw == 2 ** exp_len - 1:  # Could be Inf or NaN
            if mantissa == 2 ** mant_len - 1:
                return float('nan')  # NaN

            return sign_mult * float('inf')  # Inf

        exponent = exponent_raw - (2 ** (exp_len - 1) - 1)

        if exponent_raw == 0:
            mant_mult = 0  # Gradual Underflow
        else:
            mant_mult = 1

        for b in range(mant_len - 1, -1, -1):
            if mantissa & (2 ** b):
                mant_mult += 1 / (2 ** (mant_len - b))

        return sign_mult * (2 ** exponent) * mant_mult