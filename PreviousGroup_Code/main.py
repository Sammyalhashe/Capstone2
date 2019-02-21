#!/usr/bin/env python3
import WaveFunctionWrite as WFW
import maz as MAZ
import save

counter = 0
loop = True
while (loop == True):
   method = int(input("What would you like to do?\nToggle Output: 0\nChange Wave Function Generator Settings: 1\nPerform Sweep: 2\nRead Scope Data: 3\nChange Scope Settings: 4\nEnd: 5\n"))
   
   if (method == 0):
       WFW.toggle_output()
   
   if (method == 1):
       WFW.settings()

   if (method == 2):
       WFW.sweep()

   if (method == 3):
       t, x = MAZ.data_read()
       save_data = int(input("Would you like to save your data? 1 for yes, 0 for no\n"))
       
       if (save_data == 1):
           loc = str(input("Input save directory for file\n"))
           save.writetocsv(x,t,loc, counter)
           counter += 1
       
   if (method == 4):
       command = int(input("What would you like to do?\nChange horizontal time scale: 0\nChange vertical scale (volts/div): 1\nChange voltage offset: 2\nChange acquistion mode: 3\n"))
       if (command == 0):
           MAZ.scope_write('time scale')
       if (command == 1):
           MAZ.scope_write('volt div')
       if (command == 2):
           MAZ.scope_write('volt offset')
       if (command == 3):
           MAZ.scope_write('acquistion mode')

   if (method == 5):
       loop = False

