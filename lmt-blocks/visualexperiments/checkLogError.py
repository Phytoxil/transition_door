'''
Created on 17 mars 2023

@author: LMT_11
'''

import datetime as dt
import re

if __name__ == '__main__':
    
    def getDateTime( line ):        
        datetime = line[0:23]
        datetime = dt.datetime.strptime(datetime,'%Y-%m-%d %H:%M:%S.%f')
        return datetime
    
    logFile = "testLog - 2023-03-17 17h16m04s.log.txt"

    
    logFile = logFile
    with open( logFile ) as f:
        rawlines = f.readlines()
        
    lines = []
    for line in rawlines:
        # remove non-timestamped line:
        try:
            getDateTime( line )
            lines.append( line.strip() )
        except:
            pass
    
    rfidDic = {}
    # Animal allowed to cross: 001043406146 TO SIDE B*001043406146        
    for line in lines:
        if "blocks.autogate.Gate.Gate" in line and "Animal allowed to cross:" in line:
            '''
            if "Gate 2" in line:
                if "SIDE A" in line:
            '''                
            print ( getDateTime( line ) , line )
            rfid = line.split("*")[-1]
            if not rfid in rfidDic:
                rfidDic[rfid] = 0
            rfidDic[rfid] +=1
                        
                    
    print( rfidDic )
    print("done")
            
            
            
            
            
            
            