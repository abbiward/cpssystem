'''
How this works: 
The actual position calculator can be in whatever local file -- i.e. mycalc.py

Then, below, add 
	import mycalc as pt
The pt is important to leave as is.

I'm adding this class so that we can change how this is done later and maybe
integrate the final method into this module

'''


import compute_location_ratio_ITOdisp as pt
import numpy as np
import errorlog as el
import sys
sys.path.append("/Users/aaward/Dropbox/IW")
import configurations as config

class PositionTracker():
	def __init__(self,errorlog=None):
		if errorlog:
			self.errorlog = errorlog
		else:
			self.errorlog = el.ErrorLog()

		self.averaged_data = []
		self.num_samples_to_avg = config.pt_num_samples_to_use
		self.PT = pt.LocationComputer(errorlog=self.errorlog)
		# self.threshold_delta_values = 300

	# Keeps track of the last num_samples_to_avg samples and returns the average
	# of the latest list of samples.
	def update_data(self,data):
		# average of averages code: 
		# if len(self.averaged_data) < self.num_samples_to_avg:
		# 	self.averaged_data.append(data)
		# 	return data
		# nparr = np.array(self.averaged_data + [data])
		# avg = nparr.mean(axis=0)
		# self.averaged_data.append(avg)
		######
		# if the new data differs from the old average by more than threshold_delta_values, 
		#	then dont use the average
		# if (len(self.averaged_data) != 0):
		# 	old_data = self.averaged_data[-1]
		# 	for item,old_item in zip(data,old_data):
		# 		if abs(item-old_item) > self.threshold_delta_values:
		# 			# throw out averaging
		# 			self.averaged_data = [data]
		# 			return data

		# print "positiontracker.py: averaging"
		####
		# normal average code
		self.averaged_data.append(data)
		nparr = np.array(self.averaged_data)
		avg = nparr.mean(axis=0)
		########

		if len(self.averaged_data) > self.num_samples_to_avg:
			self.averaged_data.pop(0)
		return avg

	# Return the 3D position (x,y,z) 
	# xypos: normalized position or -1,-1 for errors
	# zpos : relative position
	def calculate_position(self,data):
		data = self.update_data(data)
		xypos = self.PT.calculate_2D_position(data)
		zpos = self.PT.calculate_z_position(data)

		# Error log:
		self.errorlog.record("positiontracker.py:data", data)
		self.errorlog.record("positiontracker.py:self.averaged_data", self.averaged_data)

		return (xypos[0], xypos[1], zpos)


	# def get_fine_cursor_position_deltaf_ratio(self,data, screen_width, screen_height):
	# 	## when ratio ~ 1 (.7-1.3) between max channels, just use that
	# 	## when ratio between max channels is <<1 or >>1, use 3 channels
	# 	pos = compute_location_ratio.calculate_2D_location(data)
	# 	# pos values will be between 0 and 1. Scale them up

	# 	if (pos[0] == -1) or (pos[1] == -1):
	# 		return (-1,-1)

	# 	pos[0] = int(pos[0]*screen_width)
	# 	pos[1] = int(pos[1]*screen_height)
	# 	# bound them appropariately to the screen
	# 	(hor_position,vert_position) = bound_readings(pos, screen_width, screen_height)
	# 	return (hor_position, vert_position)

			