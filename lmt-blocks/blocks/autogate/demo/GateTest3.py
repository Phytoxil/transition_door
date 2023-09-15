'''
Created on 8 oct. 2021

@author: Fab
'''

import time
from blocks.autogate.Gate import Gate, GateOrder
from blocks.FED3.Fed3Manager import Fed3Manager

import threading
import logging
import sys

if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout, level=logging.INFO )
    
    print( "Testing.")
    
    # self.lock = threading.Lock()

    gate1 = Gate( 
        COM_Servo = "COM69", 
        #COM_Balance= "COM81", 
        #COM_RFID = "COM82", 
        name="First Gate",
        weightFactor = 0.74 )
    
    gate1.setSpeedAndTorqueLimits(100, 100)
    
    gate1.setOrder( GateOrder.OPEN_CLOSE_HABITUATION )
    
    '''
    gate2 = Gate( 
        COM_Servo = "COM70", 
        #COM_Balance= "COM81", 
        #COM_RFID = "COM82", 
        name="Second Gate",
        weightFactor = 0.74 )
    
    gate2.setSpeedAndTorqueLimits(100, 100)
    
    gate2.setOrder( GateOrder.OPEN_CLOSE_HABITUATION )
    
    fed = Fed3Manager( "COM44", "44" )
    
    def monitorG1():
        while(True):
            gate1.open()
            time.sleep( 3 )
            gate1.close()
            time.sleep( 3 )
            
    def monitorG2():
        while(True):
            gate2.open()
            time.sleep( 3 )
            gate2.close()
            time.sleep( 3 )
            
    def monitorFED():
        while(True):
            fed.read()
            time.sleep( 0.1 )
            
    
    def listener( event ):
        print( event )
        
    gate1.addDeviceListener( listener )
    gate2.addDeviceListener( listener )
    fed.addDeviceListener(listener)
        
    
    #threadG1 = threading.Thread( target=monitorG1 )
    #threadG1.start()
    
    #threadG2 = threading.Thread( target=monitorG2 )
    #threadG2.start()
    
    
    threadFED = threading.Thread( target=monitorFED )
    threadFED.start()
    '''
    
    while True:
        '''
        fed.read()
        gate1.open()
        gate2.open()
        time.sleep(3)
        gate1.close()
        gate2.close()
        '''
        time.sleep(5)
        print("running...")
    
    
    
    
    
    