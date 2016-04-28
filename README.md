# serialplot
A python application that plots serial data in real time. Useful for visualizing data from microcontrollers. Originally written for Windows, others have used on linux

#Requirements
Python - serialplot is written so that it can be run with py2 or py3. However, there are some issues with matplotlib and py3 on windows. See the wiki for more details.

Pyserial - Obviously

matplotlib - I used matplotlib's animate function to draw the graphs. It would definitely be faster to draw the plots using a tk canvas, but I'm also lazy.
