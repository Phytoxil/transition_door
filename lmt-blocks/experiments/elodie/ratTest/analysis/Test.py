'''
Created on 4 avr. 2023

@author: Fab
'''

import datetime as dt
import matplotlib.pyplot as plt

def getDateTime( line ):        
        datetime = line[0:23]
        datetime = dt.datetime.strptime(datetime,'%Y-%m-%d %H:%M:%S.%f')
        return datetime
    
if __name__ == '__main__':
    
    
    
    logFile = "habituation lever log - 2023-04-04 09h28m22s.log.txt"
    with open( logFile ) as f:
        rawlines = f.readlines()
    
    lines = []
    for line in rawlines:
        # remove non-timestamped line:
        
        getDateTime( line )
        lines.append( line.strip().lower() )
        
        
    xsL=[]
    ysL=[]
    
    xsR=[]
    ysR=[]
    
    for line in lines:
        print( line )
        if "release" in line:
            continue
        
        if "left" in line:
            xsL.append( getDateTime( line ) )
            ysL.append( 1 )
        if "right" in line:
            xsR.append( getDateTime( line ) )
            ysR.append( 2 )
        
        
    plt.scatter(xsL, ysL )
    plt.scatter(xsR, ysR )
    
    plt.show()
    
        
    