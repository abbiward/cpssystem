'''
	Commands via PuTTY
	# Connect with device with address ECFE7E1067AC
ATDMLE,ECFE7E1067AC

EXAMPLE USAGE:
>> python testpyserial.py file rswipe g06
This will output several bytes, a time, and total # of lines to the command
It will then output everything else to a file named: file_path/rswipe/g06
	The directory rswipe should be created before trying to write to It

>> python testpyserial.py stdout
This writes everything to stdout

ATDMLE,ECFE7E107107

'''

import serial
import sys
import re
import time
from matplotlib import pyplot as plt
import numpy as np
# import io
# import pylab
#import struct
# sys.path.insert(0, 'C:/Users/Abbi/Documents/research/verma/display')
import util

### ARGUMENT FORMATTING
if (len(sys.argv) < 2) or ((sys.argv[1] != 'stdout') and (sys.argv[1] != 'file')):
	print "Possible options:"
	print "python testpyserial.py file gesture_folder_name file_name time"
	print "python testpyserial.py stdout time"
	print "This program can read data from a serial port (specified in the file). It prints out the first 100 bytes and sends to a file or stdout the next 3600"
	sys.exit(0)

### MAGIC VARIABLES
file_path = '../data/gesture-lib-12-16/raw/'
ser_port =  '/dev/cu.usbserial-AE00FRN7' # 'COM3'
do_live_display = True
SER_BAUDRATE = 115200
NUM_CHANNELS = 8
PLOT_Y_AXIS_LIMIT = 15000

### FILE I/O
folder_gesture = 'NONE'
file_name = 'NONE'
if (sys.argv[1] == 'file'):
	folder_gesture = sys.argv[2]
	file_name = sys.argv[3]
	file_name = file_path + folder_gesture + '/' + file_name
	f = open(file_name, 'w')

### SAMPLE TIME
time_length = int(sys.argv[-1])

### INITIALIZE PlOT
line = [0]*NUM_CHANNELS
ydata = [0]*NUM_CHANNELS
if do_live_display:
	util.setup_plot(plt,ydata,line,ymax=PLOT_Y_AXIS_LIMIT)

### SERIAL PORT SETTINGS
ser=serial.Serial(port=ser_port)
ser.timeout=3
ser.baudrate=SER_BAUDRATE
x = ser.write('ATDMLE,ECFE7E1067AC\r\n') # connect to posterboard
ser.flush()

############################ FUNCTIONS ################################
## functions should be in util.py
######################################################################

if (not ser.isOpen()):
	print "Opening serial communication port..."
	ser.open()

# read and toss the first few lines
for num in range(5):
	s = util.read_serial_line_to_data_list(ser)

start = time.time()
count_lines = 0
curr_time = 0
time_last_update = 0
while curr_time < time_length:
	s = util.read_serial_line_to_data_list(ser)
	count_lines = count_lines + 1
	# Update time
	curr_time = time.time() - start
	# Write data
	if (sys.argv[1] == 'stdout'):
		sys.stdout.write(" ".join(map(str,s)) + '\n')
	elif (sys.argv[1] == 'file'):
		f.write(" ".join(map(str,s)) + '\n')
	if (min(s) < 0) or (max(s) > 20000):
		continue
	# Update plot
	if do_live_display:
		time_last_update = util.update_plot(s, ydata, line, NUM_CHANNELS, time_last_update=time_last_update)

end = time.time()
print "time (s) : ",(end-start)
print "lines: ", count_lines

# Close everything
if (sys.argv[1] == 'file'):
		f.close()
