# http://stackoverflow.com/questions/281133/controlling-the-mouse-from-python-in-os-x

'''
pymachid.py

The PyMacHID class is a collection of static methods for controlling the Mac
operating system. This implements keypresses, mouse movements, and mouse clicks

'''

from Quartz.CoreGraphics import CGEventCreateMouseEvent
from Quartz.CoreGraphics import CGEventPost
from Quartz.CoreGraphics import kCGEventMouseMoved
from Quartz.CoreGraphics import kCGEventLeftMouseDown
from Quartz.CoreGraphics import kCGEventLeftMouseDown
from Quartz.CoreGraphics import kCGEventLeftMouseUp
from Quartz.CoreGraphics import kCGMouseButtonLeft
from Quartz.CoreGraphics import kCGHIDEventTap
from Quartz import CGEventCreateKeyboardEvent, CGEventSetFlags, kCGHIDEventTap, CGEventPost
import time

class PyMacHID:
    KEYCODE_DICT = {}

    @staticmethod
    def _populateKeycodeDict():
        # Look in: /System/Library/Frameworks/Carbon.framework/Versions/A/Frameworks/HIToolbox.framework/Versions/A/Headers/Events.h
        # for the mappings for all keys
        keycodestr = "asdfhgzxcv_bqweryt123465=97-80]ou[ip\nlj'k;\\,/nm."
        for index,item in enumerate(keycodestr):
            PyMacHID.KEYCODE_DICT[item] = index

        PyMacHID.KEYCODE_DICT["TAB"] = 48
        PyMacHID.KEYCODE_DICT[" "] = 49
        PyMacHID.KEYCODE_DICT["`"] = 50
        PyMacHID.KEYCODE_DICT["DELETE"] = 51
        PyMacHID.KEYCODE_DICT["ENTER"] = 52
        PyMacHID.KEYCODE_DICT["ESCAPE"] = 53
        PyMacHID.KEYCODE_DICT["PGUP"] = 116
        PyMacHID.KEYCODE_DICT["END"] = 119
        PyMacHID.KEYCODE_DICT["PGDN"] = 121
        PyMacHID.KEYCODE_DICT["LEFT"] = 123
        PyMacHID.KEYCODE_DICT["RIGHT"] = 124
        PyMacHID.KEYCODE_DICT["DOWN"] = 125
        PyMacHID.KEYCODE_DICT["UP"] = 126
        # TODO: Consider putting this in a separate file and just import it
        # print PyMacHID.KEYCODE_DICT

    @staticmethod
    def pressKey(char):
        if not PyMacHID.KEYCODE_DICT:
            PyMacHID._populateKeycodeDict()
        if not (char in PyMacHID.KEYCODE_DICT):
            return
        val = PyMacHID.KEYCODE_DICT[char]
        # Press the key
        # keyDown = Quartz.CGEventCreateKeyboardEvent(None,val,True)
        keyDown = CGEventCreateKeyboardEvent(None,val,True)
        # Release the key
        keyUp = CGEventCreateKeyboardEvent(None,val,False)

        # Set modflags on keyDown (default None):
        CGEventSetFlags(keyDown, 0)
        # Set modflags on keyUp:
        CGEventSetFlags(keyUp, 0)

        # post the event
        CGEventPost(kCGHIDEventTap,keyDown)
        CGEventPost(kCGHIDEventTap,keyUp)

    @staticmethod
    def _mouseEvent(type, posx, posy):
            theEvent = CGEventCreateMouseEvent(
                        None, 
                        type, 
                        (posx,posy), 
                        kCGMouseButtonLeft)
            CGEventPost(kCGHIDEventTap, theEvent)

    @staticmethod
    def mouseMove(posx,posy):
            PyMacHID._mouseEvent(kCGEventMouseMoved, posx,posy);

    @staticmethod
    def mouseClick(posx,posy):
            # uncomment this line if you want to force the mouse 
            # to MOVE to the click location first (I found it was not necessary).
            PyMacHID._mouseEvent(kCGEventMouseMoved, posx,posy);
            PyMacHID._mouseEvent(kCGEventLeftMouseDown, posx,posy);
            PyMacHID._mouseEvent(kCGEventLeftMouseUp, posx,posy);

def demo_mouseclick():
    PyMacHID.mouseMove(200,200)
    time.sleep(.5)
    PyMacHID.mouseMove(300,300)
    time.sleep(.5)
    PyMacHID.mouseMove(900,720)
    time.sleep(.5)
    PyMacHID.mouseClick(900,720)
    time.sleep(.5)
    PyMacHID.mouseClick(900,720)
    mystr = "hi there!"
    for item in mystr:
        PyMacHID.pressKey(item)
        time.sleep(.01)

def main():
    demo_mouseclick()

if __name__ == '__main__':
    main()
