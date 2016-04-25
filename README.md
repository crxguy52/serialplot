# serialplot
A python 2.7 application that plots serial data in real time. Useful for visualizing data from microcontrollers

#Requirements
Python 2.7 - Matplotlib uses Python 2 for the tkinter widget, which means serialplot is limited to Python 2 as well. Serialplot was written to be compatable with Python 3 where applicable, whenever matplotlib updates.

Pyserial - Obviously

matplotlib - I used matplotlib's animate function to draw the graphs. It would definitely be faster to draw the plots using a tk canvas, but I'm also lazy.
