
<h1>Intro</h1>

Thesis F2013-S2014<br>
Princeton University<br>
Advisor: Professor Naveen Verma<br>

<h1>Code</h1>

These are the final relevant files that may be useful to developing this project further.

They are the result of several iterations on different mechanisms of interaction/gesture recognition/position localization etc. I've done my best to reduce the code down to something simple and small for future applications.

<h3>Demonstration</h3>
For a demonstration of the system, please check out the following youtube videos:

Raw System Readout:
<a href="https://www.youtube.com/watch?v=tzz5eXb3yZc">https://www.youtube.com/watch?v=tzz5eXb3yZc</a>

Position Localization on ITO Display:
<a href="https://www.youtube.com/watch?v=5hDlvL9fHXY">https://www.youtube.com/watch?v=5hDlvL9fHXY</a>

Gesture Recognition + Integrated System:
<a href="http://youtu.be/z-SjWKPr0Zg">http://youtu.be/z-SjWKPr0Zg</a>
(In video, I am flipping through Keynote slides using right swipe, left swipe and tap gestures. Note the translation invariance.)

<h1>Report</h1>

The written report is in .pdf form at....TBD

<h3>Basic Information</h3>
This system detects small changes in capacitance created by the presence of a human hand. The sensors are arranged in a 2D grid with ~15cm between parallel sensors. It can localize position up to about ~20 cm away for copper sensors and ~15 cm away for ITO sensors. It can also detect proximity from about 30cm away. 

The system uses dynamic time warping for some simple gesture recognition. This algorithm was chosen because it is simple to experiment with different types of gestures and to add new gestures to our dictionary.

Thanks.

