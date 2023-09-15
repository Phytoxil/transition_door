'''
Created on 16 mars 2022

@author: Fab
'''

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import itertools
import numpy

    
'''
Current phase: Phase.PHASE2
SUGAR ok/wrong: (3, 7)
SOCIAL ok/wrong: (2, 11)

NB pass in sugar: 7
NB pass in social: 4

Current duration of this phase: 2:00:02.002261
Current duration of the experiment: 2:24:25.981867
'''

if __name__ == '__main__':
    
    file = 'log pb1.txt'
        
    
    with open( file ) as f:
        lines = f.readlines()
    
    i= 0
    
    for line in lines:
        line = line.strip()
        i+=1
        
        if i > 3146550 and i < 3146550+200:
            print( i, line )
        '''
        date = line[0:23]
        try:
            dateIn = dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
        except:
            print("error")
            print ( i, line )
        
        if "allowed" in line:
            dropLines = False
            startDate = dateIn
            print( line )
        
        '''
        
        
    
    
    
    
    