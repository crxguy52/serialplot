'''
The GraphTopLevel is a ttk.Frame class that gets packd into the root window when
the configuration is complete. All the graph updating takes place in updateGraph
'''

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

import sys
import serial
import io
import time
import os

if sys.version_info[0] < 3:
    #If we're executing with Python 2
    import Tkinter as tk
    import ttk
    import tkMessageBox as messagebox
    serialqueue = serial.Serial.inWaiting
    
else:
    #Otherwise we're using Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox    
    serialqueue = serial.Serial.inWaiting    


class GraphTopLevel:
    """
    Configures root directory for graphing - deletes config frame, adds all
    widgets necessary for graphing
    """
    def __init__(self, root):
        
        #This is the tk.Tk() root
        self.root = root
        
        #Since we're done with the serial configuration, we want to get rid of 
        #the configuration stuff. Destroy the frame.
        self.root.CfgFrm.destroy()

        #Configure the root directory to reflect the fact that it's graphing now
        self.root.title('Serial Data Live Graph')
        self.root.resizable(width=True, height=True)
        self.root.unbind("<Return>")
       

        #Change the geometry so that if the window is un-maximized, it's good
        #Move to the center of the screen
        self.root.withdraw()                
        self.root.update()
        scrwidth = self.root.winfo_screenwidth()
        scrheight = self.root.winfo_screenheight()
        winwidth = 1100
        winheight = 1000
        winposx = int(round(scrwidth/2 - winwidth/2))
        winposy = int(round(scrheight/2 - winheight/2))
        self.root.geometry('{}x{}+{}+{}'.format(winwidth, winheight, winposx, winposy))
        self.root.deiconify()

        if self.root.variables['startmax'] == 'yes':        
            #Maximize the window by default
            self.root.state('zoomed')  

        #Add the GraphFrame, which contains all the widgets we want
        self.GraphFrm = GraphFrame(self.root, self.root)
        self.GraphFrm.pack(fill='both', expand=True)            
        
        #Change the function of the X button on the upper right hand corner - 
        #Make it call a function which closes the serial port and then closes
        #the program
        self.root.wm_protocol("WM_DELETE_WINDOW", self.GraphFrm.close_prog)        

    
class GraphFrame(ttk.Frame):
    def __init__(self, parent, root):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.root = root
        
        #Create the variables for the statusbar
        self.root.variables.update({'buffsize':tk.StringVar()})
        self.root.variables.update({'lastline':tk.StringVar(value='Nothing Recieved')})
        self.root.variables.update({'refreshrate':tk.StringVar(value=0)})
        self.root.count = 0     #the number of lines we've recieved
        self.root.starttime = 0 #time when we started

        StatusBar(self, self.root).pack(fill='x', side='bottom')        
        Graph(self, self.root).pack(fill='both', expand=True, side='top')
        
    def close_prog(self):
        #Close the serial port
        self.root.ser.close()
        
        #Close the log file if it's open
        if self.root.variables['log2file'] == 'on': 
            if not self.root.logfile.closed:
                self.root.logfile.close()
            
        #Destroy the root
        self.root.destroy()

        
class Graph(ttk.Frame):
    def __init__(self, parent, root):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.root = root                

        #Create the figure object to put all the axes in        
        self.root.f = Figure(facecolor='white')
        
        #Create an empty dictionary to store the axis handles in
        self.root.ax = {}
        numgraphs = int(self.root.variables['numgraphs'])
        
        #Based on the number of graphs we want, create the axis objects
        for ax in range(1,numgraphs + 1):
            #This creates a dictionary, with the keys being character axis
            #number (ie '1', '2', etc)
        
            key = 'g'+str(ax)+'ylims'
            datadepth = int(self.root.variables['datadepth'])
            
            for lim in range(len(self.root.variables[key])):
                    self.root.variables[key][lim] = int(self.root.variables[key][lim])
                    
            lims = self.root.variables[key]
            
            self.root.ax[str(ax)] = self.root.f.add_subplot(numgraphs, 1, ax)
            self.root.ax[str(ax)].set_ylim(lims)
            self.root.ax[str(ax)].set_xlim([-datadepth, 0])
            self.root.ax[str(ax)].grid(True)
            self.root.ax[str(ax)].tick_params(axis='both', labelsize=16)
            
        #Create an empty list to store line objects in. The position in the list
        #is also the line number
        self.root.lines = []
        
        #Create an empty list to store the data position for each line
        self.root.lineDataPos = []

        #Create a list of multiplier and offsets, with position corrilating to 
        #the position of the data it will be applied to. e.g. [data1, data2]
        #would have [[multiplier1, offset,], [multiplier2, offset2]]
        self.root.dataMultOff = []
        
        #Create a list to store all the data
        self.root.data = []
        for column in range(0, int(self.root.variables['datalength'])):
            self.root.data.append([])
            #Default to a multiplier of 1, offset of zero
            self.root.dataMultOff.append([1, 0])
        
        #Set up the multiplier and offsets
        for data in range(len(self.root.data)):
            #Find if a line uses this data
            for key in self.root.variables:
                #If it does, set the position in the dataMultOff equal to
                #The multipliers in the variable       
                if key[0:5] == 'graph' and self.root.variables[key][1] != '-':
                    position = int(self.root.variables[key][1]) - 1
                else:
                    position = -1
                    
                if position == data:
                    multiplier = float(self.root.variables[key][4])
                    offset = float(self.root.variables[key][5])
                    datalbl = self.root.variables[key][0]
                    self.root.dataMultOff[data] = [multiplier, offset, datalbl]
            
        #Sort they keys, so we are always ascending
        keylst = sorted(list(self.root.variables.keys()))
        
        #Run through the variables and add only the lines and datapositions
        #we're using
        for key in keylst:
            if (key[0:5] == 'graph') and (self.root.variables[key][1] != '-'):
                #If the key is graph info AND there is a data position there, store it
                #in the arrays we created above
                graph = int(key[5])
                #linenum = int(key[10])
                datapos = int(self.root.variables[key][1])   
                
                #Add a line only if we have this number of graphs
                if int(self.root.variables['numgraphs']) >= graph:                   
                    self.root.lineDataPos.append(datapos)
                
                    #Add an empty line to the graph
                    l, = self.root.ax[str(graph)].plot([], [],\
                        color=      self.root.variables[key][2],
                        linestyle=  self.root.variables[key][3],
                        label=      self.root.variables[key][0],)
                    self.root.lines.append(l)   

        #Create the legends
        for ax in range(1,numgraphs + 1):
            handles, labels = self.root.ax[str(ax)].get_legend_handles_labels()
            self.root.ax[str(ax)].legend(handles=handles, loc='upper left')
                
        #Configure and open the serial port
        self.openSerial()
        
        #Create the initial axis objects and show the figure
        canvas = FigureCanvasTkAgg(self.root.f, master=self)  
        canvas.show()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

      
        #Start the timer for estimated update frequency
        time.clock()      
        
        #If we're recording to a csv, open it
        if self.root.variables['log2file'] == 'on':
            self.root.tmplog = ''
            self.root.prevlogtime = time.clock()
            #open and close the file in write mode so if it already exsists, 
            #delete the contents.
            f = open(self.root.variables['filename'], 'w')   
            
            #Write a header to the file so we know what gets plotted
            msg = ''
            for data in range(len(self.root.data)):
                try:
                    msg += self.root.dataMultOff[data][2] + ','
                except:
                    msg += ','
            f.write(msg)
            f.close()
                        
            #write headers so we know what the data is

        #Set up the graph update routine
        updatefreq = float(self.root.variables['refreshfreq']) #Hz 
        interval = int((1/updatefreq)*1000)
        
        try:
            self.root.ani = animation.FuncAnimation(self.root.f, self.updateGraph,\
                init_func=self.init_func, interval=interval, blit=True)
        except:
            messagebox.showerror(message='Issue starting animation')

        #Apply tight layout to reduce wasted space        
        self.root.f.tight_layout()

        #If this line isn't in here the graph shows up choppy for some reason
        #TODO Figure out why this shows up so choppy unless the window is resized 
        #This line fixed the problem previously, but after updating matplotlib
        #It ceased to fix it
        self.root.f.canvas.show()        
        
        
    def init_func(self):
        for line in self.root.lines:
            line.set_data([], [])     
        return self.root.lines


    def openSerial(self):
        #Set up the relationship between what the user enters and what the API calls for
        bytedic = {'5':serial.FIVEBITS,
                   '6':serial.SIXBITS,
                   '7':serial.SEVENBITS,
                   '8':serial.EIGHTBITS}
        bytesize = bytedic[str(self.root.variables['databits'])]
        
        paritydict = {'None':serial.PARITY_NONE,
                      'Even':serial.PARITY_EVEN,
                      'Odd' :serial.PARITY_ODD,
                      'Mark':serial.PARITY_MARK,
                      'Space':serial.PARITY_SPACE}
        parity=paritydict[self.root.variables['parity']]
        
        stopbitsdict = {'1':serial.STOPBITS_ONE,
                        '2':serial.STOPBITS_TWO}
        stopbits = stopbitsdict[str(self.root.variables['stopbits'])]
            
        #Open the serial port given the settings, store under the root
        if os.name == 'nt':
            port = self.root.variables['COMport'][0:5].strip()
            self.root.ser = serial.Serial(\
                port=port,\
                baudrate=str(self.root.variables['baud']),\
                bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=0.5) 
        else:
            first_space = self.root.variables['COMport'].index(' ')
            port = self.root.variables['COMport'][0:first_space].strip()
            # Parameters necessary due to https://github.com/pyserial/pyserial/issues/59
            self.root.ser = serial.Serial(\
                port=port,\
                baudrate=str(self.root.variables['baud']),\
                bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=0.5, rtscts=True, dsrdtr=True) 
        io.DEFAULT_BUFFER_SIZE = 5000
            
        #Purge the buffer of any previous data
        if sys.version_info[0] < 3:
            #If we're executing with Python 2
            serial.Serial.flushInput(self.root.ser)
            serial.Serial.flushOutput(self.root.ser)
        else:
            #Otherwise we're using Python 3
            serial.Serial.reset_input_buffer(self.root.ser)
            serial.Serial.reset_output_buffer(self.root.ser)
            
            
    def updateGraph(self, frameNum, *args, **kwargs):
        #Find how much stuff is in the serial buffer and update the status bar
        bufflen = serialqueue(self.root.ser)
        self.root.variables['buffsize'].set(value=str(bufflen))      
        
        #While the serial buffer lenght is greater than the threshold, read out
        #the buffer until we're below the threshold
        while int(serialqueue(self.root.ser)) >= int(self.root.variables['maxlength']):
            #Read a line
            val = str(self.root.ser.readline())
            val = val.replace('\n', '')
            val = val.replace('\r', '')
                
            #parse it, store it in a list
            val_list = val.split(',')
            
            #If the line isn't what we're expecting, discard it. It's a partial line.
            if len(val_list) != int(self.root.variables['datalength']):
                val_list = []
            
            #I had issues with some garbage making it into the serial buffer
            #and causing issues with the animation - solution is to check it
            #first
            for variable in range(len(val_list)):
                try:
                    tmp = int(val_list[variable])
                    multiplier = self.root.dataMultOff[variable][0]
                    offset = self.root.dataMultOff[variable][1]
                    val_list[variable] = tmp*multiplier + offset
                except:
                    val_list = []
                    break
                
            #Reconstruct the original string after we've applied the multipliers
            val_display_width = int(self.root.variables['stsbrwdth']) #characters
            val = val_display = ''
            for value in val_list:
                if value != val_list[len(val_list)-1]:
                    disp_len = len('{:.1f}'.format(round(value, 1)))
                    val_display += ' '*(val_display_width - disp_len) + \
                        '{:.1f}'.format(round(value, 1)) + ','
                    val += str(value)
                    val += ','
                else:
                    disp_len = len('{:.1f}'.format(round(value, 1)))
                    val_display += ' '*(val_display_width - disp_len) + \
                        '{:.1f}'.format(round(value, 1))                   
                    val += str(value)
            
            #Update the CSV once a second so we're not constantly opening and closing it
            if self.root.variables['log2file'] == 'on':    
            
                self.root.tmplog += val + '\n'

                if time.clock() >= self.root.prevlogtime + 1:
                    self.root.prevlogtime = time.clock()
                    self.root.logfile = open(self.root.variables['filename'], 'a')
                    self.root.logfile.write(self.root.tmplog)
                    self.root.logfile.close()
                    self.root.tmplog = ''
           
            for variable in range(len(val_list)):
                #If the list is greater than datadepth, remove the first row
                if len(self.root.data[variable]) > int(self.root.variables['datadepth']):
                    self.root.data[variable].pop(0)
                #Append the new data to the end
                self.root.data[variable].append(val_list[variable])         

            #Update the estimated update rate            
            self.root.count += 1
            
            #If this is the last line we're going to read, update the status bar             
            if int(self.root.variables['maxlength']) >= int(serialqueue(self.root.ser)):
               
                self.root.variables['lastline'].set(value=val_display)
                
                #Update the estimated frequency we're recieving data at
                self.root.variables['refreshrate'].set(\
                    value='{:.1f}'.format(round(self.root.count/time.clock(), 1)))

                #If we're recording everything to a spreadsheet, 
                #write the temp list to the spreadsheet
     
        #Now the data set is current we can update the graphs                              
        for line in range(len(self.root.lines)):
            datapos = self.root.lineDataPos[line] - 1
            ydata = self.root.data[datapos]
            xdata = range(-len(ydata), 0)
            self.root.lines[line].set_data(xdata, ydata)
        
        return self.root.lines

        
class StatusBar(ttk.Frame):
    def __init__(self, parent, root):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.root = root
        self['borderwidth'] = 2
        self['relief'] = 'sunken'
        
        COMlabel = ttk.Label(self, text= \
            self.root.variables['COMport'][0:5].strip() + ':')
        baudLabel = ttk.Label(self, text= \
            str(self.root.variables['baud'].strip()))
        COMlabel.pack(side='left', padx=0)
        baudLabel.pack(side='left', padx=0) 
 
        ttk.Separator(self, orient='vertical').pack(side='left', fill='y', padx=5)       
        
        buffLabel = ttk.Label(self, text='Serial Buffer:')
        buffLabel.pack(side='left', padx=0)
        
        buffBar = ttk.Progressbar(self, orient='horizontal', length=50,\
            mode='determinate', variable=self.root.variables['buffsize'],\
            maximum=io.DEFAULT_BUFFER_SIZE)
        buffBar.pack(side='left')
        
        ttk.Separator(self, orient='vertical').pack(side='left', fill='y', padx=5)
        
        lastLabel = ttk.Label(self, text='Last line Recieved: ')
        lastLabel.pack(side='left')
        lastLine = ttk.Label(self, textvariable=self.root.variables['lastline'], \
            font=('Courier', 8))
        lastLine.pack(side='left')
        
        ttk.Separator(self, orient='vertical').pack(side='left', fill='y', padx=5)
        
        updateLabel = ttk.Label(self, text='Data Recieved at: ')
        updateLabel.pack(side='left')
        updateRate = ttk.Label(self, textvariable=self.root.variables['refreshrate'])
        updateRate.pack(side='left')
        ttk.Label(self, text='Hz (Est)').pack(side='left')
        
        ttk.Separator(self, orient='vertical').pack(side='left', fill='y', padx=5)        
        
        if self.root.variables['log2file'] == 'on':
            self.root.toggleLogButton = ttk.Button(self, text='Turn Logging Off', command = self.toggleLog)
            self.root.toggleLogButton.pack(side='left')
        
    def toggleLog(self):
        if self.root.variables['log2file'] == 'on':
            #If it's on, turn it off and write a \n to seperate different logs
            self.root.variables['log2file'] = 'off'
            self.root.logfile = open(self.root.variables['filename'], 'a')
            self.root.logfile.write('\n\n')
            self.root.logfile.close()       
            self.root.toggleLogButton['text'] = 'Turn Logging On'            
        else:
            self.root.variables['log2file'] = 'on'
            self.root.toggleLogButton['text'] = 'Turn Logging Off'            
        
    def debugbutton(self):       
        width = 8
        msg = ''        
        for row in range(len(self.root.data[0])):
            for column in range(len(self.root.data)):
                element = str(self.root.data[column][row])
                if len(element) < width:
                    element += ' ' * (width - len(element))
                msg += element
                if column == len(self.root.data) - 1:
                    msg += '\n'
        #messagebox.showinfo(message=msg)
        #messagebox.showinfo(message=str(serial.Serial.inWaiting(self.root.ser)))
        #messagebox.showinfo(message=self.root.ani)
        
#If this script is executed, just run the main script
if __name__ == '__main__':
    os.system("serialplot.py")