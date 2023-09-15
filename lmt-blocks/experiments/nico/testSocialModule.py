'''
Created on 10 oct. 2022

@author: Fab
'''

import time

import logging
import sys
from blocks.autogate.MonoDoor import MonoDoor

def listener( deviceEvent ):
    print("Message received: " , deviceEvent )
    

if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout, level=logging.INFO )
    
    print( "Testing.")
    
    # self.lock = threading.Lock()

    socialBlock = MonoDoor(  COM_Servo = "COM69", name="Social block" )
    
    socialBlock.setSpeedAndTorqueLimits(100, 100)
        
    socialBlock.addDeviceListener( listener )
    
    print("running...")
    while True:
        socialBlock.close()
        time.sleep(5)
        socialBlock.open()
        time.sleep(5)
        
    
    
    
    
    
    