'''
Created on 30 mars 2023

@author: Fab
'''


import serial
from blocks.DeviceEvent import DeviceEvent
import threading
from time import sleep
from datetime import datetime

class Lever(object):

    def __init__(self, comPort = "COM24" , name="Lever" , debounceDurationS=1 ):
        
        self.name = name
        self.comPort = comPort 
        self.serialPort = serial.Serial( port=comPort, baudrate=115200, bytesize=8, timeout=.1 )
                
        self.deviceListenerList =[]
        self.enabled = True
        
        self.readThread = threading.Thread(target=self.read , name = f"LEVER Thread - {self.comPort}")
        self.readThread.start()
        
        self.lastDownTime = datetime.now()
        self.debounceDurationS = debounceDurationS        
    
    def stop(self):
        self.enabled = False
        
    def read(self):
        
        while( self.enabled ):
        
            if self.serialPort.in_waiting > 0:
                serialString = self.serialPort.readline().decode("Ascii")        
                serialString = serialString.strip()
                
                if serialString == "release":
                    self.fireEvent( DeviceEvent( "Lever", self, "lever release", data="release" ) )
                    
                if serialString == "press":   
                    durationS = ( datetime.now() - self.lastDownTime ).seconds
                    if durationS > self.debounceDurationS:                  
                        self.fireEvent( DeviceEvent( "Lever", self, "lever press", data="press" ) )
                        self.lastDownTime = datetime.now()
                    
    def click(self ):
        
        self.send( "click")
        self.fireEvent( DeviceEvent( "Lever", self, "click" ) )
    
    def light(self , on ):
        if on:
            self.send( "light")
            self.fireEvent( DeviceEvent( "Lever", self, "lightOn" ) )
        else:
            self.send( "lightoff")
            self.fireEvent( DeviceEvent( "Lever", self, "lightOff" ) )
        
    def send(self, message ):                
        self.serialPort.write( message.encode("utf-8") )
        
    def fireEvent(self, deviceEvent ):
        for listener in self.deviceListenerList:
            listener( deviceEvent )
    
    def addDeviceListener(self , listener ):
        self.deviceListenerList.append( listener )
        
    def removeDeviceListener(self , listener ):
        self.deviceListenerList.remove( listener )
        
    def __str__(self, *args, **kwargs):
        return self.name + " " + self.comPort
    
    
    
    
    
    