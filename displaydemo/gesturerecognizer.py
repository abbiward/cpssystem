'''
Should have window extractor and window analyzer objects?

Then can plug in various GR prototypes into window analyzer function?

What data should we store in the window?
	xyz data
	freq data
	(both?)

How to analyze the window?
	Look for peaks 
	classifiers: HMM, DTW


Example Applications to set up:
	Powerpoint/Keynote slide deck
		can do this via peaks
	Microsoft Flight (or similar game)
		only need xyz position
	Maze game (Halo?)
		need only xyz position
	Building block game



'''

'''
class GestureRecognizer:
	def __init__(self):
		hor_channels = [4,3,2,1]
		vert_channels = [7,6,5]

		self.gesture_dict = {(1,2,3,4):'rswipe',
						(4,3,2,1):'lswipe',
						(5,6,7):'dswipe',
						(7,6,5):'uswipe'
						# (1,2,3):'rswipe'
						# (2,3,4):'rswipe'
						}

		self.window = []
		self.window_size = 60
		self.test_frequency = 20 # test for gestures every 20 samples
		self.test_frequency_counter = 0


	def extract_peaks(self,freq_ctr,data,index):
		# extract peaks from the given data in the given index
		peak_threshold = 100
		# we define a 'peak' as a deviation from the 'freq_ctr' values by more than peak_threshold
		# and the value must come down below peak_threshold before another peak can be considered
		## TODO: FIX: for now, we only allow one peak per window per channel
		## TODO: use numpy arrays to do this crap faster
		## TODO: keep track of things over time via sliding window
		##		do this by having a data variable which stores data over time
		##		update_window is called with every new sample
		##		


	def update_window(self,data):
		# cry :(
		# add sample to curr_window
		self.window.append(data)
		if len(self.window) > self.window_size:
			self.window.remove(0) # hsould this be .pop?

		# maybe check if theres a gesture in the window?
		if (self.test_frequency_counter == self.test_frequency):
			self.get_gesture(freq_ctr)
			self.test_frequency_counter = 0
		self.test_frequency_counter += 1


	def get_gesture(self,freq_ctr,data_x,data_y):
		# data_x: time series of deltaf data for x-dimension
		# data_y: time series of deltaf data for y-dimension

		peak_order_x = []
		for i in range(len(data_x[0])):
			peak_indices = self.extract_peaks(freq_ctr,data_x,i)
			for item in peak_indices:
				peak_order.append((item,i))

		peak_order_y = []
		for i in range(len(data_y[0])):
			peak_indices = self.extract_peaks(freq_ctr,data_y,i)
			for item in peak_indices:
				peak_order.append((item,i))

		# peak order lists are of the form: [(time1,channeli), (time2,channelj)]
		# sort the peak order based on the time
		peak_order_x.sort(key=lambda item:item[0])
		peak_order_y.sort(key=lambda item:item[0])
		peak_order_x_final = [item[1] for item in peak_order_x]
		peak_order_y_final = [item[1] for item in peak_order_y]

		if peak_order_x_final in self.gesture_dict:
			return gesture_dict[peak_order_x_final]
		if peak_order_y_final in self.gesture_dict:
			return gesture_dict[peak_order_y_final]
		return None
'''




################################################################################
class Window:
	def __init__(self):
		self.x = []
		self.y = []
		self.z = []
		self.freq = []
		self.max_data_points = 15


	##
	# Maybe consider changing this such that a data dictionary is passed in
	# and then the window is updated by just storing the data from the dictionary
	# in the window dictionary (append to respective lists)
	# This way, you define what defines a window by the data that is passed in, 
	# rather than having it hardcoded into the window object

	def __str__(self):
		return "x: " + str(self.x) + "\ny: " + str(self.y) + "\nz: " + str(self.z)

	def __len__(self):
		return len(self.x)

	def update_window(self, data):
		# data = (x,y,z)
		if any(value == -1 for value in data): # any or all?
			return
		if any(value == 1.0 for value in data): # any or all?
			return
		self.update_list(self.x,data[0])
		self.update_list(self.y,data[1])
		self.update_list(self.z,data[2])

	def update_list(self, alist, data):
		alist.append(data)
		if len(alist) > self.max_data_points:
			alist.pop(0)


	def clear(self):
		self.x = []
		self.y = []
		self.z = []

	def getX(self):
		return self.x

	def getY(self):
		return self.y

	def getZ(self):
		return self.z

	def getPosition(self,position):
		return (self.x[position],self.y[position],self.z[position])


################################################################################
class XYZAnalysis:
	def __init__(self):
		self.threshold_dx = .5
		self.threshold_dy = .5

		# define gesture dictionary
		# how to standardize the names?
	def get_gesture(self, window):
		x_list = [value for value in window.getX() if value != -1]
		y_list = [value for value in window.getY() if value != -1]
		if len(x_list) == 0:
			return None
		(index_max_x, max_x) = max(enumerate(x_list),key=lambda x:x[1])
		(index_min_x, min_x) = min(enumerate(x_list),key=lambda x:x[1])
		(index_max_y, max_y) = max(enumerate(y_list),key=lambda x:x[1])
		(index_min_y, min_y) = min(enumerate(y_list),key=lambda x:x[1])
		# note: instead of finding these every time, could just update them / associate them
		# with the Window object and update them in parallel with adding/removing items


		# This is just very simple deltas, might want to make sure that hte dx and dy are below certain thresholds during the swipes too :/
		if ((max_x - min_x) > self.threshold_dx) and (index_max_x > index_min_x):
			return 'rswipe'
		if ((max_x - min_x) > self.threshold_dx) and (index_max_x <= index_min_x):
			return 'lswipe'
		if ((max_y - min_y) > self.threshold_dy) and (index_max_y > index_min_y):
			return 'uswipe'
		if ((max_y - min_y) > self.threshold_dy) and (index_max_y <= index_min_y):
			return 'dswipe'

		return None


import dtw
import numpy as np
import gestlib
class PathAnalysis:
	def __init__(self):
		self.happy = ":)"
		self.gesture_dict = gestlib.gesture_dict
		# self.gesture_dict['still'] = [[0.0, 0.0, 0.0], [0.00, 0.0, 0.0], [0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]]
		# self.gesture_dict = {
		# 					'still' : [[0.0, 0.0, 0.0], [0.00, 0.0, 0.0], [0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]],
		# 					'rswipe' : [[0.0, 0.0, 0.0], [0.05, 0.0, 0.0], [0.1, 0.0, 0.0],[0.15, 0.0, 0.0],[0.2, 0.0, 0.0],[0.25, 0.0, 0.0],[0.3, 0.0, 0.0],[0.35, 0.0, 0.0]],
		# 					'lswipe' : [[0.0, 0.0, 0.0], [-0.05, 0.0, 0.0], [-0.1, 0.0, 0.0],[-0.15, 0.0, 0.0],[-0.2, 0.0, 0.0],[-0.25, 0.0, 0.0],[-0.3, 0.0, 0.0],[-0.35, 0.0, 0.0]],
		# 					'uswipe' : [[0.0, 0.0, 0.0], [0.0, 0.05, 0.0], [0.0, 0.1, 0.0],[0.0, 0.15, 0.0],[0.0, 0.2, 0.0],[0.0, 0.25, 0.0],[0.0, 0.3, 0.0],[0.0, 0.35, 0.0]],
		# 					'circle' : [[0.0, 0.0, 0.0], [0.0, 0.05, 0.0], [0.05, 0.1, 0.0],[0.1, 0.15, 0.0],[0.15, 0.1, 0.0],[0.1, 0.05, 0.0],[0.05, 0.0, 0.0],[0.0, 0.0, 0.0]]
		# 					# 'uswipe' : [[0.0, 0.0, 0.0], [0.0, 0.05, 0.0], [0.0, 0.1, 0.0],[0.0, 0.15, 0.0],[0.0, 0.2, 0.0],[0.0, 0.25, 0.0],[0.0, 0.3, 0.0],[0.0, 0.35, 0.0],[0.0, 0.4, 0.0],[0.0, 0.45, 0.0],[0.0, 0.5, 0.0],[0.0, 0.55, 0.0],[0.0, 0.6, 0.0],[0.0, 0.65, 0.0],[0.0, 0.7, 0.0],[0.0, 0.75, 0.0],[0.0, 0.8, 0.0],[0.0, 0.85, 0.0],[0.0, 0.9, 0.0],[0.0, 0.95, 0.0]]
		# }
		self.dtw = dtw.DTW()

	def make_new_window(self,window):
		# Makes the window of absolute positions into a path with the first entry as the origin
		newwindow = []
		origin = window.getPosition(0)
		for i in range(1,len(window.getX())):
			newpt = window.getPosition(i)
			newwindow.append([val-oval for (val,oval) in zip(newpt,origin)])
		newwindow = np.array(newwindow)
		# newwindow = newwindow[:,:-1] # remove z-dir
		print "Old window: ", window
		print "New window: ", newwindow
		return newwindow

	def get_gesture(self,window):
		if len(window) < 5:
			return None
		new_window = self.make_new_window(window)
		min_alignment_dist = float("inf")
		best_gesture = ""
		for gesture in self.gesture_dict:
			mat = np.array(self.gesture_dict[gesture])
			# mat = mat[:,:-1] # remove z-dir
			alignment_dist = self.dtw.get_alignment(new_window, mat)[0]
			print "gr:gesture comp:", gesture, alignment_dist
			if (alignment_dist < min_alignment_dist):
				best_gesture = gesture
				min_alignment_dist = alignment_dist
		print "gr: best gesture", best_gesture, min_alignment_dist
		# if (min_alignment_dist > 4.0):
			# return None

		# If you're returning a gesture, clear the first 5 entries of the window


		return best_gesture

	# TODO: implement dtwmatching
	# TODO: trim starting 0's



class GestureRecognizer:
	def __init__(self):
		self.window = Window()
		self.XYZAnalysis = XYZAnalysis()

	def update(self,data):
		self.window.update_window(data)

	def get_gesture(self):
		return self.XYZAnalysis.get_gesture(self.window)


def main_xyzana():
	import time
	xyzana = XYZAnalysis()
	window = Window()

	test_frequency = 10
	test_frequency_counter = 0

	start = time.clock()
	end = start + 5

	# positions = [(.2,.5,.5),(.25,.5,.5),(.3,.5,.5),(.4,.5,.5), (.45,.5,.5),(.5,.5,.5),(.6,.5,.5),(.65,.5,.5),(.7,.5,.5),(.75,.5,.5),(.8,.5,.5)]
	positions = [(.5,.2,.5),(.5,.25,.5),(.5,.3,.5),(.5,.4,.5), (.5,.45,.5),(.5,.5,.5),(.5,.6,.5),(.5,.65,.5),(.5,.7,.5),(.5,.75,.5),(.5,.8,.5)]

	while positions:
		# get position data
		positiondata = positions.pop(0)
		print "position:", positiondata

		# update window
		window.update_window(positiondata)

		# maybe check if theres a gesture in the window?
		if (test_frequency_counter == test_frequency):
			gesture = xyzana.get_gesture(window)
			print gesture
			test_frequency_counter = 0
		test_frequency_counter += 1


def main_dtw():
	import time
	pathana = PathAnalysis()
	window = Window()

	test_frequency = 10
	test_frequency_counter = 0

	start = time.clock()
	end = start + 5

	# positions = [(.2,.5,.5),(.25,.5,.5),(.3,.5,.5),(.4,.5,.5), (.45,.5,.5),(.5,.5,.5),(.6,.5,.5),(.65,.5,.5),(.7,.5,.5),(.75,.5,.5),(.8,.5,.5)]
	positions = [(.5,.2,.5),(.5,.25,.5),(.5,.3,.5),(.5,.4,.5), (.5,.45,.5),(.5,.5,.5),(.5,.6,.5),(.5,.65,.5),(.5,.7,.5),(.5,.75,.5),(.5,.8,.5)]

	while positions:
		# get position data
		positiondata = positions.pop(0)
		print "position:", positiondata

		# update window
		window.update_window(positiondata)

		# maybe check if theres a gesture in the window?
		if (test_frequency_counter == test_frequency):
			gesture = pathana.get_gesture(window)
			print gesture
			test_frequency_counter = 0
		test_frequency_counter += 1


if __name__ == '__main__':
	main_dtw()
		
