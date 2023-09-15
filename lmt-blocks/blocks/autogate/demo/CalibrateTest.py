'''
Created on 23 sept. 2021

@author: Fab
'''
from LMT.autodoor.Gate import Gate, GateOrder
import time

if __name__ == '__main__':
    
    print( "Calibrate gate.")

    gate = Gate( 
        COM_Servo = "COM80", 
        name="First Gate" )
    
    gate.autoCalibrate()
    
    
    gate.setSpeedAndTorqueLimits(100, 100)
    
    while True:
        
        gate.open()
        time.sleep(10)
        gate.close()
        time.sleep(10)
    
    # will never be called
    gate.stop()
    
    
    
    