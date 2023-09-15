'''
Created on 8 oct. 2021

@author: Fab
'''
from LMT.autodoor.Gate import Gate, GateOrder
import time

if __name__ == '__main__':

    
    print( "Testing 2 gates.")

    gate1 = Gate( 
        COM_Servo = "COM80", 
        COM_Balance= "COM81", 
        COM_RFID = "COM82", 
        name="First Gate",
        weightFactor = 0.74 )
    

    gate2 = Gate( 
        COM_Servo = "COM85", 
        COM_Balance= "COM86", 
        COM_RFID = "COM87", 
        name="Second Gate",
        weightFactor = 0.65 )
    
    gate1.setSpeedAndTorqueLimits(150, 150)
    gate2.setSpeedAndTorqueLimits(150, 150)
    
    while True:
        
        gate1.open()
        gate2.open()
        time.sleep(10)
        gate1.close()
        gate2.close()
        time.sleep(10)
    
    
        
    
    
    