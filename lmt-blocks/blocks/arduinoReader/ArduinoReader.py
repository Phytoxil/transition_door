'''
Created on 5 oct. 2021

@author: Fab
'''
import serial
import time
import threading
import logging

class ArduinoReader(object):
    
    '''
    - Manage the scale connected with an arduino nano for the gate.
    - Manage LIDAR
    '''

    def __init__(self, comPort, name , weightFactor = 1 , invertScale = False ):        
        print("Starting balance and LIDAR controller",name,"reader on port " , comPort)
        self.weightFactor = weightFactor
        self.name = name
        self.invertScale = invertScale
        self.enabled = True
        self.comPort = comPort
        self.stopped = False
        self.weight = -1
        self.lock = threading.Lock()    
        self.comPort = comPort
        self.ser = serial.Serial(comPort, 115200  )
        self.flushData()
        self.readData = []
        self.listenerList = []
        thread = threading.Thread( target=self.monitor , name = f"Thread ArduinoReader - {self.name}")
        thread.start()
    
    def monitor(self):
        
        logging.info( "Balance monitoring started" )
        
        while( self.stopped == False ):            
            
            if self.enabled:
                
                time.sleep(0.001)
                
                data = self.readInput()
                if data == None:
                    continue
                
                if "init" in data:
                    print("Balance/LIDAR : ", self.name , data )
                    continue                  
                if "ready" in data:
                    print("Balance/LIDAR : ", self.name, data )
                    continue                
                if "tare" in data:
                    print("Tare : ", self.name, ":" , data )
                    continue
                
                if "w:" in data:
                    data = data.strip()
                    try:
                        value = round( float( data[2:] ) * self.weightFactor , 2 ) 
                        self.fireWeightMeasure( value )
                    except:                        
                        logging.info("Error in weight read. Data received: " + data)
                        
                if "lidar:" in data:
                    try:
                        data = data.strip()
                        value = data[6:10] # example of message: lidar:0000"
                        #print( value )
                        self.fireLIDARMeasure( value )
                    except:
                        logging.info("Error in lidar read. Data received: " + data)
                
                #print( "received data : " , value , " grams" )
                    
    def enableReading(self, enable ):
        self.enabled = enable
        
    def addListener(self , method ):
        self.listenerList.append( method )
    
    '''        
    def sendReadOrder(self):
        self.write("RAT")
    '''
        
    def fireWeightMeasure(self , weight ):
        #logging.info(f"Current Scale {self.comPort}:{self.name}: {str(weight)}")
        if self.invertScale:
            weight=-weight
        for listener in self.listenerList:            
            listener( weight=weight )
    
    
    def fireLIDARMeasure(self , lidarValues ):
        #print( self.listenerList )
        for listener in self.listenerList:
            listener( lidar = lidarValues )         
                        
    def flushData(self):
        self.lock.acquire()
        self.ser.flushInput()
        self.lock.release()
    
    def readInput(self):
        self.lock.acquire()
        try:
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
                        '''
                        if "OK" in decoded or "?" in decoded:
                            continue
                        '''
                        if len(decoded) > 0:
                            return decoded
            return None
        finally:
            self.lock.release()
        
        
    def write( self, command ):
    
        command+="\r"
        command= command.encode("utf_8")
        self.lock.acquire()
        #print( "Sending command : " , command )
        self.ser.write( serial.to_bytes( command ) )
        self.lock.release()
    
    def tare(self):
        self.write("tare")
                
    def close(self):    
        self.stopped = True
        time.sleep( 0.1 )
        self.ser.close()
        print( "Balance " , self.name , "stopped")

if __name__ == '__main__':
    
    def listener( weight ):
        print( "Data received by listener: " , weight )
        
    print("Testing balance")
    balance = ArduinoReader("COM81" , "Testing balance")
    balance.addListener( listener )
    
    time.sleep( 60 )
    
    '''
    balance.tare()
    balance.tare()
    balance.tare()
    time.sleep( 5 )
    balance.tare()
    time.sleep( 5 )
    balance.tare()
    time.sleep( 5 )
    balance.close()
    '''
    
    
    