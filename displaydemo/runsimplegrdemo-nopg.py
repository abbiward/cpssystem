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
import os
# import pygame as pg # use to keep track of user interactions
# import gesturedemo

import pymachid
# from appinterfaces import Game2048 as app
from appinterfaces import Keynote as app

# sys.path.append("/Users/aaward/Dropbox/IW")
# import configurations as config     # custom configuration parameters

def main():
    err = errorlog.ErrorLog()
    P = pipeline.Pipeline(errorlog=err, usefakedata=False) # set up pipeline and calibrate
    PT = positiontracker.PositionTracker(errorlog=err) # set up position tracker
    # gestanalyzer = gr.XYZAnalysis()
    gestanalyzer = gr.PathAnalysis()
    window = gr.Window()
    # GD = gesturedemo.GestureDemo()

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
    handPresent = False
    testGestureNow = False
    numsamplesbtgest = 0

    # set up the event loop 
    while now < end_time:
        # event = pg.event.poll()
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

        # hand present vs not present
        if (-1 in current_pos) or (1.0 in current_pos):
            if handPresent and (numsamplesbtgest > 5):
                # gesture is over
                testGestureNow = True
                f2.write("I WANT TO TEST A GESTURE\n")
                f2.write("numsamples " + str(numsamplesbtgest) + "\n")
                numsamplesbtgest = 0
                handPresent = False
                numsamplesbtgest += 1
            elif handPresent:
                # continue on our merry way, gesture might not be done
                f2.write("Potentially not done yet..." + str(current_pos) + "\n")
                f2.write("\t\t" + str(data) + "\n")
                f2.write("\t\t" + str(adcdata) + "\n")
                numsamplesbtgest += 1
            else:
                handPresent = False
                numsamplesbtgest += 1
        else:
            handPresent = True


        # add data to the window
        window.update_window(current_pos)
        samples_since_last_gr += 1
        if (samples_since_last_gr >= gr_frequency) and inRecovery:
            samples_since_last_gr = 0
            inRecovery = False
            # GD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5, "__")
            f2.write("WINDOW SKIP")
        # elif (samples_since_last_gr >= gr_frequency):
        elif testGestureNow:
            print " ----- Retrieving gesture ----- "
            print window
            x = str(window)
            samples_since_last_gr = 0
            gest = gestanalyzer.get_gesture(window)
            if gest is None:
                gest = ""
            elif gest != "still":
                window.clear()
                inRecovery = True
            print gest
            # GD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5,gest + str(window_counter))
            print "Window counter: ", window_counter
            f2.write(gest + "\t" + str(window_counter) + "\n")
            f2.write(x + "\n")
            window_counter += 1
            if (gest in app):
                pymachid.PyMacHID.pressKey(app[gest])
            testGestureNow = False

        # else:
            # GD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5, "__")

        # # update the demo display
        # CD.update_display([current_pos[0], current_pos[1]],current_pos[2]/1.5)

        # Record data on any key press
        # if event.type == pg.KEYDOWN:
            # Reset pipeline
            # P.recalibrate_pipeline()
            #f.write(str(data) + "\t" + str(current_pos) + "\n")
            # f.write("Pgm time:" + str(now) + "\n")
            # f.write(str(err))
            # print "RECORD"

        now = time.time()

        # quit on mouse click
        # if event.type == pg.MOUSEBUTTONDOWN:
            # print P.freq_ctr
            # print "Ending upon user instruction."
            # break

    print "DONE", "(pgm end time: ", time.time(), ")" 
    os.system('say "your program has finished"')

if __name__ == '__main__':
    main()
