'''
Created on 8 oct. 2021

@author: Fab
'''
from LMT.autodoor.Gate import Gate, GateOrder
import time

if __name__ == '__main__':

    
    print( "Slow mode balance.")

    gate = Gate( 
        COM_Servo = "COM80",         
        name="First Gate" )
    
    gate.setSpeedAndTorqueLimits(1000, 1000)
    
    while True:
        
        gate.open()
        time.sleep(20)
        gate.close()
        time.sleep(20)
    
    # never reached
    gate.stop()
    
    
    
    