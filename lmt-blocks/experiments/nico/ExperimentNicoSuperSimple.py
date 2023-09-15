'''
Created on 3 févr. 2023

@author: eye
'''
import logging
import time
from random import randint, random
from datetime import datetime
import sys
from blocks.autogate.Gate import Gate, GateMode, GateOrder

from blocks.waterpump.WaterPump import WaterPump

from time import sleep
from blocks.FED3.Fed3Manager2 import Fed3Manager2
from experiments.elodie.ratTest.architectureExample import deviceListener
from blocks.DeviceEvent import DeviceEvent

import threading

class Experiment(object):
    
    def __init__( self , name = None ):
        
        # setup logfile
        self.logFile = "ratLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"    
        print("Logfile: " , self.logFile )    
        logging.basicConfig(level=logging.INFO, filename=self.logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))        
        logging.info('Application started')
        
        if name == None:
            name = "exp#"+str( randint( 0 , 1000 ) )
        logging.info('Experiment created: ' + name )
        
        self.initHardware()        
        self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )        
        self.results = {}        
        self.animalInRFID = None
        
        #rfids ["1234567"] = [ 1  , 2 , 5 , 9 ]        
        
        
    def initHardware(self):
        
        
        logging.info('Init hardware.')
        
        self.ratGate = Gate( 
            COM_Servo = "COM80", 
            COM_Arduino= "COM81", 
            COM_RFID = "COM82", 
            name="rat_gate",
            weightFactor = 0.63,
            mouseAverageWeight = 28, #220, #31
            #lidarPinOrder = ( 1, 0, 3 , 2 )
            enableLIDAR = False,
            invertScale = True,
            gateMode = GateMode.MOUSE
             )
                
        '''self.waterPump = WaterPump(comPort="COM6", name="WaterPump")
        
        self.fed = Fed3Manager2( comPort="COM94" , name= "Fed")
                  
        self.waterPump.addDeviceListener( self.deviceListener )  
        self.fed.addDeviceListener( self.deviceListener ) '''

        self.ratGate.addDeviceListener( self.deviceListener )
        
        self.testEnabled = False
        self.datetimeEnterTest = None
        logging.info('Hardware init done.')
        self.name="rien du tout"
        thread = threading.Thread( target=self.pingEachSecond , name = f"Thread timer")
        thread.start()


        
    def pingEachSecond(self):
        while True:
            self.deviceListener( DeviceEvent( "timer", self, "TIMER", None ) )
            sleep( 1 )
    
    def stopTest(self):
        self.testEnabled = False
        self.fed.lightoff()    
        
    def deviceListener(self , event ):
        
        print( event )
        logging.info( "--->" + str(event) )
        
        if "TIMER" in event.description:
            if self.datetimeEnterTest != None:
                currentTime = datetime.now()
                durationS = ( currentTime - self.datetimeEnterTest ).seconds
                print( f"durationS : {durationS} / 15" )
                if durationS > 15:
                    self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                    self.stopTest()
                    self.datetimeEnterTest = None
                return
        
        if "NO_ORDER" in event.description and self.ratGate.getOrder() == GateOrder.ALLOW_SINGLE_B_TO_A:
            self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )            
        
        if "Animal allowed to cross" in event.description:            
            rfid = event.data            
            if "SIDE A" in event.description:
                logging.info( f"Animal {rfid} is going to the house")
                self.animalInRFID = None
                self.testEnabled = False
                
                
            if "SIDE B" in event.description:                
                logging.info( f"Animal {rfid} is going to the test chamber")
                self.animalInRFID = rfid
                if not rfid in self.results:
                    self.results[rfid]= {}
                    self.results[rfid]["phase1"]= [0]
                    self.results[rfid]["phase2"]= [0]
                    self.results[rfid]["phase3"]= [0]
                    self.results[rfid]["currentPhase"] = "phase1"
                    
                phase = self.results[rfid]["currentPhase"]
                self.results[rfid][phase].append( 0 )
                self.datetimeEnterTest = datetime.now()


                                
        if "Checking RFID: Can't read ID of animal" in event.description:
            logging.info("BIG PROBLEM: CANT READ RFID")
           
        

            
                        
if __name__ == '__main__':
    
    experiment = Experiment()
    
    while ( True ):
        #print( experiment.ratGate.currentWeight )
        sleep( 1)




































if __name__ == '__main__':
    
    experiment = Experiment()
    
    MAX_NUMBER_REWARDS_PHASE1 = 80
        
    while( True ):
    
        experiment.runLogic()
        sleep( 0.05 )
    
    
    
    
    
