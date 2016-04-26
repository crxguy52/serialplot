# serialplot
A python 2.7 application that plots serial data in real time. Useful for visualizing data from microcontrollers. Originally written for Windows, others have used on linux

#Requirements
Python 2.7 - Matplotlib uses Python 2 for the tkinter widget, which means serialplot is limited to Python 2 as well. Serialplot was written to be compatable with Python 3 where applicable, whenever matplotlib updates.

Pyserial - Obviously

matplotlib - I used matplotlib's animate function to draw the graphs. It would definitely be faster to draw the plots using a tk canvas, but I'm also lazy.

#Testing in Linux

You can bind the serial port with the following command.

    socat -d -d PTY,raw PTY,link=/dev/ttyS10

The socat utility will make the /dev/ttyS10 device ready for data, and the
program will list it correctly in the main GUI combobox.

Then you can start the program, and open the main graph. In another terminal,
you can then run this python script to send data to be plotted in the graph.

```
import serial

ser = serial.Serial('/dev/ttyS10',rtscts=True, dsrdtr=True)
# The length of the payload must be less than or equal to the value in your defaults.py
ser.write("1,-1                                                                           ".encode())
```

And you should see the value in the graph. Keep sending data, and the values will be
updated.
