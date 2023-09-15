'''
Created on 21 mars 2023

@author: eye
'''
from blocks.rfidreader.AntennaRFID import AntennaRFID
import time

i = 0

def listener(deviceEvent):
    global i
    print( i , deviceEvent)
    i+=1
    
if __name__ == '__main__':
    antenna = AntennaRFID("COM82")
    antenna.readFrequency()
    antenna.addListener( listener )
    antenna.enableReading( True )
    

    print("reading...")
    input("Press enter to stop reading...")
    
    
    print("done")