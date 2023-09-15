'''
Created on 23 sept. 2021

@author: Fab
'''

import time
import threading

from enum import Enum
    

import numpy as np
import inspect
from datetime import datetime
import logging

from inspect import getframeinfo, stack
from blocks.autogate.Parameters import *
from blocks.autogate.Door import Door
from blocks.arduinoReader.ArduinoReader import ArduinoReader
from blocks.rfidreader.AntennaRFID import AntennaRFID
from blocks.DeviceEvent import DeviceEvent

import socket
from blocks.autogate.dxl_control.MotorManager import MotorManager
from blocks.autogate.dxl_control.Ax12Motor import Ax12Motor


    
class MonoDoor(object):
    '''
    A gate manage 2 doors
    '''

    def __init__(self, COM_Servo=None, name="noName MonoDoor" ):        
        
        print('MonoDoor init..')
        
        self.COM_Servo = COM_Servo
        self.name = name
        
        self.lock = threading.Lock()
        self.motorManager = None
        
        self.previousTime = 0
        self.deviceListenerList = []

        try:
            self.motorManager = MotorManager( COM_Servo )
        except:
            print("Quit: Can't connect motors using port: " , COM_Servo )            
            self.stop()
            quit()
            
        self.doorA = Door( Ax12Motor(1, self.motorManager) , "A "+name , self.lock, lidarEnabled = False )
        self.doorA.setLimits( OPENED_DOOR_POSITION_MOUSE, CLOSED_DOOR_POSITION_MOUSE )
        self.doorA.addDeviceListener(self.listener)        
        self.setSpeedAndTorqueLimits(DEFAULT_TORQUE_AND_SPEED_LIMIT_MOUSE, DEFAULT_TORQUE_AND_SPEED_LIMIT_MOUSE)
            
        self.stopped = False
        self.deviceListenerList = []
        
        thread = threading.Thread( target=self.monitor , name= f"MonoDoor - {self.name}" )
        thread.start()
        time.sleep(1)
        print('MonoDoor started. name=' + name )
    
    def setSpeedAndTorqueLimits(self, speedLimit , torqueLimit):
        self.doorA.setSpeedAndTorqueLimits( speedLimit , torqueLimit)
            
    def setTorqueEnabled(self, enabled ):
        self.doorA.setTorqueEnabled( enabled )
        
    def monitor(self):
        
        while( self.stopped == False ):            
            time.sleep( 0.1 )            

            # security logic for doors                        
            ms = time.time()*1000.0
            if ms-self.previousTime > 250: #1000
                self.doorA.performLogic() 
                self.previousTime = ms
                        
    def open(self):
        self.doorA.open()
        
    def close(self):        
        self.doorA.close()
        
    def listener(self , deviceEvent ):
        # repeat event:        
        self.fireEvent( deviceEvent )            
        
    def fireEvent(self, deviceEvent ):
        for listener in self.deviceListenerList:
            listener( deviceEvent )
    
    def addDeviceListener(self , listener ):
        self.deviceListenerList.append( listener )
        
    def removeDeviceListener(self , listener ):
        self.deviceListenerList.remove( listener )
    
    def stop(self):        
        self.stopped = True
        
        self.doorA.motor.disable_torque()        
        self.motorManager.close_port()
        
