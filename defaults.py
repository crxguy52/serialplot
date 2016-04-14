'''
Be careful when modifying these values - if they aren't set correctly, 
the program won't run. As a precaution if you modify it, it's a good idea to 
save a copy first. serialplot just looks for a file in the same directory 
called 'defaults.py'
 
The format for graphXlineX properties is:
[datalabel,
datapos,
linecolor,
dashed,
multiplier,
offset]
'''

defaults = {'COMport': '',
 'baud': 9600,
 'databits': 8,
 'datadepth': 200,
 'datalength': 2,
 'filename': 'C:/Users/Victor/Desktop/GraphLog.csv',
 'g1ylims': [-10, 10],
 'g2ylims': [-10, 10],
 'g3ylims': [-10, 10],
 'graph1line1': ['line1', 1, '#FF0000', '-', 1, 0],
 'graph1line2': ['line2', 2, '#ff0000', '-', 1, 0],
 'graph1line3': ['line3', '-', '#00FF00', '-', 1, 0],
 'graph2line1': ['line1', 1, '#0000FF', '-', 1, 0],
 'graph2line2': ['line2', 2, '#0000FF', '-', 1, 0],
 'graph2line3': ['line3', '-', '#00FF00', '-', 1, 0],
 'graph3line1': ['line1', 1, '#FF0000', '-', 1, 0],
 'graph3line2': ['line2', 2, '#0000FF', '-', 1, 0],
 'graph3line3': ['line3', '-', '#00FF00', '-', 1, 0],
 'log2file': 'off',
 'maxlength': 50,
 'numgraphs': 3,
 'parity': 'None',
 'refreshfreq': 20,
 'startmax': 'no',
 'stopbits': 1,
 'stsbrwdth': 7}
