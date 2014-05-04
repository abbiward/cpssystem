'''
# rundemo.py
# You can change the files that we use for each part by changing the import
# statements
'''

import cursordemo
import pipeline
import positiontracker
import errorlog
import time
import pygame as pg

def main():
    err = errorlog.ErrorLog()
    P = pipeline.Pipeline(errorlog=err) # set up pipeline and calibrate
    PT = positiontracker.PositionTracker(errorlog=err) # set up position tracker
    CD = cursordemo.CursorDemo() # set up cursor demo
    
    start_time = time.time()
    
    DO_RECORD = False
    if (DO_RECORD):
        f_record = open('tmp-record.tmp', 'w')

    f = open('tmp.tmp', 'w')
    f2 = open('tmp-longterm.tmp', 'w')

    ## program constants
    program_time_length = 1800 # (seconds) == 30 min # 162 + 324 # 324=20min, 162=10min
    end_time = start_time + program_time_length
    now = time.time()
    f.write("Pgm start time:" + str(now) + "\n")
    loop_counter = 0
    sampling_freq = 20

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

        if (DO_RECORD):
            f_record.write(data + "\n")

        if loop_counter == sampling_freq:
            loop_counter = 0
            f2.write("df:" + str(data) + "\n")
            f2.write("adc:" + str(adcdata) + "\n")
        loop_counter += 1

        # get cursor position
        current_pos = PT.calculate_position(data)
        print 'rundemo.py:current_pos:',current_pos
        err.record("rundemo.py:current_pos", current_pos)

        # # update the demo display
        CD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5)
        if event.type == pg.KEYDOWN:
            # Reset pipeline
            # P.recalibrate_pipeline()
            f.write(str(data) + "\n")
            # f.write(str(data) + "\t" + str(current_pos) + "\n")
            # f.write("Pgm time:" + str(now) + "\n")
            # f.write(str(err))
            print "RECORD"
        now = time.time()
        # quit on mouse click
        if event.type == pg.MOUSEBUTTONDOWN:
            print P.freq_ctr
            f2.write("freqctr:" + str(P.freq_ctr) + "\n")
            print "Ending upon user instruction."
            break

    f2.write("freqctr:" + str(P.freq_ctr) + "\n")
    f.write("Pgm end time:" + str(time.time()) + "\n")
    f.close()
    f2.close()

if __name__ == '__main__':
    main()
