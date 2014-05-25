import serial
import sys
import re
import time
from matplotlib import pyplot as plt
import numpy as np
import io
import pylab
# import win32api
# import win32con
import heapq
import math
# import compute_location
# import compute_location_ratio
# import compute_delta_location
import logging


## SERIAL DATA ###

def read_serial_line(ser):
	eol = b'\r'
	leneol = len(eol)
	line = bytearray()
	while True:
		c = ser.read(1)
		if c:
			line += c
			if line[-leneol:] == eol:
				break
	return bytes(line)

def read_bluetooth_line_old(ser):
	s = read_serial_line(ser)
	s = re.sub('\x00', ' ', s)
	s = re.sub('\r', '\n', s)
	return s

def read_serial_line_to_data_list(ser):
	eol = b'\xff\xff'
	leneol = len(eol)
	line = bytearray()
	data = []
	while True:
		c = ser.read(1)
		#print "BYTE: ", hex(ord(c))
		data.append(ord(c))
		if c:
			line += c
			if line[-leneol:] == eol:
				break

	data_final = [0]*8
	if (len(data[:-2]) != 16):
		'''
		if (len(data[:-2]) < 16):
			logging.warning('data is too short {0} {1}'.format(len(data[:-2]), len(line)))
			print [hex(x) for x in data]
		else:
			logging.warning('data is too long %d' % len(data[:-2]))
			print [hex(x) for x in data]
		'''
		return data_final

	x = False
	for item in range(8):
		data_final[item] = (data[2*item]<<8) + (data[2*item+1])
		if data_final[item] == 0:
			print "ISZERO: ", data[2*item], data[2*item+1]
			x = True
	if x:
		print "DATAFINAL:", data_final
	return data_final


### PLOT
def update_plot(data, ydata, line, num_channels=8, time_last_update=0):
	if (len(data) == num_channels):
		for val in range(num_channels):
			ydata[val].append(data[val])
			del ydata[val][0]
			line[val].set_xdata(np.arange(len(ydata[val])))

	# update the ydata for each channel
	for val in range(num_channels):
		line[val].set_ydata(ydata[val])

	if (time.clock()-time_last_update) > .001:
		plt.draw() # update the plot
		return time.clock()
	return time_last_update

def setup_plot(plt,ydata,line,ymax=20000,num_channels=8):
	plt.ion() # set plot to animated
	# initialize the data for each channel
	for val in range(num_channels):
		ydata[val] = [0]*100
	ax1=plt.axes()
	for val in range(num_channels-1):
		line[val], = plt.plot(ydata[val])
	line[num_channels-1], = plt.plot(ydata[num_channels-1],linestyle='--')
	plt.ylim([0,ymax])
	plt.ylabel('ADC output')
	plt.xlabel('time')
	plt.legend(['Ch1', 'Ch2', 'Ch3', 'Ch4', 'Ch5', 'Ch6', 'Ch7', 'Ch8'], loc='upper left')


## FILTERING, ADC-DF CONVERSION

def print_list(list_given, fileobj):
	fileobj.write('\t'.join(map(str,list_given)))
	fileobj.write('\n')

def get_printable_list_floats(list_given):
	output = []
	for item in list_given:
		output.append('%(val).3f' % {'val': item})
	return " ".join(output)

# calibrate
# Trackpad/touchpad: factor=16
def calibrate(ser, num_channels=8, f_LO=4650000, num_calibration_attempts=0, factor=2):
	NUM_CALIBRATION_SAMPLES = 30
	MAX_CALIBRATION_ATTEMPTS = 3
	MAX_BAD_SAMPLES = 6
	if (num_calibration_attempts >= MAX_CALIBRATION_ATTEMPTS):
		print "FAILED TO CALIBRATE"
		sys.exit(0)

	# base_value = [0]*num_channels
	base_value = [[] for x in range(num_channels)]
	num_samples_used = 0
	num_bad_samples = 0
	for i in range(NUM_CALIBRATION_SAMPLES):
		line = read_serial_line_to_data_list(ser)
		if (len(line) != num_channels) or (min(line) < 800) or (max(line) > 20000):
			print i, " UH OH : ", line
			num_bad_samples = num_bad_samples + 1
			if (num_bad_samples > MAX_BAD_SAMPLES):
				print "TRYING AGAIN"
				return calibrate(ser,num_calibration_attempts=num_calibration_attempts+1)
			continue
		print i, " OKAY: ", line
		for j in range(num_channels):
			#base_value[j] = base_value[j] + int(line[j])
			base_value[j].append(int(line[j]))
		num_samples_used = num_samples_used + 1

	base_value_sorted = []
	for i in range(num_channels):
		base_value_sorted.append(sorted(base_value[i]))
		listlen = len(base_value_sorted[i])
		base_value_sorted[i] = base_value_sorted[i][int(.2*listlen):int(.8*listlen)]

	x = np.array(base_value_sorted)
	x = np.mean(x, axis=1)

	mean_value = [0]*num_channels
	for i in range(num_channels):
		mean_value[i] = x[i]

	freq_ctr = [0]*num_channels
	for i in range(num_channels):
		# freq_ctr[i] = 2*f_LO/mean_value[i]	## CHANGE HERE
		freq_ctr[i] = factor*f_LO/mean_value[i]

	print "BASE: ", mean_value
	print freq_ctr

	return freq_ctr

# convert
# Note: trackpad/touchpad factor=16
def convert_ADC_to_deltaf(freq_ctr, data, num_channels=8, f_LO=4650000, factor=2):
	data = map(int, data)
	freq_delta = [0]*num_channels
	try:
		for i in range(num_channels):
			#freq_delta[i] = (2*f_LO/data[i]) - freq_ctr[i] ## CHANGE HERE
			freq_delta[i] = (factor*f_LO/data[i]) - freq_ctr[i]
		# print_list(freq_delta, sys.stdout)
		return freq_delta
	except ZeroDivisionError:
		print "ERROR: ", data
		return [0]*num_channels

## DISPLAY ####
def get_screen_size():
	return (1440,900)
	# screen_params = win32api.GetSystemMetrics
	# screen_width = screen_params(0)
	# screen_height = screen_params(1)
	# return(screen_width, screen_height)


def get_cursor_position_deltaf(data, screen_width, screen_height):
	proportions = [1./8, 3./8, 5./8, 7./8]
	hor_positions = [screen_width*item for item in proportions]
	vert_positions = [screen_height*item for item in proportions]
	# vert_positions = vert_positions.reverse()

	# ASSUMES data is list of 8 channel values: 0-3 = horizontal, 4-7 = vertical
	hor = data[0:4]
	vert = data[4:]
	deltaf_threshold = 60

	if (max(data) > 1000):
		print data
	# threshold proximity
	if ((max(hor) < deltaf_threshold) or max(vert) < deltaf_threshold):
		print "LOW: ", data
		return (-1,-1)
	#print vals

	# test 1: just wherever the peak is, return that position
	x0 = hor_positions[hor.index(max(hor))]
	y0 = vert_positions[vert.index(max(vert))]
	# NOTE: y positions may be reversed because channel numbers are strange
	return (int(x0), int(y0))


def get_fine_position_simple(channel_data, positions_px):
	# ASSUMPTIONS: channels are already neighbors
	# given maxHor or maxVert
	pos = [x[0] for x in channel_data]
	maxVal = [x[1] for x in channel_data]
	posPx = [positions_px[x] for x in pos]

	# the channels are neighbors... w00t
	c = 10
	# equation: [(x2-x1)/ln(c*c)] * ln(c*r2/r1) + x1
	try:
		c1 = 2*math.log(c)
		## THIS IS CODED WRONGGGGG :((((((((((()))))))))))
		v = math.log(c*maxVal[pos.index(max(pos))]/(maxVal[pos.index(min(pos))]))
		x1 = min(posPx)
		x2 = max(posPx)
		eqn = ((x2-x1)/c1 * v) + x1
		return int(eqn)
	except ValueError:
		print "SAD VALUE ERROR"
		return -1

def filter_incoming_data(data):
	hor = data[0:4]
	vert = data[4:]
	deltaf_threshold = 60

	# threshold proximity
	if ((max(hor) < deltaf_threshold) or max(vert) < deltaf_threshold):
		print "LOW: ", data
		return (-1,-1)

	# find largest two values in array
	# store index associated with values too
	# format: [(index1, largestval), (index2, secondlargestval)]
	maxHor = heapq.nlargest(2, enumerate(hor), key=lambda x: x[1])
	maxVert = heapq.nlargest(2, enumerate(vert), key=lambda x: x[1])

	# check that they're neighbors
	if (abs(maxHor[1][0] - maxHor[0][0]) != 1):
		print "Horizontal messed up", maxHor
		return (-1,-1)
	if (abs(maxVert[1][0] - maxVert[0][0]) != 1):
		print "Vertical messed up", maxVert
		return (-1,-1)
	if (maxHor[0][1] < 1) or (maxHor[1][1] < 1) or (maxVert[0][1] < 1) or (maxVert[1][1] < 1):
		print "value is neg"
		return (-1,-1)
	return (maxHor, maxVert)


def get_fine_cursor_position_deltaf_simple(data, screen_width, screen_height):
	# proportions = [1./8, 3./8, 5./8, 7./8]
	proportions = [0.0, 1./3, 2./3, 1.0]

	hor_positions = [screen_width*item for item in proportions]
	vert_positions = [screen_height*item for item in proportions]

	(maxHor, maxVert) = filter_incoming_data(data)
	if (maxHor == -1) or (maxVert == -1):
		return (-1, -1)

	# return (get_fine_position(maxHor,hor_positions), int(vert_positions[1]))
	# return (get_fine_position(maxHor,hor_positions), get_fine_position(maxVert, vert_positions))
	vertPosFinal = screen_height - int(get_fine_position_simple(maxVert, vert_positions))
	# return (int(hor_positions[1]), vertPosFinal)
	return (get_fine_position_simple(maxHor,hor_positions), vertPosFinal)


def get_channel_radius(value, param_ch):
	# response = c/(x-b) + d  		where param_ch = [b c d]
	# x = c/(response-d) + b
	return param_ch[0] + 1.0*param_ch[1]/(value-param_ch[2])

def get_radius(data, num_channels=8):
	# Returns list of radii for each channel?
	param_ch1 = [-3.69, 12000.0, -256.0]
	param_ch2ch3 = [-1.92, 5988.0, -152.0]
	param_ch4 = param_ch1
	radii = [0.0]*num_channels
	radii[0] = get_channel_radius(data[0], param_ch1)
	radii[1] = get_channel_radius(data[1], param_ch2ch3)
	radii[2] = get_channel_radius(data[2], param_ch2ch3)
	return radii

def get_smallest_radii(radii):
	## Returns tuple of the form: (chi, chi+1)
	## radii: list of horizontal or vertical channels

	# find smallest two values in array
	# store index associated with values too
	# format: [(index1, largestval), (index2, secondlargestval)]
	minVals = heapq.nsmallest(2, enumerate(radii), key=lambda x: x[1])
	minCh = [x[0] for x in minVals]
	minCh = (min(minCh), max(minCh))

	# check that they're neighbors
	if (minCh[1] != minCh[0] + 1):
		return (-1, -1)
	return minCh

def get_fine_cursor_position_deltaf_r(data,screen_width, screen_height):
	###
	proportions = [1./8, 3./8, 5./8, 7./8]
	hor_positions = [screen_width*item for item in proportions]
	vert_positions = [screen_height*item for item in proportions]
	d = 10 # radius is in cm
	MAX_RADIUS = 40.0

	radii = get_radius(data)
	print "R: ", get_printable_list_floats(radii)
	# Knowing the radius data, this is a problem of the intersection of two
	# cylinders. Find the two channels with the smallest radii and use them
	# as the base
	minCh = get_smallest_radii(radii[0:3])
	if (minCh[1] == -1) or (minCh[0] == -1):
		return (-1, -1)
	if (radii[minCh[0]] > MAX_RADIUS) or (radii[minCh[0]] > MAX_RADIUS):
		return (-1, -1)
	print minCh

	rsq = radii[minCh[1]]**2
	Rsq = radii[minCh[0]]**2
	x0 = (-1.0*rsq + Rsq + d*d)/(2*d)

	x0Sq = x0*x0
	diff = Rsq - x0Sq
	z0 = 0.0
	if (diff > 0.0):
		z0 = math.sqrt(diff)


	print get_printable_list_floats((x0, z0))

	return (200,200)
	## Use knowledge about channels to derive an x value and z value

def bound_readings(pos, screen_width, screen_height):
	x = pos[0]
	y = pos[1]
	if (pos[0] < 0):
		x = 0
	elif (pos[0] >= screen_width):
		x = screen_width
	if (pos[1] < 0):
		y = 0
	elif (pos[1] >= screen_height):
		y = screen_height
	return (x,y)

def get_fine_cursor_position_deltaf_ratio(data, screen_width, screen_height):
	## when ratio ~ 1 (.7-1.3) between max channels, just use that
	## when ratio between max channels is <<1 or >>1, use 3 channels
	pos = compute_location_ratio.calculate_2D_location(data)
	# pos values will be between 0 and 1. Scale them up

	if (pos[0] == -1) or (pos[1] == -1):
		return (-1,-1)

	pos[0] = int(pos[0]*screen_width)
	pos[1] = int(pos[1]*screen_height)
	# bound them appropariately to the screen
	(hor_position,vert_position) = bound_readings(pos, screen_width, screen_height)
	return (hor_position, vert_position)


def scale(val, max_val, new_max_val):
	return int(val*new_max_val/max_val)

def get_fine_cursor_position_deltaf_reg(data, screen_width, screen_height):
	my_fit_index = [[-2262.8,3.7832], [-3672.4,11.091], [-3318.7,5.379],[ -7491.2,9.1247],[  -38372,42.846],[  -14345,17.695],[  -12184,14.453],[  -10805,14.061],[ -6928.8,7.8422],[ -6254.5,7.5817],[ -5497.8,6.4507],[ -4942.7,6.2533 ]]
	location = compute_location.calculate_2D_location(data, my_fit_index)
	print "LOCATION: ", location
	# map (0,15)x(0,15) --> (0, screen_width)x(0, screen_height)
	vert_position = screen_height - min(scale(location[1], 17, screen_height),screen_height)
	hor_position = min(scale(location[0], 17, screen_width), screen_width)
	hor_position = max(0, hor_position)
	vert_position = max(0, vert_position)
	return (hor_position, vert_position)

def get_z_position_deltaf_sum(data):
	threshold = 50
	data_above_thresh = [x-threshold for x in data if (x > threshold)]
	return sum(data_above_thresh)

def get_z_position_deltaf_eqn(data, x,y):
	hor_channels = [0,1,2,3]
	vert_channels = [4,5,6,7]
	maxv = max(data)
	maxvind = data.index(maxv)
	maxvpos = 1.*maxvind/3
	print maxvind, maxvpos, maxv
	if (maxvind) in hor_channels:
		return ((1/(maxv*maxv) - (maxvpos-x)*(maxvpos-x)))
	else:
		maxvpos = 1.*(maxvind-4)/3
		return ((1/(maxv*maxv) - (maxvpos-y)*(maxvpos-y)))

## CHANGE THIS FUNCTION TO CHANGE CURSOR POSITION
def get_fine_cursor_position_deltaf(data, screen_width, screen_height):
	#return get_fine_cursor_position_deltaf_simple(data, screen_width, screen_height)
	# return get_fine_cursor_position_deltaf_r(data, screen_width, screen_height)
	# return get_fine_cursor_position_deltaf_reg(data, screen_width, screen_height)
	return get_fine_cursor_position_deltaf_ratio(data, screen_width, screen_height)

## CHANGE THIS FUNCTION TO CHANGE OUTPUT Z
def get_z_position_deltaf(data,x=0,y=0):
	return get_z_position_deltaf_sum(data)
	# return get_z_position_deltaf_eqn(data,x,y)

def get_3D_position(data):
	# returns: (x,y,z) position where values are normalized between 0 and 1
	pos = compute_location_ratio.calculate_2D_location(data)
	pos = bound_readings(pos,1.,1.)
	z = get_z_position_deltaf(data, pos[0], pos[1])
	z = 1.*z/10000
	z = max(0, min(z,1))
	return (pos[0], pos[1], z)

def click(x0, y0):
	# win32api.SetCursorPos((x0,y0))
	# win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0)
	# time.sleep(0.5)
	# win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0)
	# time.sleep(0.1)
	return False

def smooth_filter(pre_x, pre_y, x, y):
	pre_x.pop()
	pre_x.insert(0,x)
	pre_y.pop()
	pre_y.insert(0,y)
	x = int(sum(pre_x) / 2.0)
	y = int(sum(pre_y) / 2.0)
	pre_x[0] = x
	pre_y[0] = y
	return [pre_x,pre_y,x,y]

def set_cursor_position_display(delta_freq, pre_delta_freq, screen_width, screen_height, pre_delta_x, pre_delta_y):
	x_ratio = 0.05
	y_ratio = 0.05
	#my_fit_index = [[-2262.8,3.7832], [-3672.4,11.091], [-3318.7,5.379],[ -7491.2,9.1247],[  -38372,42.846],[  -14345,17.695],[  -12184,14.453],[  -10805,14.061],[ -6928.8,7.8422],[ -6254.5,7.5817],[ -5497.8,6.4507],[ -4942.7,6.2533 ]]
	[delta_x,delta_y] = compute_delta_location.compute_delta_location(delta_freq, pre_delta_freq)
	velocity = pow(delta_x*delta_x+delta_y*delta_y, 0.35)
	delta_x = int(x_ratio * delta_x * velocity)
	delta_y = int(y_ratio * delta_y * velocity)
	print "dx dy:", delta_x, delta_y
	#if delta_x * pre_delta_x[0] < 0:
	#	delta_x = 0
	#if delta_y * pre_delta_y[0] < 0:
	#	delta_y = 0
	#print delta_x,delta_y
	[pre_delta_x,pre_delta_y,delta_x,delta_y] = smooth_filter(pre_delta_x,pre_delta_y,delta_x,delta_y)
	#print pre_delta_x,pre_delta_y,delta_x,delta_y

	x, y = (100,100) # win32api.GetCursorPos()
	x = max(min(x + delta_x, screen_width), 0)
	y = max(min(y - delta_y, screen_height), 0)

	print "location", (x,y), delta_x, delta_y

	#print "LOCATION: ", location
	# win32api.SetCursorPos((x,y))
	return [pre_delta_x, pre_delta_y]
