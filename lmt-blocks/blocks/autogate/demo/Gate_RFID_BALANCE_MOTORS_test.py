'''
Created on 8 oct. 2021

@author: Fab
'''
from LMT.autodoor.Gate import Gate, GateOrder
import time

if __name__ == '__main__':

    
    print( "Testing.")

    gate = Gate( 
        COM_Servo = "COM80", 
        COM_Balance= "COM81", 
        COM_RFID = "COM82", 
        name="First Gate" )
    
    gate.setSpeedAndTorqueLimits(100, 100)
    
    while True:
        
        gate.open()
        time.sleep(10)
        gate.close()
        time.sleep(10)
    
    # unreachable
    print("Stop")
    gate.stop()
    
    
    
    