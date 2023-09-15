'''
Created on 22 févr. 2023

@author: Fab
'''
from blocks.rfidreader.AntennaRFID2 import AntennaRFID2
import time


if __name__ == '__main__':
    
    a1 = AntennaRFID2( "COM16")
    a2 = AntennaRFID2( "COM17")
    a3 = AntennaRFID2( "COM18")
    
    a1.off()
    #a2.enableReading( False )
    
    for i  in range( 1000 ):
        print( i )
        #a1.oneShotRead = True
        a2.oneShotRead = True
        a3.oneShotRead = True
        time.sleep(0.1)
    
    
    #input("Wait")