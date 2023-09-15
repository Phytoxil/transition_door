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
        name="First Gate",
        weightFactor = 0.74,
        mouseAverageWeight = 7 #25
         )
    
    #gate.addAllowedRFID("0000000123")
    #gate.addForbiddenRFID("0000000007")
    
    gate.setSpeedAndTorqueLimits(200, 200)    
    gate.setOrder( GateOrder.ALLOW_A_TO_B )

    time.sleep(60*60) # 1 hour test
    print("Stop")
    gate.stop()
    
    
    
    