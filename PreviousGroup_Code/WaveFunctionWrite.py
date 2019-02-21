#!/usr/bin/env python3
import time
import visa
import math

def setup():
    '''
    Find connected instruments
    '''
    #call the pyVisa resource manager to find a list of connected compatible instruments
    #such as Oscilliscopes, function generators and multimeters
    rm = visa.ResourceManager()
    x = rm.list_resources()
    
    #print('The list of connected instruments:', x)
    
    #create a variable for the function generator of interest
    #read and write termination based on the SDG805
    #setting the read/write command timeout to 5 seconds
    for i in range(len(x)):
        if ("SDG" in str(x[i])):
            func_gen = rm.open_resource(str(x[i]),write_termination='\n', read_termination='\n')
            func_gen.timeout = 5000
            return (func_gen)



def settings():
#asking the user for various parameter inputs,
#writing to the function generator, and then implementing a delay for 1 second
#if commands are written too quickly in succession they will not be applied
    func_gen = setup()
    wvtp = str(input("Wavetype? ie SINE, SQUARE, RAMP, PULSE, NOISE, ARB, DC\n"))
    if (wvtp.lower() == 'sine' or wvtp.lower() == 'square' or wvtp.lower() == 'ramp' or wvtp.lower() == 'pulse' or wvtp.lower() == 'noise' or wvtp.lower() == 'arb' or wvtp.lower() == 'dc'):
        wave_type = func_gen.write("C1:BSWV WVTP, " + wvtp)
        time.sleep(1)
    
    amp = str(input("Amplitude in Volts?\n"))
    amplitude = func_gen.write("C1:BSWV AMP, " + amp)
    time.sleep(1)
    
    frq = str(input("Frequency in Hz?\n"))
    frequency = func_gen.write("C1:BSWV FRQ, " + frq)
    time.sleep(1)
    
    phse = str(input("Phase in Degrees?\n"))
    phase = func_gen.write("C1:BSWV PHSE, " + phse)
    time.sleep(1)
    
    ofst = str(input("DC Offset in Volts?\n"))
    offset = func_gen.write("C1:BSWV OFST, " + ofst)
    time.sleep(1)
    
    if (wvtp.lower() == 'pulse'):
        wid = int(input("Width in milliseconds?\n"))
        wid = wid/1000
        width = func_gen.write("C1:BSWV WIDTH, " + str(wid))
        time.sleep(1)
        ris = int(input("Rise in nanoseconds?\n"))
        ris = ris/1000000000
        rise = func_gen.write("C1:BSWV RISE, " + str(ris))
        time.sleep(1)
        fal = int(input("Fall in nanoseconds?\n"))
        fal = fal/1000000000
        fall = func_gen.write("C1:BSWV FALL, " + str(fal))
        time.sleep(1)
        
    if (wvtp.lower() == 'ramp'):
        sym = str(input("Symmetry in percentage?\n"))
        symmetry = func_gen.write("C1:BSWV SYM, " + sym)
        time.sleep(1)
    
    if (wvtp.lower() == 'noise'):
        std = str(input("Standard Deviation in Volts?\n"))
        stdev = func_gen.write("C1:BSWV STDEV, " + std)
        time.sleep(1)
        mea = str(input("Mean in Volts?\n"))
        mean = func_gen.write("C1:BSWV MEAN, " + mea)
        time.sleep(1)
    
    if (wvtp.lower() == 'square'):
        dut = str(input("Duty in percentage?\n"))
        duty = func_gen.write("C1:BSWV DUTY, " + dut)
        time.sleep(1)







def toggle_output():
#asking the user if they would like to begin outputting
    func_gen = setup()
    outpoot = int(input("1 for on, 0 for off\n"))
    if (outpoot == 1):
        out = func_gen.write("C1:OUTP ON")
    if (outpoot == 0):    
        out = func_gen.write("C1:OUTP OFF")


def sweep():
#asking user if they would like to utilize a sweep
#frequency, amplitude, phase, and offset are sweepable parameters
#only one parameter can be swept at a time
#requires user input on the min and max parameter for each 
#user inputs delay for how long each step is held for
#steps are determined by the user inputted number of divisions between
#the min and max of each parameter  
    
    func_gen = setup()
    swp_var = input("What would you like to sweep? ie frequency, amplitude, phase, offset\n")

    if (swp_var.lower() == 'frequency'):
        min_freq = int(input("Min frequency of sweep in Hz?\n"))
        max_freq = int(input("Max frequency of sweep in Hz?\n"))
        direction = int(input("Sweep direction? 1 for up, 0 for down\n"))
        div = int(input("How many divisions between the min and max frequency?\n"))
        delay = int(input("How long would you like each frequency to be held for in seconds?\n"))
        step = abs(max_freq-min_freq)/div
        if (direction == 1):
            count_freq = min_freq
            while (count_freq <= max_freq):
                frequency = func_gen.write("C1:BSWV FRQ, " + str(count_freq))
                time.sleep(delay)
                count_freq = count_freq + step
        if (direction == 0):
            count_freq = max_freq
            while (count_freq >= min_freq):
                frequency = func_gen.write("C1:BSWV FRQ, " + str(count_freq))
                time.sleep(delay)
                count_freq = count_freq - step


    if (swp_var.lower() == 'amplitude'):
        min_amp = int(input("Min amplitude of sweep in Volts?\n"))
        max_amp = int(input("Max amplitude of sweep in Volts?\n"))
        direction = int(input("Sweep direction? 1 for up, 0 for down\n"))
        div = int(input("How many divisions between the min and max amplitude?\n"))
        delay = int(input("How long would you like each amplitude to be held for in seconds?\n"))
        step = abs(max_amp-min_amp)/div
        if (direction == 1):
            count_amp = min_amp
            while (count_amp <= max_amp):
                amplitude = func_gen.write("C1:BSWV AMP, " + str(count_amp))
                time.sleep(delay)
                count_amp = count_amp + step
        if (direction == 0):
            count_amp = max_amp
            while (count_amp >= min_amp):
                amplitude = func_gen.write("C1:BSWV AMP, " + str(count_amp))
                time.sleep(delay)
                count_amp = count_amp - step



    if (swp_var.lower() == 'phase'):
        min_phase = int(input("Min phase of sweep in Degrees?\n"))
        max_phase = int(input("Max phase of sweep in Degrees?\n"))
        direction = int(input("Sweep direction? 1 for up, 0 for down\n"))
        div = int(input("How many divisions between the min and max phase?\n"))
        delay = int(input("How long would you like each phase to be held for in seconds?\n"))
        step = abs(max_phase-min_phase)/div
        if (direction == 1):
            count_phase = min_phase
            while (count_phase <= max_phase):
                phase = func_gen.write("C1:BSWV PHSE, " + str(count_phase))
                time.sleep(delay)
                count_phase = count_phase + step
        if (direction == 0):
            count_phase = max_phase
            while (count_phase >= min_phase):
                phase = func_gen.write("C1:BSWV PHSE, " + str(count_phase))
                time.sleep(delay)
                count_phase = count_phase - step
            
    if (swp_var.lower() == 'offset'):
        min_offset = int(input("Min offset of sweep in Volts?\n"))
        max_offset = int(input("Max offset of sweep in Volts?\n"))
        direction = int(input("Sweep direction? 1 for up, 0 for down\n"))
        div = int(input("How many divisions between the min and max offset?\n"))
        delay = int(input("How long would you like each offset to be held for in seconds?\n"))
        step = abs(max_offset-min_offset)/div
        if (direction == 1):
            count_offset = min_offset
            while (count_offset <= max_offset):
                offset = func_gen.write("C1:BSWV OFST, " + str(count_offset))
                time.sleep(delay)
                count_offset = count_offset + step
        if (direction == 0):
            count_offset = max_offset
            while (count_offset >= min_offset):
                offset = func_gen.write("C1:BSWV OFST, " + str(count_offset))
                time.sleep(delay)
                count_offset = count_offset - step



    
    
    
    
    
    
    
    
    
    
    
    
