'''
Created on 16 mars 2022

@author: Fab
'''

import serial
from time import sleep
from blocks.DeviceEvent import DeviceEvent

class WaterPump(object):

    
    def __init__(self, comPort = "COM90" , name="WaterPump" ):
        
        self.name = name
        self.comPort = comPort 
        self.serialPort = serial.Serial( port=comPort, baudrate=115200, bytesize=8, timeout=.1 )
        
        self.nbDrop = 0
        self.deviceListenerList = []
        
        print("Waterpump init...")
        sleep( 2 ) # init of transmission
        print("Waterpump ready")
    
    def read(self):
        if self.serialPort.in_waiting > 0:
            serialString = self.serialPort.readline().decode("Ascii")
            serialString = serialString.strip()
            
            print( serialString )
            if serialString == "drop":
                self.nbDrop+=1
                
                
            print( self )            
        
    def pump( self, pwm, duration ):
        s = f"pump,{int(pwm)},{int(duration)}"
        self.send( s )
        self.fireEvent( DeviceEvent( "waterpump", self, s ) )
        print( s )
    
    '''
    def drop(self):
        self.send( "drop")
        self.fireEvent( DeviceEvent( "waterpump", self, "drop" ) )
        print( "drop")
    
    def primePump(self):
        self.send( "prime")
        self.fireEvent( DeviceEvent( "waterpump", self, "prime pump" ) )
        print("prime pump")
    '''
    
    def send(self, message ):        
        self.serialPort.write( message.encode("utf-8") )
        
    def __str__(self, *args, **kwargs):
        return "Water pump: " + self.name + " nb drop : " + str( self.nbDrop )

    def fireEvent(self, deviceEvent ):
        for listener in self.deviceListenerList:
            listener( deviceEvent )
    
    def addDeviceListener(self , listener ):
        self.deviceListenerList.append( listener )
        
    def removeDeviceListener(self , listener ):
        self.deviceListenerList.remove( listener )
