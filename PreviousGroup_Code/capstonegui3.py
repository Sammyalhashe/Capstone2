
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')
from datetime import datetime
from time import time
import random
import csv
import numpy as np
import struct
import visa


#Find connected instruments

#call the pyVisa resource manager to find a list of connected compatible instruments
#such as Oscilliscopes and multimeters
rm = visa.ResourceManager()
rsrclist = rm.list_resources()
print('The list of connected instruments:', rsrclist)

for i in range(len(rsrclist)):
    if ("ASRL" in str(rsrclist[i])):

        #create a variable for the oscilliscope of interest
        #read and write termination based on the Tektronix 2001c
        scope = rm.open_resource(str(rsrclist[i]),write_termination='\n', read_termination='\n')
        scope.write('DATa:ENCdg ASC')

scope.timeout = 5000 # timeout of 5s

func_gen = rm.open_resource(str(rsrclist[0]),write_termination='\n', read_termination='\n')
func_gen.timeout = 5000

#turn output off
out = func_gen.write("C1:OUTP OFF")


##########################################################################



LARGE_FONT= ("Arial Bold", 16)
REG_FONT= ("Arial", 14)
t_axis=[]
output=[]
samplerate = 10     # In milliseconds
func_id = None

describe = """ This is the Python data acquisition interface.
    Go to 'Obtain Data' to collect and plot data from the connected oscilloscope.
    Go to...
    
    """

def animate(i):
    a.clear()
    a.plot(t_axis, output)

class DataManager(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        #tk.Tk.iconbitmap(self,default='cmaicon.ico')
        tk.Tk.wm_title(self, "CMA Design 2018")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        for F in (StartPage, SetUpPage, SetUpPageTwo, Sweep, PlotPage):
            
            frame = F(container, self)
            
            self.frames[F] = frame
            
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(StartPage)
    
    def show_frame(self, cont):
        
        frame = self.frames[cont]
        frame.tkraise()

##########################################################################
class StartPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
        label = ttk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button = ttk.Button(self, text="Configure Oscilloscope",
                           command=lambda: controller.show_frame(SetUpPage))
        button.pack()
                           
        button2 = ttk.Button(self, text="Configure WF Generator",
                                               command=lambda: controller.show_frame(SetUpPageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Sweep WF Generator",
                     command=lambda: controller.show_frame(Sweep))
        button3.pack()
        
        button4 = ttk.Button(self, text="Obtain Data",
                             command=lambda: controller.show_frame(PlotPage))
        button4.pack()

        description = ttk.Label(self, text=describe, font=REG_FONT)
        description.pack(pady=10,padx=10)
##########################################################################
class SetUpPage(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Configure Oscilloscope", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        
        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage)).pack()
        
        '''
        Set horizontal time scale in seconds
        '''
        global hor_div, hor_scale, v
        #Default
        hor_div = 1
        timescale_d = ttk.Label(self, text="Choose time scale:", font=REG_FONT).pack()
        #Let user input unit for horizontal timescale
        v = tk.StringVar()
        v.set("1")
        b1 = tk.Radiobutton(self, text="s", variable = v, value="1", command=self.setscale('s')).pack()
        b2 = tk.Radiobutton(self, text="ms", variable = v, value="2", command=self.setscale('ms')).pack()
        b3 = tk.Radiobutton(self, text="us", variable = v, value="3", command=self.setscale('us')).pack()
        b4 = tk.Radiobutton(self, text="ns", variable = v, value="4", command=self.setscale('ns')).pack()
        
        #let user input number of units per scale division they would like
        div_d = ttk.Label(self, text="Specify number of divisions:", font=REG_FONT).pack()
        hor_scale = tk.StringVar()
        hor_scale.set("10")         #Default
        enter1 = tk.Entry(self, textvariable=hor_scale).pack()
        
        '''
        Let user set acquisition mode
        '''
        global acq_mode_set
        acq_mode_set = tk.StringVar()
        acq_mode_set.set("PEAKdetect")
        div_d = ttk.Label(self, text="Acquisition Mode:", font=REG_FONT).pack()
        b5 = tk.Radiobutton(self, text="Peakdetect", variable = acq_mode_set, value="PEAKdetect").pack()
        b6 = tk.Radiobutton(self, text="Sample", variable = v, value="SAMple").pack()
        b7 = tk.Radiobutton(self, text="Average", variable = v, value="AVerage").pack()
        
        '''
        Set channel 1- Volts/div scale
        '''
        global vol_div
        vol_div = tk.StringVar()
        vol_div.set("1000")
        vol_d = ttk.Label(self, text="Volts/div [mV]:", font=REG_FONT).pack()
        #vol_div = tk.Scale(self, from_=2, to=5000, length=1000, orient=tk.HORIZONTAL).pack()
        enter3 = tk.Entry(self, textvariable=vol_div).pack()
        
        '''
        Take user input and set channel 1 vertical position
        '''
        global vol_offset
        vol_o = ttk.Label(self, text="Specify a vertical offset:", font=REG_FONT).pack()
        vol_offset = tk.DoubleVar()
        vol_offset.set(0.00)
        vol_offset = tk.Scale(self, from_=-4.0, to=4.0, resolution=0.02, length = 400, orient=tk.HORIZONTAL).pack()
        
        # Apply changes to config
        button2 = ttk.Button(self, text="Apply", command=self.setdiv)
        button2.pack()
    
        '''
        Lock user from making changes to the device
        '''
    
    def setscale(self,hor_unit):
        if hor_unit == 's':
            hor_div = 1
        elif hor_unit == 'ms':
                hor_div = 1000
        elif hor_unit == 'us':
            hor_div = 1000000
        elif hor_unit == 'ns':
            hor_div = 1000000000
        else:
            hor_div = 1

    def setdiv(self):
        scale = hor_scale.get()
        mode = acq_mode_set.get()
        vd = int(vol_div.get())
        offset = vol_offset.get()
        if vd > 5000:
            vol_div.set("5000")
            vd = 5000
        if vd < 2:
            vol_div.set("2")
            vd = 2
        vd /= 10
        scope.write('HORIZONTAL:MAIN:SCALE '+str(scale/hor_div))
        scope.write('ACQUIRE:MODE '+mode)
        scope.write('CH1:VOLTS '+str(vd))
        scope.write('CH1:POSition '+str(offset))

##########################################################################
class SetUpPageTwo(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Configure WF Generator", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()
        
        #asking the user for various parameter inputs,
        #writing to the function generator, and then implementing a delay for 1 second
        global wvtp
        wvtp_d = ttk.Label(self, text="Choose wavetype:", font=REG_FONT).pack()
        wvtp = tk.StringVar()
        wvtp.set("SINE")
        
        b1 = tk.Radiobutton(self, text="Sine", variable = wvtp, value="SINE").pack()
        b2 = tk.Radiobutton(self, text="Square", variable = wvtp, value="SQUARE").pack()
        b3 = tk.Radiobutton(self, text="Ramp", variable = wvtp, value="RAMP").pack()
        b4 = tk.Radiobutton(self, text="Pulse", variable = wvtp, value="PULSE").pack()
        b5 = tk.Radiobutton(self, text="Noise", variable = wvtp, value="NOISE").pack()
        b6 = tk.Radiobutton(self, text="ARB", variable = wvtp, value="ARB").pack()
        b7 = tk.Radiobutton(self, text="DC", variable = wvtp, value="DC").pack()
        
        #Amplitude
        global amp
        amp = tk.StringVar()
        amp.set("1")
        amp_d = ttk.Label(self, text="Choose amplitude [V]:", font=REG_FONT).pack()
        enter1 = tk.Entry(self, textvariable=amp).pack()
        
        #Frequency
        global freq
        freq = tk.StringVar()
        freq.set("100")
        freq_d = ttk.Label(self, text="Choose frequency [Hz]:", font=REG_FONT).pack()
        enter2 = tk.Entry(self, textvariable=freq).pack()
    
        #Phase
        global phse
        phse = tk.StringVar()
        phse.set("0")
        phas_d = ttk.Label(self, text="Choose phase [º]:", font=REG_FONT).pack()
        enter3 = tk.Entry(self, textvariable=phase).pack()
    
        #Amp
        global ofst
        ofst = tk.StringVar()
        ofst.set("0")
        offs_d = ttk.Label(self, text="Choose DC Offset [V]:", font=REG_FONT).pack()
        enter4 = tk.Entry(self, textvariable=amp).pack()
        
 
        global wid, ris, fal
        wid = tk.StringVar()
        ris = tk.StringVar()
        fal = tk.StringVar()
        wid.set("1000")
        ris.set("1000")
        fal.set("1000")
            
        wid_d = ttk.Label(self, text="(Pulse) Width [ms]:", font=REG_FONT).pack()
        enter5 = tk.Entry(self, textvariable=wid).pack()
            
        ris_d = ttk.Label(self, text="(Pulse) Rise [ns]:", font=REG_FONT).pack()
        enter6 = tk.Entry(self, textvariable=ris).pack()
            
        fall_d = ttk.Label(self, text="(Pulse) Fall [ns]:", font=REG_FONT).pack()
        enter7 = tk.Entry(self, textvariable=fal).pack()

        global sym
        sym = tk.StringVar()
        sym.set("100")
            
        sym_d = ttk.Label(self, text="(Ramp) Symmetry [%]:", font=REG_FONT).pack()
        enter8 = tk.Entry(self, textvariable=sym).pack()
        
        global std, mea
        std = tk.StringVar()
        mea = tk.StringVar()
        std.set("0.5")
        mea.set("1.0")

        std_d = ttk.Label(self, text="(Noise Wave) Standard Deviation [V]:", font=REG_FONT).pack()
        enter9 = tk.Entry(self, textvariable=std).pack()
            
        std_d = ttk.Label(self, text="(Noise Wave) Mean [V]:", font=REG_FONT).pack()
        enter10 = tk.Entry(self, textvariable=mea).pack()
        
        global dut
        dut = tk.StringVar()
        dut.set("50")
                
        dut_d = ttk.Label(self, text="(Square Wave) Duty [%]:", font=REG_FONT).pack()
        enter11 = tk.Entry(self, textvariable=dut).pack()
        
        button_app = ttk.Button(self, text="Apply Changes", command=self.apply_commands)
        
        global onoff
        onoff = tk.IntVar()
        onoff.set(0)
        togg_d = ttk.Label(self, text="Toggle Output:", font=REG_FONT).pack()
        b8 = tk.Radiobutton(self, text="On", variable = onoff, value=0, command=self.toggle_output).pack()
        b9 = tk.Radiobutton(self, text="Off", variable = onoff, value=1, command=self.toggle_output).pack()

    def toggle_output():
        #asking the user if they would like to begin outputting
        outpoot = onoff.get()
        func_gen = setup()
        if (outpoot == 1):
            out = func_gen.write("C1:OUTP ON")
        if (outpoot == 0):
            out = func_gen.write("C1:OUTP OFF")
    
    def apply_commands(self):
        wvtpp = wvtp.get()
        ampp = amp.get()
        freqq = freq.get()
        phsee = phse.get()
        ofstt = ofst.get()
        
        
        wave_type = func_gen.write("C1:BSWV WVTP, " + wvtpp)
        time.sleep(1)
        if wvtpp.lower() == 'pulse':
            widd = wid.get()/1000
            width = func_gen.write("C1:BSWV WIDTH, " + str(widd))
            time.sleep(1)
            riss = ris.get()/1000000000
            rise = func_gen.write("C1:BSWV RISE, " + str(riss))
            time.sleep(1)
            falp = fal.get()/1000000000
            fall = func_gen.write("C1:BSWV FALL, " + str(falp))
            time.sleep(1)
        elif wvtpp.lower() == 'ramp':
            symm = sym.get()
            symmetry = func_gen.write("C1:BSWV SYM, " + symm)
            time.sleep(1)
        elif wvtpp.lower() == 'noise':
            stdev = func_gen.write("C1:BSWV STDEV, " + std.get())
            time.sleep(1)
            mean = func_gen.write("C1:BSWV MEAN, " + mea.get())
            time.sleep(1)
        elif wvtpp.lower() == 'square':
            duty = func_gen.write("C1:BSWV DUTY, " + dut.get())
            time.sleep(1)
            
        
        amplitude = func_gen.write("C1:BSWV AMP, " + ampp)
        time.sleep(1)
        
        frequency = func_gen.write("C1:BSWV FRQ, " + freqq)
        time.sleep(1)

        phase = func_gen.write("C1:BSWV PHSE, " + phsee)
        time.sleep(1)

        offset = func_gen.write("C1:BSWV OFST, " + ofstt)
        time.sleep(1)

##########################################################################
class Sweep(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Configure WF Generator", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()
        
        global swp_var
        swp_d = ttk.Label(self, text="Choose variable to sweep:", font=REG_FONT).pack()
        wvtp = tk.StringVar()
        wvtp.set("FRQ")
        
        b1 = tk.Radiobutton(self, text="Frequency", variable = swp_var, value="FRQ").pack()
        b2 = tk.Radiobutton(self, text="Amplitude", variable = swp_var, value="AMP").pack()
        b3 = tk.Radiobutton(self, text="Phase", variable = swp_var, value="PHSE").pack()
        b4 = tk.Radiobutton(self, text="Offset", variable = swp_var, value="OFST").pack()
        
        global min, max, dir, divs, delay
        min = tk.StringVar()
        max = tk.StringVar()
        dir = tk.StringVar()
        divs = tk.StringVar()
        delay = tk.StringVar()
        min.set("0")
        max.set("1")
        dir.set(1)
        divs.set("10")
        delay = ("1")
        
        min_d = ttk.Label(self, text="Minimum [Hz/V/º/V]:", font=REG_FONT).pack()
        enter1 = tk.Entry(self, textvariable=max).pack()
        
        max_d = ttk.Label(self, text="Maximum [Hz/V/º/V]:", font=REG_FONT).pack()
        enter2 = tk.Entry(self, textvariable=max).pack()
        
        div_d = ttk.Label(self, text="Divisions between Max & Min:", font=REG_FONT).pack()
        enter3 = tk.Entry(self, textvariable=divs).pack()
        
        delay_d = ttk.Label(self, text="Sweep Delay [s]:", font=REG_FONT).pack()
        enter4 = tk.Entry(self, textvariable=delay).pack()
        
        dir_d = ttk.Label(self, text="Sweep Direction:", font=REG_FONT).pack()
        b1 = tk.Radiobutton(self, text="Down", variable = onoff, value=0, command=self.toggle_output).pack()
        b2 = tk.Radiobutton(self, text="Up", variable = onoff, value=1, command=self.toggle_output).pack()

        button_swp = ttk.Button(self, text="Start Sweep", command=self.start_sweep)
    def start_sweep(self):
        swp = swp_var.get()
        minimum = int(min.get())
        maximum = int(max.get())
        dell = float(delay.get())
        direction = int(dir.get())
        step = abs(maximum-minimum)/div
        if (direction == 1):
            count = minimum
            while (count <= maximum):
                amplitude = func_gen.write("C1:BSWV " + swp +", " + str(count))
                time.sleep(dell)
                count += step
        if (direction == 0):
            count = maximum
            while (count >= minimum):
                amplitude = func_gen.write("C1:BSWV " + swp +", " + str(count))
                time.sleep(dell)
                count -= step

##########################################################################
class PlotPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Data Acquisition", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()
        global f, a
        f = Figure(figsize=(10,5), dpi=100)
        a = f.add_subplot(111)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        readbutton = ttk.Button(self, text="Start Data Collection", command=self.read_data)
        readbutton.pack(pady=5)

        stopbutton = ttk.Button(self, text="Stop Data Collection",
                     command=self.stop_data)
        stopbutton.pack(pady=5)
        
        resetbutton = ttk.Button(self, text="Clear Data",
                                command=self.clr_data)
        resetbutton.pack(pady=5)

        save_plot = ttk.Button(self, text="Save Plot as PNG", command=self.savegraph)
        save_plot.pack(pady=5)

        save_csv = ttk.Button(self, text="Save Data as CSV", command=self.writetocsv)
        save_csv.pack(pady=5)

    def read_data(self):
        del t_axis[:]
        del output[:]
        print("go")
        self.update_plot()
    
    def update_plot(self):
        global func_id
        
        ###########
        #check the acquisition paramters
        param_acq = scope.query('ACQUIRE:MODE?', delay=0.25)

        #check the state of the oscilliscope
        state = scope.query('ACQuire:STATE?', delay =0.25)

        #check parameters for ch1
        param_ch1 = scope.query('CH1?', delay=0.25)

        #check channel 1 volts/div
        volts_ch1 = scope.query('CH1:VOLTS?', delay=0.25)

        #split the volt division around the E character
        volt_scale = volts_ch1.split('E')


        #check horizontal parameters
        param_hor_ch1 = scope.query('HORizontal?', delay=0.25)

        #getting horizontal time scale data
        hor_scale_data = (param_hor_ch1.split(';')[2]).split('E')

        #check measurement parameters
        param_meas = scope.query('MEASUrement?', delay=0.25)

        #set the data source to be Binary
        scope.write('DATA:SOURCE CH1')
        scope.write('DATa:ENCdg RIBinary')
        scope.write('DATa:Width 1')
        scope.write('DATa:START 1')
        scope.write('DATa:STOP 2500')
        
        #get the waveform
        print(scope.query('WFMPRE:ENCDG?'))
        waveform_data = scope.query('WFMpre?', delay=0.25)

        waveform = scope.query_binary_values('CURV?', datatype = 'c')
        
        x = len(waveform)
        data = np.zeros(x)
        
        for i in range(x):
            data[i] = int.from_bytes(waveform[i], byteorder='big', signed=True)
        
        hor_vector = np.arange(0,10*(float(hor_scale_data[0])*10**int(hor_scale_data[1])),float(hor_scale_data[0])*10**int(hor_scale_data[1])/250)
        

        #divide data by 25 to set vertical division value to 1
        output =  data*(float(volt_scale[0])*10**(int(volt_scale[1])))/25
        t_axis = hor_vector
        ###########

        func_id = self.after(samplerate, self.update_plot)
    
    def stop_data(self):
        global func_id
        self.after_cancel(func_id)

    def writetocsv(self,x=output,t=t_axis):
        name = "Data_taken_on_" + str(datetime.now()) + ".csv"
        line_list = name.split(':')
        loc = '-'.join(line_list[:-1])
        with open(loc, mode='w') as csv_file:
            fieldnames = ['time', 'output']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(len(x)):
                writer.writerow({'time': str(t[i]), 'output': str(x[i])})

    def savegraph(self):
        name = "Data_taken_on_" + str(datetime.now()) + ".png"
        line_list = name.split(':')
        new_name = '-'.join(line_list[:-1])
        f.savefig(new_name, bbox_inches='tight')

    def clr_data(self):
        del t_axis[:]
        del output[:]
##########################################################################



app = DataManager()
ani = animation.FuncAnimation(f,animate, interval=1000)
app.mainloop()