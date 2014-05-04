'''
# collectsample.py
# You can change the files that we use for each part by changing the import
# statements
'''
import sys
sys.path.append("/Users/aaward/Dropbox/IW/displaydemo")
import cursordemo
import pipeline
import positiontracker
import errorlog
import time
import pygame as pg

# import configurations as config     # custom configuration parameters

def main(argv):
    err = errorlog.ErrorLog()
    P = pipeline.Pipeline(errorlog=err) # set up pipeline and calibrate
    PT = positiontracker.PositionTracker(errorlog=err) # set up position tracker
    CD = cursordemo.CursorDemo() # set up cursor demo
    
    # Interpret commandline arguments
    [program_time_length,dirname, gesture_name] = argv
    if dirname[-1] != '/':
        dirname = dirname + '/'
    program_time_length = int(program_time_length)
    
    # Data is recorded to a different file for each type. 
    # This way, any of the later data can be reproduced if we don't want to 
    # recollect samples and any module has changed
    f_calibration = open(dirname+'calibration/cal_'+gesture_name,'w')
    f_adc = open(dirname+'adc/adc_'+gesture_name,'w')
    f_deltaf = open(dirname+'deltaf/df_'+gesture_name,'w')
    f_position_all = open(dirname+'position/pos_'+gesture_name,'w')
    f_position_gest = open(dirname+'positiongest/pos_'+gesture_name,'w')

    f_calibration.write(str(P.get_freq_ctr()) + "\n")

    start_time = time.time()
    end_time = start_time + program_time_length
    now = time.time()

    # set up the event loop 
    while now < end_time:
        event = pg.event.poll()
        err.reset()        

        # read in data
        (data, adcdata) = P.get_data()
        
        print "rundemo.py:data: ", data
        err.record("rundemo.py:data", data)

        if all(value == 0 for value in data):
            continue

        # record ADC and df
        f_adc.write(str(adcdata) + "\n")
        f_deltaf.write(str(data) + "\n")

        # get cursor position
        current_pos = PT.calculate_position(data)
        print 'rundemo.py:current_pos:',current_pos
        err.record("rundemo.py:current_pos", current_pos)

        # Record position
        f_position_all.write(str(current_pos) + "\n")
        if (-1 not in current_pos) and (1.0 not in current_pos):
            f_position_gest.write(str(current_pos) + "\n")

        # # update the demo display
        CD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5)
        now = time.time()
        # quit on mouse click
        if event.type == pg.MOUSEBUTTONDOWN:
            print "Ending upon user instruction."
            break

    print "Start time: ", start_time, "end: ", end_time, "diff: ", end_time-start_time
    f_calibration.close()
    f_adc.close()
    f_deltaf.close()
    f_position_all.close()
    f_position_gest.close()
    

if __name__ == '__main__':
    t1 = time.time()
    if len(sys.argv) != 4:
        print 'python collectsample.py time dir gesture_name'
    else:
        main(sys.argv[1:])
        print "TOTAL TIME: ", time.time()-t1
