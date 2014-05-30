import sys
import math
#import util
import heapq
import errorlog as el

sys.path.append("/Users/aaward/Dropbox/IW")
import configurations as config


class LocationComputer:
	def __init__(self,errorlog=None):
		if errorlog:
			self.errorlog = errorlog
		else:
			self.errorlog = el.ErrorLog()
		# create ratio dictionaries ahead of time
		ratio_dictionary4 = {(1,2,3,4): [[1,1,1],[2,3,4]],# [[1,1,1],[2,3,4]], ## WHAT I HAD WAS WRONG B/C THESE ARE THE RATIOS BETWEEN THE ORDERED CHANNELS (1 = channel w/ max val)
								(2,1,3,4): [[2,1,1],[1,3,4]],# [[1,2,2],[2,3,4]],
								(3,1,2,4): [[2,3,1,2],[3,1,4,4]],# [[1,2,1,3],[2,3,4,4]],
								(4,2,1,3): [[3,3,2,4],[2,1,4,1]],# [[1,2,1,3],[2,3,4,4]],
								(4,3,1,2): [[3,4,4],[4,2,1]],# [[1,2,2],[2,3,4]],
								(4,3,2,1): [[4,4,4],[3,2,1]],# [[1,1,1],[2,3,4]],
								# dth		# what happens is these channel orderings show up
								# when multiple channel values are below threshold.
								# I've coded it so that they are like they closest
								# physically sensible ordering
								#(3,4,2,1): [[1,1,1],[2,3,4]],
								#(4,1,2,3): [[1,2,1,3],[2,3,4,4]],
								}
		ratio_dictionary4.update(dict.fromkeys([(1,2,3,4), (1,2,3,0), (1,2,0,0), (1,0,0,0)], [[1,1,1],[2,3,4]]))
		ratio_dictionary4.update(dict.fromkeys([(2,1,3,4), (2,1,3,0), (2,1,0,0), (0,1,0,0)], [[2,1,1],[1,3,4]]))
		ratio_dictionary4.update(dict.fromkeys([(3,1,2,4), (3,1,2,0), (0,1,2,0), (0,1,0,0)], [[2,3,1,2],[3,1,4,4]]))
		ratio_dictionary4.update(dict.fromkeys([(4,1,2,3), (0,1,2,3), (0,1,2,0), (0,1,0,0)], [[2,3,4,2],[3,1,1,4]]))
		ratio_dictionary4.update(dict.fromkeys([(4,2,1,3), (0,2,1,3), (0,2,1,0), (0,0,1,0)], [[3,3,2,4],[2,1,4,1]]))
		ratio_dictionary4.update(dict.fromkeys([(4,3,1,2), (0,3,1,2), (0,0,1,2), (0,0,1,0)], [[3,4,4],[4,2,1]]))
		ratio_dictionary4.update(dict.fromkeys([(4,3,2,1), (0,3,2,1), (0,0,2,1), (0,0,0,1)], [[4,4,4],[3,2,1]]))


		ratio_dictionary3 = {(1,2,3): [[1,1],[2,3]],# [[1,1,1],[2,3,4]], ## WHAT I HAD WAS WRONG B/C THESE ARE THE RATIOS BETWEEN THE ORDERED CHANNELS (1 = channel w/ max val)
								(2,1,3): [[2,1],[1,3]],# [[1,2,2],[2,3,4]],
								(3,1,2): [[2,3],[3,1]],# [[1,2,1,3],[2,3,4,4]],
								(3,2,1): [[3,3],[2,1]],# [[1,1,1],[2,3,4]],
								# The following entries dont make sense physically but
								# what happens is these channel orderings show up
								# when multiple channel values are below threshold.
								# I've coded it so that they are like they closest
								# physically sensible ordering
								#(3,4,2,1): [[1,1,1],[2,3,4]],
								#(4,1,2,3): [[1,2,1,3],[2,3,4,4]],
								}
		ratio_dictionary3.update(dict.fromkeys([(1,2,3), (1,2,0), (1,0,0)],[[1,1],[2,3]]))
		ratio_dictionary3.update(dict.fromkeys([(2,1,3), (2,1,0), (0,1,0)],[[2,1],[1,3]]))
		ratio_dictionary3.update(dict.fromkeys([(3,1,2), (0,1,2), (0,1,0)],[[2,3],[3,1]]))
		ratio_dictionary3.update(dict.fromkeys([(3,2,1), (0,2,1), (0,0,1)],[[3,3],[2,1]]))

		self.ratio_dictionaries = {3:ratio_dictionary3, 4:ratio_dictionary4}

		self.threshold_channel = config.threshold_channel_zdir # [150,100,100,200,250,250,100]
		self.max_sum_value = config.max_sum_value #10000

	################################## Z POSITION ##################################
	def get_z_position_deltaf_sum(self, data):
		#threshold = 150
		data_above_thresh = [x-threshold for x,threshold in zip(data,self.threshold_channel) if (x > threshold)]
		return sum(data_above_thresh)

	def calculate_z_position(self, data):
		return 1.*self.get_z_position_deltaf_sum(data)/self.max_sum_value

	################################## XY POSITION #################################
	def calculate_2D_position(self, delta_freq):
		# delta_freq is list of 8 deltaf values
		# fit_index is list of length 8 where each entry is list of length 2
		# each entry defines the fit model (a,b)
		# freq_threshold = 200
		# threshold_vertical = 4
		# threshold = 3

		# hor_channels are the ones used to get the horizontal position.
		# They're actually positioned vertically on the display.

		# Trackpad
		#hor_channels = [5,6,7,8] # left to right
		#vert_channels = [4,3,1,2] # bottom to top

		# big display
		hor_channels = config.hor_channels #[7,3,2,1] #[1,2,3,4]
		vert_channels = config.vert_channels #[4,5,6] #[6,5,4] #[5,6,7]

		#delta_freq_hor = [abs(delta_freq[x-1]) for x in hor_channels]
		delta_freq_hor = [delta_freq[x-1] for x in hor_channels]
		#delta_freq_vert = [abs(delta_freq[x-1]) for x in vert_channels]
		delta_freq_vert = [delta_freq[x-1] for x in vert_channels]

		self.errorlog.record("compute:delta_freq", delta_freq)
		self.errorlog.record("compute:delta_freq_hor", tuple(delta_freq_hor))
		self.errorlog.record("compute:delta_freq_vert", tuple(delta_freq_vert))

		location = [-1,-1]

		#location[0] = get_x_location(delta_freq_hor)
		#location[1] = get_y_location(delta_freq_vert)
		#print "x pos:"
		location[0] = self.get_location_delta(delta_freq_hor,num_channels_dim=len(hor_channels),channel_distance=17.5,threshold_ratio=config.threshold_ratio_hor)
		#print "y pos:"
		location[1] = self.get_location_delta(delta_freq_vert,num_channels_dim=len(vert_channels),channel_distance=14.5,threshold_ratio=config.threshold_ratio_vert)
		# if (ypos != -1):
		# 	location[1] = 1.-ypos
		# else:
		# 	location[1] = ypos

		#print "computed loc: ", location
		return location


	def get_ratio_dict(self, num_channels):
		if num_channels not in self.ratio_dictionaries:
			return self.ratio_dictionaries[4]
		return self.ratio_dictionaries[num_channels]

	def get_ratios_to_consider(self, data, num_channels=4,value_threshold=350):
		# Returns two lists which contain the indices of various ratios to consider
		# value_threshold: ignore indices

		# we want to ignore stuff below the value_threshold. 
		data_above_thresh = [x > value_threshold for x in data]
		data_thresh = data
		for ind,isAboveThresh in enumerate(data_above_thresh):
			if not isAboveThresh:
				data_thresh[ind] = 0


		# get data ordering
		#a = heapq.nlargest(len(data), enumerate(data), key=lambda x: x[1])
		a = heapq.nlargest(len(data_thresh), enumerate(data_thresh), key=lambda x: x[1])		
		b = range(len(data))
		data_ordering = [0]*num_channels
		for ind,val in enumerate(a):
			data_ordering[val[0]] = ind + 1
		####
		# zero stuff in the ordering now
		for ind,isAboveThresh in enumerate(data_above_thresh):
			if not isAboveThresh:
				data_ordering[ind] = 0
		####
		data_ordering = tuple(data_ordering)
		# data_ordering = tuple([b[x[0]]+1 for x in a])
		# print 'ordering:',data_ordering
		ratio_dictionary = self.get_ratio_dict(num_channels)

		# This dictionary contains unusual orderings which may happen when no body
		# part is in close proximity to multiple channels:
		strange_ordering = list(data_ordering)
		strange_ordering.extend([(val >= value_threshold) for val in data])
		strange_ordering = tuple(strange_ordering)
		strange_ratio_dictionary = {
							(3,2,1,4,False,True,True,False): [[3,3,2,4],[2,1,4,1]],
							(3,4,2,1,False,False,True,True): [[4,4,4],[3,2,1]],
							(4,1,2,3,False,True,True,False): [[2,3,1,2],[3,1,4,4]],
		}


		if data_ordering not in ratio_dictionary:
			print "I am sad.:", data_ordering
			self.errorlog.record("compute:data_ordering", data_ordering)
			#print (strange_ordering in strange_ratio_dictionary), strange_ordering
			#print "a", a
			return []
		ratio_lists = ratio_dictionary[data_ordering]
		# print "get_ratios_to_consider:rat_lists:",ratio_lists
		# only want to use ratios when the values are above a given value threshold
		thresholded_lists = [(rtop,rbottom) for rtop,rbottom in zip(ratio_lists[0],ratio_lists[1]) if (data[rtop-1] > value_threshold) and (data[rbottom-1] > value_threshold)]
		# print "get_ratios_to_consider:thresholded_lists:", thresholded_lists
		# now calculate the actual ratios from the data?
		# also want to calculate what the weights should be
		thresholded_data_values = [(data[x[0]-1]-value_threshold, data[x[1]-1]-value_threshold, x[0]-1, x[1]-1) for x in thresholded_lists]

		# print "get_ratios_to_consider:threshold_data_val:", thresholded_data_values

		# return list format: [(ratio1,weight1,ch_top1, ch_bottom1),(ratio2,weight2,ch_top2,ch_bottom2),...]
		# here, the weights are just the smaller value
		final_list = [(1.*x[0]/x[1], min(x[0],x[1]), x[2], x[3]) for x in thresholded_data_values]
		# final_list = [(1.*(x[0]+value_threshold)/(x[1]+value_threshold), min(x[0],x[1]), x[2], x[3]) for x in thresholded_data_values]


		# Error values:
		self.errorlog.record("compute:data_ordering", data_ordering)
		self.errorlog.record("compute:ratio_lists", ratio_lists)
		self.errorlog.record("compute:thresholded_lists", thresholded_lists)
		self.errorlog.record("compute:thresholded_data_values", thresholded_data_values)
		self.errorlog.record("compute:final_list", final_list)

		return final_list


	def get_norm_position(self, ratio, positions_px, threshold_ratio=config.threshold_ratio): # 2.5
		# ASSUMPTIONS: channels are already neighbors
		# positions_px: [0] = loc of highest val, [1] location of lowest val

		# print "R: ", ratio, " positions:", positions_px

		# TODO: account for case where the ratio is so big you should leave it
		if (ratio > threshold_ratio):
			"compute_location.py:ratio > threshold_ratio"
			return positions_px[0]

		if positions_px[1] > positions_px[0]:
			# switch ratio, switch positions before using the equation
			positions_px.reverse()
			ratio = 1.0/ratio

		# equation: [(x2-x1)/ln(c*c)] * ln(c*r2/r1) + x1
		try:
			c1 = 2*math.log(threshold_ratio)
			v = math.log(threshold_ratio*ratio)
			x1 = positions_px[1]
			x2 = positions_px[0]
			eqn = ((x2-x1)/c1 * v) + x1
			return eqn
		except ValueError:
			print "VALUE ERROR with log"
			return -1

	def get_channel_loc(self, indices, num_channels=4):
		# ASSUME CHANNELS ARE EVENLY SPACED
		# get the normalized channel location for a given set of channel indices
		# and the given number of channels
		return [1.0*item/(num_channels-1) for item in indices]
		#x = []
		#for item in indices:
		#	x.append(1.0*item/(num_channels-1))
		#return x

	def get_location(self, ratio, indices, num_channels=4, channel_distance=15, threshold_ratio=config.threshold_ratio):
		# calculate the location like before
		# channel_distance: distance in cm between consecutive channels
		# threshold_ratio = 10
		positions_norm = self.get_channel_loc(indices,num_channels) # values between 0 and 1
		loc = self.get_norm_position(ratio, positions_norm, threshold_ratio=threshold_ratio)
		# print 'get_location:positions_norm', positions_norm
		# print 'get_location:loc', loc, ratio

		self.errorlog.record("compute:ratio,indicies,loc", (ratio,indices,loc))

		return loc

	def get_location_delta(self, delta_freq_dim, num_channels_dim=4,channel_distance=15,threshold_ratio=config.threshold_ratio):
		# delta_freq_dim: delta_freq values for a particular dimension
		ratio_list = self.get_ratios_to_consider(delta_freq_dim, num_channels=num_channels_dim, value_threshold=config.base_noise_threshold)
		# each ratio tells us something about the position
		if len(ratio_list) == 0:
			print "compute_location.py: no ratios : ", num_channels_dim, delta_freq_dim 
			return -1

		# want to call:
		location = []
		for item in ratio_list:
			location.append(self.get_location(item[0],[item[2], item[3]],num_channels=num_channels_dim, channel_distance=channel_distance, threshold_ratio=threshold_ratio))

		# print 'location_delta:', location
		# print 'ratio_list: ', ratio_list

		# now want to do all the weights
		total_weight = sum([x[1] for x in ratio_list])
		average_location = sum([1.*location[ind]*val[1]/total_weight for ind,val in enumerate(ratio_list)])
		# print "avg_loc, tot_w:", average_location, total_weight
		return average_location

def main():
	LC = LocationComputer()
	# V10
	# my_delta_freq = [-470 ,  -91,  -586,  -758,  -203,  -590,  -659,  -185]
	# H9
	# my_delta_freq = [-314  , -73 , -575 , -813  ,-185,  -543,  -624  ,-200]
	# H8
	# my_delta_freq = [-263  , -66,  -588,  -917  ,-227  ,-729 , -521,  -143]
	# H5
	# my_delta_freq = [ -251 ,  -73 , -579  ,-658 , -549 , -601  ,-226  , -89]
	# V5
	# my_delta_freq = [ -44  , -23,  -346,  -770 , -132 , -369 , -401 ,  -95]
	# V15
	# my_delta_freq = [-486 ,   75  ,-428,  -348,  -256 , -574 ,-671 , -271]
	my_delta_freq = [1130.122, 2156.276, 1121.850, 219.997, 34.770, 52.595, 60.954, 91.880]
	print LC.calculate_2D_location(my_delta_freq)

if __name__ == '__main__':
	main()