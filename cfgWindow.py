import sys
if sys.version_info[0] < 3:
    #If we're executing with Python 2
    import Tkinter as tk
    import tkMessageBox as messagebox
    import ttk
    import tkFileDialog as filedialog
    import tkColorChooser as colorchooser
else:
    #Otherwise we're using Python 3
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import colorchooser

from graphWindow import *  
import serial.tools.list_ports  
import idlelib.ToolTip as tt
import pprint
from defaults import defaults

class ConfigFrame(ttk.Frame):
    """
    Main application Frame. Houses all the individual objects (classes) that
    make up the application
    """
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self['padding'] = '4'
        
        self.TKvariables = {}
        
        #Read in the defaults
        for key in defaults:
            
            if key[0:5] == 'graph' or key.find('ylims') >= 0:
                self.TKvariables.update({key:[]})
                
                for val in range(len(defaults[key])):
                    self.TKvariables[key].append(tk.StringVar(value=defaults[key][val]))
                    
            else:
                self.TKvariables.update({key:tk.StringVar(value=defaults[key])})      
        
        num_vars = int(self.TKvariables['datalength'].get())
        self.datalist = list(range(1,num_vars+1))
        
        #Create a combobox containing the available COM ports        
        comlst = self.get_comlst()
        self.COMbox = ttk.Labelframe(self, text='COM port to source data from')
        self.COMcombo = ttk.Combobox(self.COMbox,  width=60, values=comlst, \
            state='readonly', textvariable=self.TKvariables['COMport'],\
            postcommand=self.updateCOMbox )
        self.COMbox.grid(row = 0, column = 0, columnspan = 5)
        self.COMcombo.grid()
        
        #Create an "about" text box
        ABOUTframe = ttk.LabelFrame(self, text = 'What it does')
        ABOUTlabel = ttk.Label(ABOUTframe, text= \
            'Graphs data coming in over the serial port in a comma '
            'seperated variable string. Hover over each option to get ' 
            'a description of what the setting does', wraplength = 140)
        ABOUTframe.grid(row=1, column = 0, rowspan = 2, columnspan = 2, \
            sticky = 'nw, se', padx= 3, pady = 5)
        CreateToolTip(ABOUTlabel,\
        "The default values can be changed by opening defaults.py with a text "
        "editor and changing the values")
        ABOUTlabel.pack()        
        
        #Create a Graph! and About buttons
        GObut = ttk.Button(self, text='Go!', command=self.goButton)
        GObut.grid(row=6, column = 0, sticky = 'we')
        #GObut.tip = tt.ListboxToolTip(GObut, ["Run this motherfucker"])
        ABOUTbut = ttk.Button(self, text='About', command=self.aboutButton) 
        ABOUTbut.grid(row = 6, column = 1, sticky = 'we')
        
        #Create an instance of the class for the config panel
        notebook = ConfigNotebook(self, self)
        
        #Update the state of the graphs based on the defaults and grid
        notebook.updateGraphs()     
        notebook.grid(row=1, column=3, columnspan=2, rowspan=6, sticky = 'nsew', \
                padx = 5, pady = 5)
        
        #Bind the enter key to start the program
        self.parent.bind("<Return>", lambda event:self.goButton())
                
    def getfilename(self):
        if self.TKvariables['log2file'].get() == 'on':
            #Only pop up with the dialog when the box is checked
            options = {}
            options['filetypes'] = [('Comma Seperated Variable', '.csv')]
            options['initialfile'] = 'GraphLog.csv'
            self.TKvariables['filename'].set(filedialog.asksaveasfilename(**options))             
            
    def goButton(self):
        self.parent.variables = {}

        for key in self.TKvariables:
            if key[0:5] == 'graph' or key.find('ylims') >= 0:
                self.parent.variables.update({key:[]})
                for val in range(len(self.TKvariables[key])):
                    self.parent.variables[key].append(self.TKvariables[key][val].get())
            else:
                self.parent.variables.update({key:self.TKvariables[key].get()})
                
        #msg = ''
        #for key in self.parent.variables:
        #    msg += str(key)+':'+str(self.parent.variables[key])+'\n'
        #messagebox.showinfo(message=msg)    
        
        if self.parent.variables['COMport'] == '':
            messagebox.showerror(message='Select a COM port!')
        else:
            try:
                #Try to open the COM port first to make sure it's available                
                s = serial.Serial(port=self.parent.variables['COMport'][0:4])
                s.close()              
                GraphTopLevel(self.parent)
            except:
                #Otherwise the port isn't available, so error out
                messagebox.showerror(message='COM port not available')
    
    def aboutButton(self):
        toplvl = tk.Toplevel()
        toplvl.title('About')
      
        txt = ttk.Label(toplvl, wraplength=450, text= \
        "This program was written by Victor Zaccardo as a way to familiarize "
        "myself with Python, and also so I don't have to try and read a serial"
        " terminal every time I want to visualize data coming out of a "
        "microcontroller. It's written in Python 2.7, using tkinter, "
        "matplotlib, and pyserial. \n \n I hope it can be helpful with your "
        "embedded projects. If you have any questions or comments, feel free "
        "to contact me at victorzaccardo@gmail.com. Happy plotting!")
        txt.grid(row=0, column=0, padx=5, pady=5)
        
        closeButton = ttk.Button(toplvl, text='Close', command=toplvl.destroy)
        closeButton.grid(row=1, column=0, pady = 3)
        
        toplvl.update()
        scrwidth = toplvl.winfo_screenwidth()
        scrheight = toplvl.winfo_screenheight()
        winwidth = toplvl.winfo_reqwidth()
        winheight = toplvl.winfo_reqheight()
        winposx = int(round(scrwidth/2 - winwidth/2))
        winposy = int(round(scrheight/2 - winheight/2))
        toplvl.geometry('{}x{}+{}+{}'.format(winwidth, winheight, winposx, winposy))  
        
    def get_comlst(self):  
        """Returns a list of available COM ports with description"""
        comports = serial.tools.list_ports.comports()
        comlst = []    
        
        for item in comports:
            name = item[0]
            
            if len(item[1]) > 50:
                description = item[1][0:44] + "..."
            else:
                description = item[1]
                
            comlst.append(str(name + " - " + description))
        
        return sorted(comlst)
        
    def updateCOMbox(self):
        self.COMcombo['values'] = self.get_comlst()
        
class ConfigNotebook(ttk.Notebook):
    """
    A notebook that houses all the configuration for the program. Calls classes
    that configure each tab individually and places them in the notebook.
    Note on the controller - it's the top level of the application (an instance
    of MainApplication). It will have a dictionary that houses all the
    TKvariables, makes accessing them easier.
    """
    def __init__(self, parent, controller):
        
        ttk.Notebook.__init__(self, parent)
        self.controller = controller

        datalist = list(range(1,7))
        datalist.insert(0,'-')
        
        #Create the pages
        serialcfgframe = SerialTab(self, self.controller)
        datacfgframe = DataTab(self, self.controller)
        graph1frame = GraphTab(self, self.controller, 1)
        graph2frame = GraphTab(self, self.controller, 2)
        graph3frame = GraphTab(self, self.controller, 3)
            
        #Add them to the notebook
        self.add(datacfgframe, text='Data')            
        self.add(serialcfgframe, text='Serial')
        self.add(graph1frame, text='Graph 1')
        self.add(graph2frame, text='Graph 2')
        self.add(graph3frame, text='Graph 3')
        
    def updateGraphs(self, *args, **kwargs):
        num_graphs = int(self.controller.TKvariables['numgraphs'].get())
        
        #First, disable all the graphs
        for i in range(2, 5):
            self.tab(i, state='disabled')
        
        #Now, re-enable based on how many graphs are selected
        if num_graphs >= 1:
            self.tab(2, state='normal')
        if num_graphs >= 2:
            self.tab(3, state='normal')
        if num_graphs >= 3:
            self.tab(4, state='normal')


class SerialTab(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self['padding'] = [0, 7, 0, 0]
        
        #Populate the serial configuration tab        
        self.baudlist = (4800, 9600, 19200, 38400, 57600, 115200, 230400, 921600)
        self.databitslist = (7, 8)
        self.stopbitslist = (1, 2)
        self.paritylist = ('None', 'Even', 'Odd', 'Mark', 'Space')
        
        baudlabel = ttk.Label(self, text='Baudrate')
        baudbox = ttk.Combobox(self, width=8, values=self.baudlist, 
                        textvariable=self.controller.TKvariables['baud'])
        datalabel = ttk.Label(self, text='Data bits')
        databox = ttk.Combobox(self, width=8, values = self.databitslist, \
                        textvariable=self.controller.TKvariables['databits'])            
        stopbitslabel = ttk.Label(self, text='Stop bits')
        stopbitsbox = ttk.Combobox(self, width=8, values=self.stopbitslist, \
                        textvariable=self.controller.TKvariables['stopbits'])          
        paritylabel = ttk.Label(self, text='Parity')
        paritybox = ttk.Combobox(self, width=8, values=self.paritylist, \
                        textvariable=self.controller.TKvariables['parity'])
        
        #ttk.Label(self, text='            ').grid(row=1, column=0)                
        baudlabel.grid(row=1, column = 1, padx=5)
        baudbox.grid(row=1, column=2, padx=5)
        datalabel.grid(row=2, column = 1, padx=5)
        databox.grid(row=2, column=2,  padx=5)
        stopbitslabel.grid(row=3, column = 1,  padx=5)
        stopbitsbox.grid(row=3, column=2,  padx=5)
        paritylabel.grid(row=4, column = 1,  padx=5)
        paritybox.grid(row=4, column=2,  padx=5)


class DataTab(ttk.Frame):
    """
    Houses configuration for the incoming data
    """
    def __init__(self, parent, controller):
        
        ttk.Frame.__init__(self, parent)
        self['padding'] = 4   
        self.parent = parent
        self.controller = controller
        
        self.datalist = list(range(1,11))       
        self.terminatorlist = ['\\n', ';', '\\n;']  
        self.numgraphslist = list(range(1,4))
        
        #How long is the data coming in?
        datalabel = ttk.Label(self, text='Variables per line')
        databox = ttk.Combobox(self, width=8, values = self.datalist, \
                        textvariable=self.controller.TKvariables['datalength'])
        tt.tip = tt.ListboxToolTip(datalabel,\
        ["The number of", "TKvariables coming", 'in per line. ', 'for example, ',\
        't, data1, data2;', 'would have 3 TKvariables', 'and be terminated', \
        'by a semicolon'])
        CreateToolTip(datalabel,\
        "The numbder of variables per line. "
        "A line is a series of variables seperated by a comma, and terminated by a \\n character. "
        "For example, the line: data1, data2, data3\\n would have 3 variables. "
        "All data recieved must be a string, no binary numbers allowed")
        
        maxlabel = ttk.Label(self, text='Max Message Length')
        maxbox = ttk.Entry(self, width=11, \
            textvariable=self.controller.TKvariables['maxlength'])
        CreateToolTip(maxlabel, \
        'The maximum length of one line (in characters). If anything '
        'be conservative with this number, err on the high side. The program reads '
        'lines from the serial buffer until it is below this number of characters, to avoid '
        'a condition where it tries to read a line out of the serial buffer and a \\n '
        "can't be found"
        )
        
        numgraphslabel = ttk.Label(self, text='Number of graphs')
        numgraphsbox = ttk.Combobox(self, width=8, values=self.numgraphslist, \
            textvariable=self.controller.TKvariables['numgraphs'])
        numgraphsbox.bind('<<ComboboxSelected>>', self.parent.updateGraphs)
        CreateToolTip(numgraphslabel,\
        "The number of graphs to plot data on")
        
        maxcheck = ttk.Checkbutton(self, text='Start Maximized?', \
        variable=self.controller.TKvariables['startmax'], \
            onvalue='yes', offvalue='no')
        CreateToolTip(maxcheck, \
        "When the graph is started, the window will be maximized.")
            
        log2filecheck = ttk.Checkbutton(self, text='Log to file?',\
            variable=self.controller.TKvariables['log2file'], onvalue='on', \
            offvalue='off', command=self.controller.getfilename)
        CreateToolTip(log2filecheck, \
        "If checked, all data recieved will also be logged to a CSV file")
        
        AObutton = ttk.Button(self, text='Advanced Options', command=self.AObutton)
                                    
        datalabel.grid(row=1, column = 1, sticky='w')
        databox.grid(row=1, column = 2, sticky='w', padx=7)
        maxlabel.grid(row=2, column=1, sticky='w')
        maxbox.grid(row=2, column=2, sticky='w', padx=7)
        numgraphslabel.grid(row=3, column=1, sticky='w')
        numgraphsbox.grid(row=3, column=2, sticky='w', padx=7)
        maxcheck.grid(row=4, column=1, columnspan=2, sticky='w')
        log2filecheck.grid(row=5, column=1, columnspan=2, sticky='w')
        AObutton.grid(row=6, column=1, columnspan=2, sticky='ew')
        
    def AObutton(self):
        toplvl = tk.Toplevel()
        toplvl.withdraw()
        frame = ttk.Frame(toplvl, padding=[4, 4, 4, 4])
        boxwidth = 8
        boxpadx = 5
        TKvars = self.controller.TKvariables
        
        #Data Depth
        datalabel = ttk.Label(frame, text='Data History Depth')
        databox = ttk.Entry(frame, width=boxwidth, textvariable=TKvars['datadepth'])
        datapostlbl = ttk.Label(frame, text='Lines')
        datalabel.grid(row=0, column=0, sticky='e')
        databox.grid(row=0, column=1, sticky='ew', padx=boxpadx)
        datapostlbl.grid(row=0, column=2, sticky='w')         
        CreateToolTip(datalabel, \
        'How many lines of data to plot on the x axis. More = longer history '
        'displayed on the screen')

        #Refresh Frequency
        refreshlabel = ttk.Label(frame, text='Refresh Frequency')
        refreshbox = ttk.Entry(frame, width=boxwidth, textvariable=TKvars['refreshfreq'])
        refreshpostlbl = ttk.Label(frame, text='Hz')
        refreshlabel.grid(row=1, column=0, sticky='e')
        refreshbox.grid(row=1, column=1, sticky='ew', padx=boxpadx)
        refreshpostlbl.grid(row=1, column=2, sticky='w')   
        CreateToolTip(refreshlabel, \
        'How often to redraw the screen. Any value higher than what your PC '
        'can do will just max out the process. A reasonable value to start '
        'with is 20')

        #Data Width
        widthlabel = ttk.Label(frame, text='Statusbar Data Width')
        widthbox = ttk.Entry(frame, width=boxwidth, textvariable=TKvars['stsbrwdth'])
        widthpostlbl = ttk.Label(frame, text='Chars')
        widthlabel.grid(row=2, column=0, sticky='e')
        widthbox.grid(row=2, column=1, sticky='ew', padx=boxpadx)
        widthpostlbl.grid(row=2, column=2, sticky='w')   
        CreateToolTip(widthlabel, \
        'This is for keeping the "last line recieved" value in the statusbar'
        'a constant width. If you find that the statusbar is jumping around, '
        'increase this value')

        #Set as defaults
        defaultbutton = ttk.Button(frame, text='Set selections as defaults', \
            command=self.setDefaults)
        defaultbutton.grid(row=3, column=0, columnspan=1, pady=1, sticky='ww')
        CreateToolTip(defaultbutton, \
        'Set ALL the current settings as the defaults')
        
        #OK button
        OKbutton = ttk.Button(frame, text='OK', width=10, command=toplvl.destroy)
        OKbutton.grid(row=3, column=1, columnspan=2, pady=1, sticky='e')
        
        frame.grid()
        toplvl.update()
        scrwidth = toplvl.winfo_screenwidth()
        scrheight = toplvl.winfo_screenheight()
        winwidth = toplvl.winfo_reqwidth()
        winheight = toplvl.winfo_reqheight()
        winposx = int(round(scrwidth/2 - winwidth/2))
        winposy = int(round(scrheight/2 - winheight/2))
        toplvl.geometry('{}x{}+{}+{}'.format(winwidth, winheight, winposx, winposy))
        toplvl.deiconify()        
        
    def setDefaults(self):
        defaultstmp = {}
        TKvars = self.controller.TKvariables

        for key in TKvars:
            if key[0:5] == 'graph' or key.find('ylims') >= 0:
                defaultstmp.update({key:[]})
                for val in range(len(TKvars[key])):
                    try:
                        defaultstmp[key].append(int(TKvars[key][val].get()))
                    except:
                        defaultstmp[key].append(TKvars[key][val].get())
                        
            elif key == 'filename':
                #There is a bug with pprint that puts a u in front of the
                #filename, so convert it to a string first
                defaultstmp.update({key:str(TKvars[key].get())})                   
            else:
                try:
                    defaultstmp.update({key:int(TKvars[key].get())}) 
                except:    
                    defaultstmp.update({key:TKvars[key].get()})   
        
        fileobj = open('defaults.py', 'w')
        header = \
        "'''\n" \
        "Be careful when modifying these values - if they aren't set correctly, \n" \
        "the program won't run. As a precaution if you modify it, it's a good idea to \n" \
        "save a copy first. serialplot just looks for a file in the same directory \n" \
        "called 'defaults.py'\n \n" \
        "The format for graphXlineX properties is:\n"\
        "[datalabel,\ndatapos,\nlinecolor,\ndashed,\nmultiplier,\noffset]\n"\
        "'''\n\n"

        fileobj.write(header)
        fileobj.write('defaults = ' + pprint.pformat(defaultstmp) + '\n')
        fileobj.close()
        
        
class GraphTab(ttk.Frame):
    def __init__(self, parent, controller, graphnum):
        
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self['padding'] = [4, 4, 0, 0]
        
        key1 = 'graph' + str(graphnum) + 'line1'
        key2 = 'graph' + str(graphnum) + 'line2'
        key3 = 'graph' + str(graphnum) + 'line3'

        data1 = self.controller.TKvariables[key1][1]
        color1 = self.controller.TKvariables[key1][2]   
            
        data2 = self.controller.TKvariables[key2][1]
        color2 = self.controller.TKvariables[key2][2]        
        
        data3 = self.controller.TKvariables[key3][1] 
        color3 = self.controller.TKvariables[key3][2]        
        
        #Create 3 comboboxes to select up to 3 datas to plot
        data1label = ttk.Label(self, text='Data 1 position in string')
        self.data1box = ttk.Combobox(self, width=3, values=self.controller.datalist, \
                        textvariable=data1, postcommand=self.updatecblist)            
        data1color = tk.Button(self, bg=color1.get(), width=1,\
            command=lambda:self.setcolor(data1color,1,1,color1))
        CreateToolTip(data1label,\
        "The position of the first value to plot in the incoming line. It is one indexed, so "
        "the first value is in position 1")
        
        data2label = ttk.Label(self, text='Data 2 position in string')
        self.data2box = ttk.Combobox(self, width=3, values=self.controller.datalist, \
                        textvariable=data2, postcommand=self.updatecblist)
        data2color = tk.Button(self, bg=color2.get(), width=1,\
            command=lambda:self.setcolor(data2color,1,2,color2))                                    
        CreateToolTip(data2label,\
        "The position of the second value in the incoming line. It is one indexed, so "
        "the first value is in position 1")       
        
        data3label = ttk.Label(self, text='Data 3 position in string')
        self.data3box = ttk.Combobox(self, width=3, values=self.controller.datalist, \
                        textvariable=data3, postcommand=self.updatecblist)
        data3color = tk.Button(self, bg=color3.get(), width=1,\
            command=lambda:self.setcolor(data3color,1,3,color3))                        
        CreateToolTip(data3label,\
        "The position of the third value in the incoming line. It is one indexed, so "
        "the first value is in position 1")   
        
        #Create an advanced options button
        AObutton = ttk.Button(self, text='Advanced Options', \
            command=lambda:self.AObutton(graphnum))
        
        data1label.grid(row=1, column = 1, columnspan=3, sticky='w', pady = 3)
        self.data1box.grid(row=1, column=4, sticky='w', padx = 5)  
        data1color.grid(row=1, column=5, padx=2)
        
        data2label.grid(row=2, column = 1, columnspan=3, sticky='w', pady = 3)
        self.data2box.grid(row=2, column=4, sticky='w', padx = 5)
        data2color.grid(row=2, column=5)   
        
        data3label.grid(row=3, column=1, columnspan=3, sticky='w', pady = 3)
        self.data3box.grid(row=3, column=4, sticky='w', padx = 5)
        data3color.grid(row=3, column=5)       
        
        #Ymin\Ymax
        key = 'g'+str(graphnum)+'ylims'
        ttk.Label(self, text='Ymin').grid(row=4, column=1, sticky='w')
        ttk.Entry(self, width=5, textvariable=self.controller.TKvariables[key][0] \
            ).grid(row=4, column=2, sticky='ew')
        ttk.Label(self, text='Ymax').grid(row=4, column=3, sticky='e', padx=3)
        ttk.Entry(self, width=6, textvariable=self.controller.TKvariables[key][1] \
            ).grid(row=4, column=4, sticky='ew', padx=5)
        
        AObutton.grid(row=5, column=1, columnspan=5, sticky='nsew', pady=6)
        
    def updatecblist(self):
        num_vars = int(self.controller.TKvariables['datalength'].get())
        self.controller.datalist = list(range(1,num_vars+1))
        self.controller.datalist.insert(0, '-')        
        self.data1box['values'] = self.controller.datalist
        self.data2box['values'] = self.controller.datalist
        self.data3box['values'] = self.controller.datalist
        
    def setcolor(self, button, graph, line, initialcolor):
        color = colorchooser.askcolor(initialcolor=initialcolor.get())
        #If the user hits cancel, the dialog returns a "Nonetype" object
        #which causes issues, so check for it:
        if isinstance(color[1], str):
            button['bg'] = color[1]
            key = 'graph'+str(graph)+'line'+str(line)
            self.controller.TKvariables[key][2].set(value=color[1])
            
    def AObutton(self, graphnum):
        toplvl = tk.Toplevel()
        toplvl.withdraw()
        frame = ttk.Frame(toplvl, padding=[2, 3, 3, 0])
        
        boxwidth = 15
        
        #Create the labels
        lbl = ttk.Label(frame, text='Label')
        CreateToolTip(lbl, \
        'This text will show up in the legend and the log file')
        lbl.grid(row=0, column=1)
        
        mult = ttk.Label(frame, text='Multiplier')
        CreateToolTip(mult, \
        'Multiply by this value')
        mult.grid(row=0, column=2)
        
        offset = ttk.Label(frame, text='Offset') 
        CreateToolTip(offset, \
        'Add this value. Happens AFTER the data is multiplied')
        offset.grid(row=0, column=3)  
        
        dashed = ttk.Label(frame, text='Dashed')
        CreateToolTip(dashed, \
        'If checked, the line will be dashed')
        dashed.grid(row=0, column=4)  
        
        ttk.Label(frame, text='Line 1').grid(row=1, column=0, padx=2)
        ttk.Label(frame, text='Line 2').grid(row=2, column=0, padx=2)
        ttk.Label(frame, text='Line 3').grid(row=3, column=0, padx=2) 

        for row in range(1,3+1):
            key = 'graph'+str(graphnum)+'line'+str(row)
            #Label
            ttk.Entry(frame, width=boxwidth, \
                textvariable=self.controller.TKvariables[key][0]).grid(row=row, column=1)
            #Multiplier
            ttk.Entry(frame, width=boxwidth, \
                textvariable=self.controller.TKvariables[key][4]).grid(row=row, column=2)
            #Offset
            ttk.Entry(frame, width=boxwidth, \
                textvariable=self.controller.TKvariables[key][5]).grid(row=row, column=3) 
            #Dashed
            ttk.Checkbutton(frame, onvalue='--', offvalue='-', \
                variable=self.controller.TKvariables[key][3]).grid(row=row, column=4)
        ttk.Button(frame, text='OK', command=toplvl.destroy).grid(row=5,\
            column=3, columnspan=2, sticky='ew', pady=4)
        
        #Center the window
        frame.grid()
        toplvl.update()
        scrwidth = toplvl.winfo_screenwidth()
        scrheight = toplvl.winfo_screenheight()
        winwidth = toplvl.winfo_reqwidth()
        winheight = toplvl.winfo_reqheight()
        winposx = int(round(scrwidth/2 - winwidth/2))
        winposy = int(round(scrheight/2 - winheight/2))
        toplvl.geometry('{}x{}+{}+{}'.format(winwidth, winheight, winposx, winposy))
        toplvl.deiconify()
        
        
class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = ttk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()
            
#If this script is executed, just run the main script
if __name__ == '__main__':
    import os
    os.system("serialplot.py")