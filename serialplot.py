#! python3
# -*- coding: utf-8 -*-
"""
Program to plot serial data in real time.
"""
import matplotlib
matplotlib.use('TkAgg')
#import sys
#sys.dont_write_bytecode = True

from cfgWindow import *
from graphWindow import *

root = tk.Tk()

#Hide the window so we can't see it jump to the middle
root.withdraw()

#Add the configuration frame to the root
root.CfgFrm = ConfigFrame(root)
root.CfgFrm.pack(side='top', fill='both', expand=True)

#Move the root to the center of the screen
root.update()
scrwidth = root.winfo_screenwidth()
scrheight = root.winfo_screenheight()
winwidth = root.winfo_reqwidth()
winheight = root.winfo_reqheight()
winposx = int(round(scrwidth/2 - winwidth/2))
winposy = int(round(scrheight/2 - winheight/2))
root.geometry('{}x{}+{}+{}'.format(winwidth, winheight, winposx, winposy))

#Set the title and icon and stuff
root.title('Serial Plotter Configuration')
root.iconbitmap(default='graphs.ico')
root.resizable(width=False, height=False)

#Unhide the window now that it's configured
root.deiconify()

#Run the mainloop. All the other code is executed in class __init__ or event bindings
root.mainloop()