'''
## This takes care of everything for the hardware-software pipeline    

There is an option to use fake data as input to the pipeline. This is useful for
recording sample ADC values and then using the pipeline to convert them to
deltaf values as we would normally, in a live system. 

Example Use:
    pipeline = Pipeline()

Note: configurations as specified in configurations.py can be overwritten. This
is done for prototyping purposes and should be eliminated in future iterations.

'''

import sys
import serial
import numpy as np
import re
import time
import errorlog as el

sys.path.append("/Users/aaward/Dropbox/IW")
import configurations as config     # custom configuration parameters

class Pipeline():
    def __init__(self, valid_channels=config.valid_channels, com=config.com, baudrate=config.baudrate, errorlog=None,
        usefakedata=False):  
        self.ser_port = com
        self.ser_baudrate = baudrate
        if errorlog:
        	self.errorlog = errorlog
        else:
        	self.errorlog = el.ErrorLog()

        self.valid_channels = valid_channels
        num_channels = len(valid_channels)

        self.usefakedata = usefakedata
        self.fake_data_files = ['calibration.tmp', 'sample1.tmp']
        self.fake_data = []

        self.adc_recalibration = []
        self.samples_since_calibration = 0

        # Prepare serial port when using real data
        if not self.usefakedata:
            ## setup serial port
            self.ser=serial.Serial(port=self.ser_port)
            self.ser.timeout=3
            self.ser.baudrate=self.ser_baudrate    

            self.ser.write(config.connectioncmd) # open connection to module
            self.ser.flush()

        else:
            self.ser=None

        # Read and toss
        for num in range(20):
            s = self.read_serial_line_to_data_list(self.ser)

        # calibrate
        self.freq_ctr = self.calibrate(self.ser,num_channels=len(self.valid_channels))

        print "CALIBRATION DONE"

    def recalibrate_pipeline(self):
        self.freq_ctr = self.calibrate(self.ser,num_channels=len(self.valid_channels))

    ## Helper function that mocks out the serial readout
    def read_fake_data(self):
    	if not self.fake_data:
            if not self.fake_data_files:
                return ""
            filename=self.fake_data_files.pop(0)
            f = open(filename,'r')
            self.fake_data = f.readlines()
    	
    	new_data = self.fake_data.pop().strip()
    	new_data = new_data.replace('[','')
    	new_data = new_data.replace(']','')
    	new_data = new_data.replace(r'\s','')
    	print "pipeline.py:fakedata:",new_data
    	time.sleep(.1)
    	vals = [int(x) for x in new_data.split(',')]
    	data_final = [0]*len(self.valid_channels)
    	for i in range(len(data_final)):
    		data_final[i] = vals[self.valid_channels[i]]
    	return data_final

    # This function converts the serial data input to a list of data.  Each
    # channel should be represented by 2 bytes and at the end of each data
    # sample, there is an EOL byte string specific to this system
    def read_serial_line_to_data_list(self, ser):
        if self.usefakedata:
    	   return self.read_fake_data()
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

        data_final = [0]*len(self.valid_channels)
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

        thereIsZeroDataVal = False
        for ind,item in zip(range(0,len(self.valid_channels)),self.valid_channels):
            data_final[ind] = (data[2*item]<<8) + (data[2*item+1])
            if data_final[ind] == 0:
                # print "ISZERO: ", data[2*item], data[2*item+1]
                data_final[ind] = data_final[ind] + 1
                thereIsZeroDataVal = True
        if thereIsZeroDataVal:
            print "DATAFINAL:", data_final
        return data_final


    # calibrate Collect several calibration samples and average them to get base
    # calibration values. It is assumed that these samples are collected during
    # a period of no interaction. 
    def calibrate(self, ser, num_channels=8, f_LO=config.f_LO, num_calibration_attempts=0, factor=config.factor):
        NUM_CALIBRATION_SAMPLES = 20
        MAX_CALIBRATION_ATTEMPTS = 3
        MAX_BAD_SAMPLES = 6
        ADC_LOW_THRESHOLD = 0
        ADC_HIGH_THRESHOLD = 20000
        if (num_calibration_attempts >= MAX_CALIBRATION_ATTEMPTS):
            print "pipeline.py:FAILED TO CALIBRATE"
            sys.exit(0)

        base_value = [[] for x in range(num_channels)]
        num_samples_used = 0
        num_bad_samples = 0

        # Collect samples (ignore misformatted data)
        for i in range(NUM_CALIBRATION_SAMPLES):
            line = self.read_serial_line_to_data_list(ser)
            if (len(line) != num_channels) or (min(line) < ADC_LOW_THRESHOLD) or (max(line) > ADC_HIGH_THRESHOLD) or (max(line) < 1):
                print i, " UH OH : ", line, len(line), min(line), max(line)
                num_bad_samples = num_bad_samples + 1
                if (num_bad_samples > MAX_BAD_SAMPLES):
                    print "pipeline.py:TRYING AGAIN"
                    return self.calibrate(ser,num_calibration_attempts=num_calibration_attempts+1)
                continue
            print i, " OKAY: ", line
            for j in range(num_channels):
                #base_value[j] = base_value[j] + int(line[j])
                base_value[j].append(int(line[j]))
            num_samples_used = num_samples_used + 1

        # Take the middle 60% of the samples
        base_value_sorted = []
        for i in range(num_channels):
            base_value_sorted.append(sorted(base_value[i]))
            listlen = len(base_value_sorted[i])
            base_value_sorted[i] = base_value_sorted[i][int(.2*listlen):int(.8*listlen)]

        # Find the mean
        x = np.array(base_value_sorted)
        x = np.mean(x, axis=1)

        mean_value = [0]*num_channels
        for i in range(num_channels):
            mean_value[i] = x[i]
            if (x[i] == 0):
            	mean_value[i] = 1.

        freq_ctr = [0]*num_channels
        for i in range(num_channels):
            # freq_ctr[i] = 2*f_LO/mean_value[i]    ## CHANGE HERE
            freq_ctr[i] = factor*f_LO/mean_value[i]

        print "pipeline.py:BASE: ", mean_value
        print "pipeline.py:freq_ctr",freq_ctr

        return freq_ctr

    # convert
    # Note: trackpad/touchpad factor=config.factor
    def convert_ADC_to_deltaf(self, freq_ctr, data, num_channels=8, f_LO=config.f_LO, factor=config.factor):
        data = map(int, data)
        freq_delta = [0]*num_channels
        try:
            for i in range(num_channels):
                #freq_delta[i] = (2*f_LO/data[i]) - freq_ctr[i] ## CHANGE HERE
                freq_delta[i] = (factor*f_LO/data[i]) - freq_ctr[i]
            # print_list(freq_delta, sys.stdout)
            return freq_delta
        except ZeroDivisionError:
            print "pipeline.py:ERROR-0-DIV: ", data
            return [0]*num_channels   

    def recalibration(self, f_LO=config.f_LO, factor=config.factor):
        num_channels = len(self.valid_channels)

        if (len(self.adc_recalibration) < 30):
            print "NOT ENOUGH SAMPLES"
            sys.exit(0)

        npx = np.array(self.adc_recalibration)
        x = np.mean(npx, axis=0)

        mean_value = [0]*num_channels
        for i in range(num_channels):
            mean_value[i] = x[i]
            if (x[i] == 0):
                mean_value[i] = 1.

        freq_ctr = [0]*num_channels
        for i in range(num_channels):
            # freq_ctr[i] = 2*f_LO/mean_value[i]    ## CHANGE HERE
            freq_ctr[i] = factor*f_LO/mean_value[i]

        print "Num recalibration samples:", len(self.adc_recalibration)
        self.adc_recalibration = []
        print "Old:", self.freq_ctr
        print "New:", freq_ctr
        self.freq_ctr = freq_ctr
        # sys.exit(0)
        return

    def get_freq_ctr(self):
        return self.freq_ctr

    def use_smallest_ch_as_baseline(self, freq_delta):
        mindf = min(freq_delta)
        return [val-mindf for val in freq_delta]

        # need to handle the case where:
        #   interaction will reduce the df values, so what appears as the min is
        #   actually interaction

    def get_data(self):
        ## get data! 
        s = self.read_serial_line_to_data_list(self.ser)
        print "pipeline.py:adc:", s
        freq_delta = self.convert_ADC_to_deltaf(self.freq_ctr, s, num_channels=len(self.valid_channels))
        # freq_delta_list = maintain_freq_delta_list(freq_delta_list, freq_delta)
        


        freq_delta = [abs(x) for x in freq_delta]
        # freq_delta = self.use_smallest_ch_as_baseline(freq_delta)
        
        # # store for recalibration:
        # self.samples_since_calibration += 1
        # if all([((x < 200) && (x > 0)) for x in freq_delta]):
        # # if all([((x < (y+200)) and (x > (y-200))) for (x,y) in zip(freq_delta,self.freq_ctr)]):
        #     # print "RECALIBRATION:", freq_delta
        #     # print "RECALIBRATION:", self.freq_ctr
        #     self.adc_recalibration.append(s)
        #     if self.samples_since_calibration > (15*20): # recalibrate every 15s
        #         self.recalibration()
        #         self.samples_since_calibration = 0
        #     # print "RECALIBRATION: ADDING"
        # else:
        #     print "RECALIBRATION: IGNORNING"
        # print "RECALIBRATION:", freq_delta
        # print "RECALIBRATION:", self.freq_ctr

        # record in error log
        self.errorlog.record("pipeline:s",s)
        self.errorlog.record("pipeline:freq_delta",freq_delta)

        return (freq_delta, s)
        # return s
    



