'''
Created on 24 sept. 2021

@author: Fab
'''
import serial
import time
import threading
import logging


class AntennaRFID2(object):
    
    def __init__(self, comPort, startReading = True ):
    
        self.stopped = False
        self.frequency = 0
        self.lock = threading.Lock()    
        self.comPort = comPort
        self.ser = serial.Serial( self.comPort, 9600,bytesize=serial.EIGHTBITS,
                        stopbits=serial.STOPBITS_ONE,parity=serial.PARITY_NONE, 
                        xonxoff=True, writeTimeout = 0  )
        print( "Starting RFID antenna :", self.ser.name )
        self.write( "ST2" ) # Set read animal tags.
        self.write( "SB1" ) # Disable read buzzer
        self.write( "SL4" ) # Leds off
        self.switchOff()
        self.readData = []
        self.cr = serial.to_bytes("\r".encode("utf-8"))
        self.enableReading( startReading )
        self.listenerList = []
        self.oneShotRead = False
        thread = threading.Thread( target=self.monitor , name= f"Thread AntennaRFID - {comPort}")
        thread.start()
    
    def enableReading(self, enable ):
        self.enabled = enable
        
    def addListener(self , method ):
        self.listenerList.append( method )
    
    def monitor(self):
                
        while( self.stopped == False ):            
        
            while( self.oneShotRead == False ):
                pass
                #time.sleep(0.0001)
            
            #print("reading " + self.comPort )                
            
            if self.enabled:
                #print( "on " + self.comPort )
                self.switchOn()
                time.sleep(0.1)
                self.sendReadOrder()
                #print( "read order " + self.comPort )
                self.readDataSerial()
                #print( "read serial " + self.comPort )
                #self.ser.flushInput()
                self.switchOff()
                self.switchOff()
                self.switchOff()
                #print( "off " + self.comPort )
            else:
                self.switchOff()
                self.ser.flushInput()
                time.sleep(0.1)
                
            self.oneShotRead = False                        
            
    def off(self):
        self.switchOff()
        self.ser.flushInput()
            
    def sendReadOrder(self):
        self.write("RAT")
        
    def fireRFIDFound(self , rfid ):
        for listener in self.listenerList:
            #logging.info("Sending RFID fire to listeners: " + str( listener ) )
            listener( rfid )
        
    def readDataSerial(self):
        #print("Read data")
        
        r = self.readInput()        
        if r != None:
            for s in r.split("_"):
                if len(s)==12:
                    print("RFID found " + self.comPort + " : ", s )
                    self.fireRFIDFound( s )
        
        
        
    def flushData(self):
        self.ser.flushInput()
    
    def readInput(self):
        
        bytesToRead = self.ser.inWaiting()
        if bytesToRead > 0: 
            data = self.ser.read_all()
            #print( data )
            for b in data:
                #print ( b )
                if b!=13:
                    self.readData.append( b )
                else:                    
                    decoded = "".join(map(chr, self.readData))
                    #print("Data is  : " , decoded )
                    self.readData = []
                    if "OK" in decoded or "?" in decoded:
                        continue
                    if len(decoded) > 0:
                        return decoded
        return None
        
    def readFrequency(self):
        self.switchOn()
        time.sleep(0.3)
        self.flushData()
        self.write("MOF")
        time.sleep(2)
        
        decode = self.readInput()
        if decode != None:
            print( "Frequency : " , decode )
            self.frequency = float( decode )
        else:
            print("Can't read frequency")
                        
        self.switchOff()
        
    def write( self, command ):
    
        command+="\r"
        command= command.encode("utf_8")
        #print( "Sending command : " , command )
        self.ser.write( serial.to_bytes( command ) )
    
    def switchOn(self):
        self.write("SRA")
        
    def switchOff(self):
        self.write("SRD")
        
    def close(self):    
        self.stopped = True
        time.sleep( 0.1 )
        self.ser.close()

if __name__ == '__main__':
    
    def method( value ):
        print( "Data received from RFID reader: " , value )        
    
    antenna = AntennaRFID( "COM82" )
    '''
    antenna = AntennaRFID( "COM40" , startReading=False )
    '''
    antenna.readFrequency()
    
    antenna.addListener( method )
    
    time.sleep( 60 )
    
    antenna.close()
    
    
    
    
    
    print("Done")