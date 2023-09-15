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
import traceback

import threading

class Result():
    
    def __init__( self ):
        self.nbPokeOk = 0
        self.nbPokeFalse = 0
        self.duration = 0
        self.startTime = datetime.now()        
        
    def __str__(self):
        return f"Result:\tnbPokeOk:\t{self.nbPokeOk}\tnbPokeFalse:\t{self.nbPokeFalse}\tduration:\t{self.duration}"

class Experiment(object):
    
    def __init__( self , name = None ):
        
        # setup logfile
        self.logFile = "ratElodieLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"    
        print("Logfile: " , self.logFile )    
        logging.basicConfig(level=logging.INFO, filename=self.logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))        
        logging.info('Application started')
        
        self.results = {}
        
        if name == None:
            name = "exp#"+str( randint( 0 , 1000 ) )
        logging.info('Experiment created: ' + name )
        
        self.initHardware()        
        self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )        
                
        self.animalInRFID = None
        
        #rfids ["1234567"] = [ 1  , 2 , 5 , 9 ]        
        
        
    def initHardware(self):
        
        
        logging.info('Init hardware.')
        
        self.ratGate = Gate( 
            COM_Servo = "COM80", 
            COM_Arduino= "COM81", 
            COM_RFID = "COM82", 
            name="rat_gate",
            weightFactor = 0.74,
            mouseAverageWeight = 150, #220, #31
            #lidarPinOrder = ( 1, 0, 3 , 2 )
            enableLIDAR = False,
            invertScale = True,
            gateMode = GateMode.RAT
             )
                
        self.waterPump = WaterPump(comPort="COM6", name="WaterPump")
        
        self.fed = Fed3Manager2( comPort="COM94" , name= "Fed")
                  
        self.waterPump.addDeviceListener( self.deviceListener )  
        self.fed.addDeviceListener( self.deviceListener )  
        self.ratGate.addDeviceListener( self.deviceListener )
        
        self.testEnabled = False
        self.errorHoldTest = False
        self.datetimeEnterTest = None
        self.errorDateTime = None
        logging.info('Hardware init done.')
        self.name="rien du tout"
        thread = threading.Thread( target=self.pingEachSecond , name = f"Thread timer")
        thread.start()


        
    def pingEachSecond(self):
        while True:
            self.deviceListener( DeviceEvent( "timer", self, "TIMER", None ) )
            sleep( 1 )
    
    def stopTest(self ):
        
        # save duration in current result
        phase = self.results[self.animalInRFID]["currentPhase"]
        resultList = self.results[self.animalInRFID][phase]
        currentResult = resultList[-1]
        currentTime = datetime.now()
        durationS = ( currentTime - self.datetimeEnterTest ).seconds
        currentResult.duration = durationS
        
        self.testEnabled = False
        self.fed.lightoff()    
        
    def deviceListener(self , event ):
        
        #print( event )
        logging.info( "--->" + str(event) )
        
        # give a limited time to the animal to do the session
        if "TIMER" in event.description:
            
            #print( "error in test: " + str( self.errorHoldTest ) )
            
            if self.datetimeEnterTest != None:
                currentTime = datetime.now()
                durationS = ( currentTime - self.datetimeEnterTest ).seconds
                print( f"durationS : {durationS} / 60" )
                if durationS > 60:
                    self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                    self.stopTest()
                    self.datetimeEnterTest = None
                    
            
            # test if the error hold test should be over or not 
            if self.errorHoldTest:
                logging.info( "error in test: " + str( self.errorHoldTest ) )
                currentTime = datetime.now()
                durationS = ( currentTime - self.errorDateTime ).seconds
                print( durationS )                
                if durationS > 10:
                    self.errorHoldTest = False
                    
            # display results:
            
            logging.info( "---- All results:")
            for rfid in self.results:
                logging.info( rfid )
                for phase in self.results[rfid]:
                    if "phase" in phase:
                        logging.info( phase )
                        for r in self.results[rfid][phase]:
                            logging.info ( r )
            logging.info( "-----------")
            

        
        if "NO_ORDER" in event.description and self.ratGate.getOrder() == GateOrder.ALLOW_SINGLE_B_TO_A: # intercept si on a fini le programme de la porte
            self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )            
        
        if "Animal allowed to cross" in event.description:            
            rfid = event.data            
            if "SIDE A" in event.description:
                logging.info( f"Animal {rfid} is going to the house")
                self.stopTest()
                self.animalInRFID = None
                
                
            if "SIDE B" in event.description:                
                logging.info( f"Animal {rfid} is going to the test chamber")
                self.animalInRFID = rfid
                if not rfid in self.results:
                    self.results[rfid]= {}
                    self.results[rfid]["phase1"]= [Result()]
                    self.results[rfid]["phase2"]= [Result()]
                    self.results[rfid]["phase3"]= [Result()]
                    self.results[rfid]["currentPhase"] = "phase1"
                    
                phase = self.results[rfid]["currentPhase"]
                self.results[rfid][phase].append( Result() ) # on fait une nouvelle session
                self.datetimeEnterTest = datetime.now()
                self.testEnabled = True
                self.errorHoldTest = False
                self.fed.light( direction = "right" )
                                
        if "Checking RFID: Can't read ID of animal" in event.description:
            logging.info("BIG PROBLEM: CANT READ RFID")
           
        
        if self.errorHoldTest:
            if "nose poke" in event.description:
                if "right" in event.data:
                    print("poke alors qu'il a meme pas le droit (right)")
                if "left" in event.data:
                    print("poke alors qu'il a meme pas le droit (letf) et en plus c'est le mauvais trou !")
            
        if self.testEnabled == True and not self.errorHoldTest:
            
            if event.deviceObject == self.fed:
                if "nose poke" in event.description:
                    phase = self.results[self.animalInRFID]["currentPhase"]
                    resultList = self.results[self.animalInRFID][phase]
                    currentResult = resultList[-1] 

                    if "right" in event.data:
                        logging.info("pump !")
                        currentResult.nbPokeOk+=1
                        print( self.results )
                        if "phase1" in phase and resultList[-1].nbPokeOk>5:
                            self.stopTest()
                            self.results[self.animalInRFID]["currentPhase"]="phase2"
                            self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                            print("PHASE 1 COMPLETE !")
                        if "phase2" in phase and resultList[-1].nbPokeOk>8:
                            self.stopTest()
                            self.results[self.animalInRFID]["currentPhase"]="phase3"
                            self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                            print("PHASE 2 COMPLETE !")
                        
                        self.waterPump.pump( 255, 30 )
                        
                    if "left" in event.data:
                        logging.info("click !")
                        self.errorDateTime = datetime.now()
                        self.errorHoldTest = True
                        currentResult.nbPokeFalse+=1                    
                        self.fed.click()
        
            
def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        

                        
if __name__ == '__main__':

    sys.excepthook = excepthook
        
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
    
    
    
    
    
