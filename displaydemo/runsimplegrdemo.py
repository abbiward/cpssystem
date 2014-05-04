'''
# runsimplegrdemo.py
# You can change the files that we use for each part by changing the import
# statements
'''

# import cursordemo
import gesturerecognizer as gr
import pipeline
import positiontracker
import errorlog
import time
import pygame as pg # use to keep track of user interactions
import gesturedemo

import pymachid
from appinterfaces import Keynote

# sys.path.append("/Users/aaward/Dropbox/IW")
# import configurations as config     # custom configuration parameters

def main():
    err = errorlog.ErrorLog()
    P = pipeline.Pipeline(errorlog=err, usefakedata=False) # set up pipeline and calibrate
    PT = positiontracker.PositionTracker(errorlog=err) # set up position tracker
    # gestanalyzer = gr.XYZAnalysis()
    gestanalyzer = gr.PathAnalysis()
    window = gr.Window()
    GD = gesturedemo.GestureDemo()

    # CD = cursordemo.CursorDemo() # set up cursor demo
    start_time = time.time()
     
    f = open('tmp.tmp', 'w')

    f2 = open('tmp-gest.tmp', 'w')

    print "STARTING"

    ## program constants
    program_time_length = 30
    end_time = start_time + program_time_length
    now = time.time()
    f.write("Pgm start time:" + str(now) + "\n")
    samples_since_last_gr = 0
    gr_frequency = 10 # num samples to collect before trying recognition
    window_counter = 0
    inRecovery = False

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

        # get cursor position
        current_pos = PT.calculate_position(data)
        print 'rundemo.py:current_pos:',current_pos
        err.record("rundemo.py:current_pos", current_pos)


        # add data to the window
        window.update_window(current_pos)
        samples_since_last_gr += 1
        if (samples_since_last_gr >= gr_frequency) and inRecovery:
            samples_since_last_gr = 0
            inRecovery = False
            GD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5, "__")
            f2.write("WINDOW SKIP")
        elif (samples_since_last_gr >= gr_frequency):
            print " ----- Retrieving gesture ----- "
            print window
            samples_since_last_gr = 0
            gest = gestanalyzer.get_gesture(window)
            if gest is None:
                gest = ""
            else:
                window.clear()
                inRecovery = True
            print gest
            GD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5,gest + str(window_counter))
            print "Window counter: ", window_counter
            f2.write(gest + "\t" + str(window_counter) + "\n")
            window_counter += 1
            if (gest in Keynote):
                pymachid.PyMacHID.pressKey(Keynote[gest])

        else:
            GD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5, "__")

        # # update the demo display
        # CD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5)

        # Record data on any key press
        if event.type == pg.KEYDOWN:
            # Reset pipeline
            # P.recalibrate_pipeline()
            #f.write(str(data) + "\t" + str(current_pos) + "\n")
            # f.write("Pgm time:" + str(now) + "\n")
            # f.write(str(err))
            print "RECORD"

        now = time.time()

        # quit on mouse click
        if event.type == pg.MOUSEBUTTONDOWN:
            print P.freq_ctr
            print "Ending upon user instruction."
            break

    print "DONE", "(pgm end time: ", time.time(), ")" 

if __name__ == '__main__':
    main()
