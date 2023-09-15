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
from experiments.elodie.ratTest.utilRatExp import *
from blocks.lever.Lever import Lever

class Result():
    
    def __init__( self ):
        self.nbPokeOk = 0
        self.nbPokeFalse = 0
        self.nbPokeWhileNotAllowed = 0
        self.duration = 0
        self.startTime = datetime.now()        
    
    def getTotal(self):
        return self.nbPokeOk + self.nbPokeFalse
    
    def __str__(self):
        return f"Result:\tnbPokeOk:\t{self.nbPokeOk}\tnbPokeFalse:\t{self.nbPokeFalse}\tduration:\t{self.duration}"

class Experiment(object):
    
    def __init__( self , name = None , startExperimentNow = True ):
        
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
        #self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )        
        self.ratGate.close()
        self.animalInRFID = None
        
        if startExperimentNow:
            self.startExperiment()
        else:
            self.pauseExperiment()
        
        thread = threading.Thread( target=self.pingEachSecond , name = f"Thread timer")
        thread.start()
        
        #self.pumpInXseconds( 5 )
    
    def startExperiment(self):
        self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )
        self.enabled = True
        
    def pauseExperiment(self):
        self.enabled = False
        self.ratGate.setOrder( GateOrder.NO_ORDER , noOrderAtEnd=True )
        
    def stop(self):
        self.ratGate.stop()        
        self.leftLever.stop()
        self.rightLever.stop()
        
    def initHardware(self):
        
        
        logging.info('Init hardware.')
        
        self.ratGate = Gate( 
            COM_Servo = "COM80", 
            COM_Arduino= "COM81", 
            #COM_RFID = "COM82", 
            name="rat_gate",
            weightFactor = 0.74,
            mouseAverageWeight = 230, #600, #150, #220, #31
            #lidarPinOrder = ( 1, 0, 3 , 2 )
            enableLIDAR = False,
            invertScale = True,
            gateMode = GateMode.RAT
             )
                
        self.waterPump = WaterPump(comPort="COM6", name="WaterPump")
        
        #self.fed = Fed3Manager2( comPort="COM94" , name= "Fed")
        self.leftLever = Lever(comPort="COM4", name="Lever left")
        self.rightLever = Lever(comPort="COM8", name="Lever right")
                  
        self.leftLever.addDeviceListener( self.deviceListener )
        self.rightLever.addDeviceListener( self.deviceListener )
        
        self.waterPump.addDeviceListener( self.deviceListener )  
        #self.fed.addDeviceListener( self.deviceListener )  
        self.ratGate.addDeviceListener( self.deviceListener )
        
        self.testEnabled = False
        self.errorHoldTest = False
        #self.inactivityBetweenTrials = False
        self.datetimeEnterTest = None
        self.errorDateTime = None
        logging.info('Hardware init done.')
        self.name="rien du tout"
        

    def pumpInXsecondsThread(self , second ):
        logging.info("Thread pump start !")
        time.sleep( second )
        logging.info("Thread pump pump pump pidou !")
        self.waterPump.pump( 255, 30 ) #one big drop
    
    def pumpInXseconds(self , second ):
        logging.info("Launching thread pump...")
        thread = threading.Thread( target=self.pumpInXsecondsThread, args=(second,) , name = f"Thread timer pump")
        thread.start()
        
        
    def pingEachSecond(self):
        while True:
            self.deviceListener( DeviceEvent( "timer", self, "TIMER", None ) )
            sleep( 1 )
    
    def getCurrentDurationInTestInS(self):
        currentTime = datetime.now()
        durationS = ( currentTime - self.datetimeEnterTest ).seconds
        return durationS
    
    def isCurrentDurationInTestOverS(self , second ):
        duration = self.getCurrentDurationInTestInS()
        if duration > second:
            return True
        else:
            return False

    def stopTest(self ):
        
        # save duration in current result
        logging.info("STOP TEST")
        logging.info(f"Current RFID: {self.animalInRFID}")
        phase = self.results[self.animalInRFID]["currentPhase"]
        resultList = self.results[self.animalInRFID][phase]
        currentResult = resultList[-1]
        currentTime = datetime.now()
        durationS = ( currentTime - self.datetimeEnterTest ).seconds
        currentResult.duration = durationS
        
        self.testEnabled = False
        self.leftLever.lightoff()
        self.rightLever.lightoff()
        
        if self.ratGate.getOrder( ) != GateOrder.ALLOW_SINGLE_B_TO_A :
            self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )    
        
    def deviceListener(self , event ):
        
        if not self.enabled:
            return
        
        #print( event )
        logging.info( "--->" + str(event) )
        rfid = "123456"
        # give a limited time to the animal to do the session
        if "TIMER" in event.description:
            
            #print( "error in test: " + str( self.errorHoldTest ) )
            
            if self.datetimeEnterTest != None:
                if self.testEnabled:
                    currentTime = datetime.now()
                    durationS = ( currentTime - self.datetimeEnterTest ).seconds
                    logging.info( f"durationS : {durationS} / {maxDurationSSessionDic[self.results[self.animalInRFID]['currentPhase']]}" )
                    if durationS > maxDurationSSessionDic[self.results[self.animalInRFID]['currentPhase']]: #check if the maximum duration of the phase is reached
                        #self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                        self.stopTest()
                        self.datetimeEnterTest = None
                    
            
            # test if the error hold test should be over or not 
            if self.errorHoldTest:
                logging.info( "error in test: " + str( self.errorHoldTest ) )
                currentTime = datetime.now()
                durationS = ( currentTime - self.errorDateTime ).seconds
                logging.info( durationS )                
                if durationS > errorHoldTestDurationDic[self.results[self.animalInRFID]['currentPhase']]:
                    self.errorHoldTest = False
                    
            
            if self.testEnabled:
                currentPhase = self.results[self.animalInRFID]['currentPhase']
                rfid = self.animalInRFID
                maxDuration = maxDurationSSessionDic[currentPhase]
                if self.isCurrentDurationInTestOverS( maxDuration ):
                    logging.info( f"[Phase:{currentPhase}/Animal:{rfid}] maxSessionTimeReached ({maxDuration}). " )
                    self.stopTest()
            
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
            currentPhase = self.results[self.animalInRFID]['currentPhase']
            if not "phase4" in currentPhase:
                self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )            
        
        #if "Animal allowed to cross" in event.description: #RFIDTODO            
        if "ALLOW_SINGLE_B_TO_A DONE" in event.description:
            #rfid = event.data
            #rfid = "123456789"
            #self.animalInRFID = rfid        
            #if "SIDE A" in event.description:
            if True:
                logging.info( f"Animal {rfid} is going to the housing compartment")
                self.stopTest()
                currentPhase = self.results[self.animalInRFID]["currentPhase"]
                resultList = self.results[self.animalInRFID][currentPhase]
                logging.info( f"test-self.animalInRFID : {self.animalInRFID}")
                logging.info( f"test-The current phase is : {currentPhase}")
                
                if "phase1" in currentPhase: 
                    if len(resultList) > MAX_NB_SESSION_PHASE1: # one session = 20 max trials                        
                        self.results[self.animalInRFID]["currentPhase"] = "phase2"
                        logging.info("PHASE 1 COMPLETE (onExit)! (number of entry in test module reached)")
                        return
                    
                if "phase2" in currentPhase:
                    
                    totalNosePokeCorrect = 0
                    for result in self.results[rfid][currentPhase]:
                        totalNosePokeCorrect+=result.nbNosePokeCorrect
                    
                    if totalNosePokeCorrect > NB_NOSE_POKE_CORRECT_PHASE2:
                        self.results[self.animalInRFID]["currentPhase"] = "phase3"
                        logging.info("PHASE 2 COMPLETE (onExit)! (number of correct poke reached)")
                    else:
                        logging.info(f"PHASE 2 not finished yet (onExit)! nb total nose poke : {totalNosePokeCorrect}")
                        
                    
                    
                if "phase3" in currentPhase: 
                    
                    logging.info(f"PHASE 3 exit")
                                        
                    totalNosePokeCorrect = 0
                    totalNosePokeTotal = 0
                    
                    pokeList = self.results[rfid]["phase3ListPoke"]
                    
                    if len(  pokeList ) > NUMBER_OF_MIN_POKE_PHASE3:
                        
                        for b in pokeList[-NUMBER_OF_MIN_POKE_PHASE3:]:
                            if b == True:
                                totalNosePokeCorrect+=1
                        
                        totalNosePokeTotal = NUMBER_OF_MIN_POKE_PHASE3
                        ratio =totalNosePokeCorrect / totalNosePokeTotal
                                                                                
                        if ratio > RATIO_PHASE3:
                            self.results[self.animalInRFID]["currentPhase"] = "phase4"
                            logging.info("PHASE 3 COMPLETE (onExit)! (ratio reached)")
                        else:
                            logging.info(f"PHASE 3 not finished yet (onExit)! ratio not ok : {ratio}")
                    else:
                        logging.info(f"PHASE 3 not enough poke in phase (onExit)!: {len(pokeList)}")
                                        
        #if "SIDE B" in event.description:                
        if "ALLOW_SINGLE_A_TO_B DONE" in event.description:
            logging.info( f"Animal {rfid} is going to the test chamber")
            self.animalInRFID = rfid
            if not rfid in self.results:
                self.results[rfid]= {}
                self.results[rfid]["phase1"]= [Result()] # phase 1: a drop each time the gate is crossed + one per nose poke (any hole)
                self.results[rfid]["phase2"]= [Result()] # phase 2: a drop each time a nose poke is done (any hole) stop session if ( 10 nose poke or timeout xx s)
                self.results[rfid]["phase3"]= [Result()] # phase 3: a drop each time a nose poke in the right side is done
                self.results[rfid]["phase4"]= [Result()] # phase 4: fin de test, attente dans la tente
                self.results[rfid]["phase3ListPoke"] = [] # list of poke with true or false in it.
                self.results[rfid]["currentPhase"] = "phase1"
                
            phase = self.results[rfid]["currentPhase"]
            self.results[rfid][phase].append( Result() ) # on fait une nouvelle session
            self.datetimeEnterTest = datetime.now()
            self.testEnabled = True
            self.errorHoldTest = False
                                
                                
        if "Checking RFID: Can't read ID of animal" in event.description:
            logging.info("BIG PROBLEM: CANT READ RFID")
           
        '''
        if "press" in event.description:
            
            self.waterPump.pump( 255, 20 )
            
            if "right" in event.deviceObject.name:
                logging.info("lever right")
                self.nbLeverRight+=1
                                
            if "left" in event.deviceObject.name:
                logging.info("lever left")
                self.nbLeverLeft+=1
                tu captes plus ?
                ca raccroche...
        '''
        if self.errorHoldTest:
            phase = self.results[self.animalInRFID]["currentPhase"]
            resultList = self.results[self.animalInRFID][phase]
            currentResult = resultList[-1]
            if "press" in event.description:
                currentResult.nbPokeWhileNotAllowed += 1
                if "right" in event.description:
                    logging.info("Poke while not allowed (right)")
                if "left" in event.description:
                    logging.info("Poke while not allowed (left)")
                
        #if "Animal allowed to cross" in event.description:        
        #if "SIDE B" in event.description:
        
        if "ALLOW_SINGLE_A_TO_B DONE" in event.description:
            phase = self.results[self.animalInRFID]["currentPhase"]
            resultList = self.results[self.animalInRFID][phase]
            currentResult = resultList[-1] 
            
            if "phase1" in phase:
                #phase 1: a drop each time the gate is crossed + one per nose poke (any hole)
                #pre-training: one drop each time the gate is crossed (animal in B)
                logging.info(f"[Phase:{phase}/Animal:{self.animalInRFID}] in B for pre-training (entry): pump! nbEntry:{len(resultList)}")
                #delayed pump action
                self.pumpInXseconds( 1 )
                
                self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                
                    
    
        if self.testEnabled == True and not self.errorHoldTest:    
            if event.deviceObject == self.leftLever or event.deviceObject == self.rightLever:
                rfid = self.animalInRFID
                if "press" in event.description:
                    phase = self.results[rfid]["currentPhase"]
                    resultList = self.results[rfid][phase]
                    currentResult = resultList[-1] 
                    
                    if "phase1" in phase:
                        #pre-training: one drop each time the gate is crossed (animal in B) and one additional drop if nose poke
                        logging.info(f"[Phase:{phase}/Animal:{rfid}] in B for pre-training (nose poke): pump!")
                        self.waterPump.pump( 255, dropSizeDic['phase1'] ) #one big drop
                        currentResult.nbPokeOk += 1
                        # de-bounce time ?
                            
                    if "phase2" in phase:
                        # phase 2: a drop each time a nose poke is done (any hole) stop session if ( 10 nose poke or timeout xx s)
                        logging.info(f"[Phase:{phase}/Animal:{rfid}] Animal {rfid} in B for training: pump!")
                        currentResult.nbPokeOk+=1
                        self.waterPump.pump( 255, dropSizeDic['phase2'] )
                        
                        if resultList[-1].nbPokeOk> MAX_NB_POKE_SESSION2:
                            self.stopTest()                            
                            self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )                            
                            logging.info("PHASE 2: Session over (nbpoke reached) !")
                    
                    if "phase3" in phase:
                                                
                        if "right" in event.description:
                            logging.info(f"[Phase:{phase}/Animal:{rfid}] nose poke proper side")
                            currentResult.nbPokeOk+=1
                            self.results[rfid]["phase3ListPoke"].append( True )
                            self.waterPump.pump( 255, dropSizeDic['phase3'] )
                            
                            
                        if "left" in event.description:
                            logging.info("click !")
                            self.errorDateTime = datetime.now()
                            self.errorHoldTest = True
                            currentResult.nbPokeFalse+=1
                            self.results[rfid]["phase3ListPoke"].append( False )                    
                            self.leftLever.click()
                        
                        if currentResult.getTotal() > maxNbTrialPerSession[phase]: 
                            self.stopTest()
            
            
def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        

                        
if __name__ == '__main__':

    sys.excepthook = excepthook
        
    experiment = Experiment( "name", startExperimentNow = True )
    
    input("Enter to start")
    experiment.startExperiment()
    
    while ( True ):
        #print( experiment.ratGate.currentWeight )
        sleep( 1)




































    
    
    
