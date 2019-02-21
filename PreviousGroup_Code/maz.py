#!/usr/bin/env python3
#import necessary libraries
import visa
import matplotlib.pyplot as plt
import numpy as np
import time
import struct

'''
Function: Find connected instruments
input: nill
output: return scope variable
'''

def find_scope():
#call the pyVisa resource manager to find a list of connected compatible instruments
#such as Oscilliscopes and multimeters
    rm = visa.ResourceManager()
    x = rm.list_resources()
    #print('The list of connected instruments:', x)
    
    #create a variable for the oscilliscope of interest
    #read and write termination based on the Tektronix 2001c
    for i in range(len(x)):
        if ("ASRL" in str(x[i])):
            scope = rm.open_resource(str(x[i]),write_termination='\n', read_termination='\n')
            scope.timeout = 5000 # timeout of 5s
            #scope.baud_rate = 9600
            #set Data encoding to ASIIC
            scope.write('DATa:ENCdg ASC')
            return scope

'''
Function: Write scope commands
input: Command
output: none
'''
#Inputs are- time scale, acquisition mode, volt div, volt offset
def scope_write(command):
    scope = find_scope()
    #Perform scope time_scale write function
    if command.lower() == 'time scale':
        #Let user input unit for horizontal timescale
        hor_unit = str(input('What units do you want the horizontal scale to be in? s, ms, us are the options\n'))
        #check the unit chosen for horizontal timescale is valid
        if hor_unit.lower() == 's':
            hor_div = 1
        elif hor_unit.lower() == 'ms':
            hor_div = 1000
        elif hor_unit.lower() == 'us':
            hor_div = 1000000
        elif hor_unit.lower() == 'ns':
            hor_div = 1000000000      
        else:
            hor_div = 1
    
        #let user input number of units per scale division they would like    
        hor_scale = float(input('How many '+hor_unit+' per horizontal division does the user desire?\n'))
    
        #write the selected Horizontal timescale into the device
        scope.write('HORIZONTAL:MAIN:SCALE '+str(hor_scale/hor_div))
    
    elif command.lower() == 'acquisition mode':
        acq_mode_set = str(input('Select Acquisition mode from the following options: Peakdetect, sample, and average'))
        acq_mode_set = acq_mode_set.upper()

        #set the acquisition mode to PEAKdetect (Options are also SAMple, AVerage)
        scope.write('ACQUIRE:MODE '+acq_mode_set)
    
    elif command.lower() == 'volt div':
        #request the Volts/division from the user
        vol_div = float(input('Input the desired volts/division for data display:\n(Min: 0.002V/div (2mV) Max: 5V/div -- Displayed area is 8x selected V/div)\n'))

        #loop while the user selects outputs out of range
        while vol_div < 0.002 or vol_div > 5:
            vol_div = float(input('Please input the desired Volts/div again (Min: 0.002V/div (2mV) Max: 5V/div):\n'))

        #write to the scope to set the desired voltage
        scope.write('CH1:VOLTS '+str(vol_div))
    
    elif command.lower() == 'volt offset':
        vol_offset = float(input('Please input any desired offset (Range is +- 4 in intervals of 0.02):\n'))

        #loop while the user selects offset out of range
        while vol_offset < -4 or vol_offset > 4:
                vol_offset = float(input('Please input the desiredoffset (Min: -4 Max: +4):\n'))

        #write to the scope to set the desired voltage offset
        scope.write('CH1:POSition '+str(vol_offset))
    
    #if none of the inputs match the ones in the if statement, don't do anything    
    else:
        return
    
    return

'''
Function: Write scope commands
input: scope
output: 2500 data points from oscilliscope in units of volts and time
'''
        
def data_read():
    strt = time.time()
    scope = find_scope()
    #Force trigger oscilliscope
    scope.write('TRIGger FORCe')
        
    #check the acquisition paramters
    param_acq = scope.query('ACQUIRE:MODE?')
    
    
    #check the state of the oscilliscope
    state = scope.query('ACQuire:STATE?')
    
    #check parameters for ch1
    param_ch1 = scope.query('CH1?')
    
    #check channel 1 volts/div
    volts_ch1 = scope.query('CH1:VOLTS?')
    
    #split the volt division around the E character
    volt_scale = volts_ch1.split('E')
    
    
    #check horizontal parameters
    param_hor_ch1 = scope.query('HORizontal?')
    
    #getting horizontal time scale data
    hor_scale_data = (param_hor_ch1.split(';')[2]).split('E')
    
    #check measurement parameters
    param_meas = scope.query('MEASUrement?')
    
    #set the data source to be Binary
    scope.write('DATA:SOURCE CH1')
    scope.write('DATa:ENCdg RIBinary')
    scope.write('DATa:Width 1')
    scope.write('DATa:START 1')
    scope.write('DATa:STOP 2500')
    
    #get the waveform
    print(scope.query('WFMPRE:ENCDG?'))
    waveform_data = scope.query('WFMpre?')
    
    waveform = scope.query_binary_values('CURV?', datatype = 'c')
    stop = time.time()
    print(stop-strt)
    #check scope status
    #print(scope.query('BUSY?'))
    x = len(waveform)
    data = np.zeros(x)
    
    #loop and change binary bytes data to integers
    for i in range(x):
        data[i] = int.from_bytes(waveform[i], byteorder='big', signed=True)
    
    #horizontal time vector
    hor_vector = np.arange(0,10*(float(hor_scale_data[0])*10**int(hor_scale_data[1])),float(hor_scale_data[0])*10**int(hor_scale_data[1])/250)
    
    #divide data by 25 to set vertical division value to 1   
    plt.plot(hor_vector, data*(float(volt_scale[0])*10**(int(volt_scale[1])))/25)
    
    #scale the data based on the horizontal scale
    scaled_data = data*(float(volt_scale[0])*10**(int(volt_scale[1])))/25
    
    #plt.xticks(np.arange(min(x), max(x)+1, 1.0))
    #plt.yticks(np.arange(-4*(float(volt_scale[0])/10**(int(volt_scale[1]))), 4*(float(volt_scale[0])/10**(int(volt_scale[1]))),(float(volt_scale[0])/10**(int(volt_scale[1])))))
    plt.xlabel('Time (s)')
    plt.ylabel('Output Voltage (V)')
    plt.title('Oscilliscope output')
    plt.show()
    
    return hor_vector, scaled_data