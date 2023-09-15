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

from blocks.DeviceEvent import DeviceEvent
import traceback

import threading
from experiments.elodie.ratTest.utilRatExp import *
from blocks.lever.Lever import Lever
from mail.Mail import LMTMail

class Result():
    
    def __init__( self ):
        self.nbLeverRight = 0
        self.nbLeverLeft = 0
        self.nbPressCorrect = 0
        self.nbPressFalse = 0
        self.nbPressWhileNotAllowed = 0
        self.duration = 0
        self.startTime = datetime.now()        
    
    def getTotal(self):
        return self.nbPressCorrect + self.nbPressFalse
    
    def __str__(self):
        return f"Result:\tnbLeverRight:\t{self.nbLeverRight}\tnbLeverLeft:\t{self.nbLeverLeft}\tnbPressCorrect:\t{self.nbPressCorrect}\tnbPressFalse:\t{self.nbPressFalse}\tnbPressWhileNotAllowed:\t{self.nbPressWhileNotAllowed}\tduration:\t{self.duration}"

class Experiment(object):
    
    def __init__( self , name = None , startExperimentNow = True ):
        
    
        # setup logfile        
        self.logFile = "ratElodieLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"    
        print("Logfile: " , self.logFile )    
        logging.basicConfig(level=logging.INFO, filename=self.logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))        
        logging.info('Application started')
        
        self.results = {}
        
        self.enabled = True # force enable experiment
        
            
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
        
        self.mailInfo( "Experiment started" )
        
        #self.pumpInXseconds( 2 )
    
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
            COM_RFID = "COM82", 
            name="rat_gate",
            weightFactor = 2.14 , #2.14,
            mouseAverageWeight =  350, #350, #264, #270, #412.2, # #230, #600, #150, #220, #31
            #lidarPinOrder = ( 1, 0, 3 , 2 )
            enableLIDAR = True,
            gateMode = GateMode.RAT
             )
                
        self.waterPump = WaterPump(comPort="COM6", name="WaterPump")
        
        
        self.leftLever = Lever(comPort="COM4", name="Lever left")
        self.rightLever = Lever(comPort="COM8", name="Lever right")
                  
        self.leftLever.addDeviceListener( self.deviceListener )
        self.rightLever.addDeviceListener( self.deviceListener )
        
        self.waterPump.addDeviceListener( self.deviceListener )  
          
        self.ratGate.addDeviceListener( self.deviceListener )
        
        self.testEnabled = False
        self.errorHoldTest = False
        #self.inactivityBetweenTrials = False
        #self.datetimeEnterTest = None
        self.errorDateTime = None
        logging.info('Hardware init done.')
        self.name="RatGateExp01 #" + str ( randint(0,10000 ) )
        self.targetSide = {}
        self.reversedSide = {}
        

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
            #print( f"current Weight: {self.ratGate.currentWeight}" )
            sleep( 1 )
    
    def getCurrentDurationInTestInS(self):
        currentTime = datetime.now()
        
        currentPhase = self.results[self.animalInRFID]["currentPhase"]
        resultList = self.results[self.animalInRFID][currentPhase]
        currentResult = resultList[-1]
                
        if currentResult.startTime  != None:
            durationS = ( currentTime - currentResult.startTime ).seconds
            return durationS
        logging.info("The duration in test was not recorded. return 0")
        return 0
    
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
        #currentResult = resultList[-1]
        #currentTime = datetime.now()
        #durationS = ( currentTime - self.datetimeEnterTest ).seconds
        #currentResult.duration = durationS
        
        self.testEnabled = False
        self.leftLever.light( False )
        self.rightLever.light( False )
        
        if self.ratGate.getOrder( ) != GateOrder.ALLOW_SINGLE_B_TO_A :
            self.gateToHouse()
            #self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )   
            
    def determineTargetSide(self):
        positionInList = randint(0,1)
        targetSide = targetSideList[positionInList]
        reversedSide = targetSideList[1 - positionInList]
        return (targetSide, reversedSide)
        
    def mailInfo( self, subject, content=None , sendLog = False ):
        
        if content == None:
            content = subject
        
        mails = ["eye@igbmc.fr"]
        subject = "[Rat2Levers]"+subject + " exp:"+str( self.name ) 
        
        mail = LMTMail()
        
        files = []
        if sendLog == True:
            files.append( self.logFile )

        txt = ""
        for rfid in self.results:
            txt+= f"rfid:{rfid}"
            for phase in self.results[rfid]:
                if "phase" in phase:
                    txt+= phase+"\r"
                    for r in self.results[rfid][phase]:
                        txt+= f"{r}\r"
        
        content+= "\r"+txt
                
        mail.sendInfo(mails, subject, content, files  )
    
    def gateToHouse(self):
        self.ratGate.setRFIDControlEnabled(False)
        self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A , noOrderAtEnd=True )
    
    def gateToTest(self):
        self.ratGate.setRFIDControlEnabled(True)
        self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )
    
    def changePhase(self , newPhase ):
        logging.info (f"Change phase {self.animalInRFID} -- {newPhase}")
        self.results[self.animalInRFID]["currentPhase"] = newPhase
        self.mailInfo(f"Phase {newPhase} reached for animal {self.animalInRFID}")
    
    def saveResults(self):
        logging.info( "---- All results:")
        for rfid in self.results:
            logging.info( f"rfid:{rfid}" )
            for phase in self.results[rfid]:
                if "phase" in phase:
                    logging.info( phase )
                    for r in self.results[rfid][phase]:
                        logging.info ( r )
        logging.info( "-----------")
        
    def deviceListener(self , event ):
        
        if not self.enabled:
            return
        
        #print( event )
        if not "TIMER" in event.description:
            logging.info( "--->" + str(event) )
        
        
        if "Animal allowed to cross" in event.description:                        
            if "SIDE B" in event.description:
                self.animalInRFID = event.data
                logging.info( f"Animal {self.animalInRFID} is going to the test")

        rfid = self.animalInRFID
        
        
        # give a limited time to the animal to do the session
        if "TIMER" in event.description:
            
            #print( "error in test: " + str( self.errorHoldTest ) )
            
            #if self.datetimeEnterTest != None:
            if self.testEnabled:
                durationS = self.getCurrentDurationInTestInS()
                #currentTime = datetime.now()
                #durationS = ( currentTime - self.datetimeEnterTest ).seconds
                #logging.info( f"durationS : {durationS} / {maxDurationSSessionDic[self.results[self.animalInRFID]['currentPhase']]}" )
                if durationS > maxDurationSSessionDic[self.results[self.animalInRFID]['currentPhase']]: #check if the maximum duration of the session is reached
                    #self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                    self.stopTest()
                    #self.datetimeEnterTest = None
                
            
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
            
            '''
            logging.info( "---- All results:")
            for rfid in self.results:
                logging.info( f"rfid:{rfid}" )
                for phase in self.results[rfid]:
                    if "phase" in phase:
                        logging.info( phase )
                        for r in self.results[rfid][phase]:
                            logging.info ( r )
            logging.info( "-----------")
            '''
            

        
        if "NO_ORDER" in event.description and self.ratGate.getOrder() == GateOrder.ALLOW_SINGLE_B_TO_A: # intercept si on a fini le programme de la porte
            currentPhase = self.results[self.animalInRFID]['currentPhase']
            #if not "phase5" in currentPhase:
            self.gateToTest()
                        
        
        if self.ratGate.getOrder() == GateOrder.ALLOW_SINGLE_B_TO_A:
            #if "Animal allowed to cross" in event.description: #TO CHECK: compute and store the duration spent in the test
            
            if  "ANIMAL ACCEPTED" in event.description:            
                logging.info("TEST ANIMAL ACCEPTED 1")
                currentPhase = self.results[self.animalInRFID]["currentPhase"]
                resultList = self.results[self.animalInRFID][currentPhase]
                currentResult = resultList[-1]
                currentResult.duration = 0
                
                currentResult.duration = self.getCurrentDurationInTestInS()
                
                logging.info( f"TEST ANIMAL ACCEPTED 2")
                    
                
                self.saveResults()
                           
        
        if "ALLOW_SINGLE_B_TO_A DONE" in event.description:
            #rfid = event.data
                  
                   
            #if "SIDE A" in event.description:
            if True:
                logging.info( f"Animal {rfid} is going to the housing compartment")
                self.stopTest()
                currentPhase = self.results[self.animalInRFID]["currentPhase"]
                resultList = self.results[self.animalInRFID][currentPhase]
                logging.info( f"test-self.animalInRFID : {self.animalInRFID}")
                logging.info( f"test-The current phase is : {currentPhase}")
                
                
                
                if "phase1" in currentPhase:
                    totalLeverCorrect = 0 
                    for result in self.results[self.animalInRFID][currentPhase]:
                        totalLeverCorrect+=result.nbPressCorrect
                        
                    if totalLeverCorrect > MAX_NB_PRESS_PHASE1: # if the max number of press for phase1 is reached, move to phase 2                        
                        #self.results[self.animalInRFID]["currentPhase"] = "phase2"
                        self.changePhase("phase2")
                        logging.info("PHASE 1 COMPLETE (onExit)! (number of press in test module reached)")
                        return
                    
                    
                if "phase2" in currentPhase:
                    
                    totalLeverCorrect = 0
                    for result in self.results[self.animalInRFID][currentPhase]:
                        totalLeverCorrect+=result.nbPressCorrect
                    
                    if totalLeverCorrect > NB_PRESS_CORRECT_PHASE2:
                        #self.results[self.animalInRFID]["currentPhase"] = "phase3"
                        self.changePhase("phase3")
                        logging.info("PHASE 2 COMPLETE (onExit)! (number of correct lever press reached)")
                    else:
                        logging.info(f"PHASE 2 not finished yet (onExit)! nb total lever press : {totalLeverCorrect}")
                        
                    
                    
                if "phase3" in currentPhase: 
                    
                    logging.info(f"PHASE 3 exit")
                                        
                    totalPressCorrect = 0
                    
                    pressList = self.results[self.animalInRFID]["phase3ListPress"]
                    
                    if len(  pressList ) > NUMBER_OF_MIN_PRESS_PHASE3:
                        
                        for b in pressList[-NUMBER_OF_MIN_PRESS_PHASE3:]:
                            
                            if b == True:
                                totalPressCorrect+=1
                        
                        ratio = totalPressCorrect / NUMBER_OF_MIN_PRESS_PHASE3
                                                                                
                        if ratio > RATIO_PHASE3:
                            #self.results[self.animalInRFID]["currentPhase"] = "phase4"
                            self.changePhase("phase4")
                            logging.info("PHASE 3 COMPLETE (onExit)! (ratio reached)")
                        else:
                            logging.info(f"PHASE 3 not finished yet (onExit)! ratio not ok : {ratio}")
                    else:
                        logging.info(f"PHASE 3 not enough press in phase (onExit)!: {len( pressList )}")
                        
                if "phase4" in currentPhase: 
                    
                    logging.info(f"PHASE 4 exit")
                                        
                    totalPressCorrect = 0
                    
                    pressList = self.results[self.animalInRFID]["phase4ListPress"]
                    
                    if len(  pressList ) > NUMBER_OF_MIN_PRESS_PHASE4:
                        
                        for b in pressList[-NUMBER_OF_MIN_PRESS_PHASE4:]:
                            if b == True:
                                totalPressCorrect+=1
                        
                        
                        ratio = totalPressCorrect / NUMBER_OF_MIN_PRESS_PHASE4
                                                                                
                        if ratio > RATIO_PHASE4:
                            #self.results[self.animalInRFID]["currentPhase"] = "phase5"
                            self.changePhase("phase5")
                            logging.info(f"Animal exiting in phase5. now forbidden to come back in test. rfid: {self.animalInRFID}")
                            self.ratGate.addForbiddenRFID( self.animalInRFID )
                            logging.info("PHASE 4 COMPLETE (onExit)! (ratio reached)")
                        else:
                            logging.info(f"PHASE 4 not finished yet (onExit)! ratio not ok : {ratio}")
                    else:
                        logging.info(f"PHASE 4 not enough press in phase (onExit)!: {len( pressList )}")
                                        
                                        
        #if "SIDE B" in event.description:                
        if "ALLOW_SINGLE_A_TO_B DONE" in event.description:
            logging.info( f"Animal {rfid} is going to the test chamber")
            #self.animalInRFID = rfid
            if not rfid in self.results:
                self.results[self.animalInRFID]= {}
                self.results[self.animalInRFID]["phase1"]= [Result()] # phase 1: a drop each time the gate is crossed + one per lever press (any side); stops when max number of press reached
                self.results[self.animalInRFID]["phase2"]= [Result()] # phase 2: a drop each time a press is done (any side) stop session if ( 10 lever press or timeout xx s)
                self.results[self.animalInRFID]["phase3"]= [Result()] # phase 3: a drop each time a press in a definite side is done; stop session if (10 lever press or timeout of xx s)
                self.results[self.animalInRFID]["phase4"]= [Result()] # phase 4: a drop each time a press in the other side is done; stop session if (10 lever press or timeout of xx s)
                self.results[self.animalInRFID]["phase5"]= [Result()] # phase 5: fin de test, attente dans la tente
                self.results[self.animalInRFID]["phase3ListPress"] = [] # list of press with true or false in it for phase 3.
                self.results[self.animalInRFID]["phase4ListPress"] = [] # list of press with true or false in it for phase 4.
                #self.results[self.animalInRFID]["currentPhase"] = "phase1"
                self.changePhase("phase1")
                
            phase = self.results[self.animalInRFID]["currentPhase"]
            self.results[self.animalInRFID][phase].append( Result() ) # on fait une nouvelle session
            #self.datetimeEnterTest = datetime.now()
            #logging.info(f"TEST DATE TIME ENTER {self.datetimeEnterTest}")
            resultList = self.results[self.animalInRFID][phase]
            currentResult = resultList[-1]
            currentResult.startTime = datetime.now() # self.datetimeEnterTest
            self.testEnabled = True
            self.errorHoldTest = False
            
            #determine the random target side for each animal
            if not self.animalInRFID in self.targetSide:
                r = self.determineTargetSide()
                self.targetSide[self.animalInRFID] = r[0]
                self.reversedSide[self.animalInRFID] = r[1]
                                
                                
        if "Checking RFID: Can't read ID of animal" in event.description:
            logging.info("BIG PROBLEM: CANT READ RFID")
           
        
        if self.errorHoldTest:
            phase = self.results[self.animalInRFID]["currentPhase"]
            resultList = self.results[self.animalInRFID][phase]
            currentResult = resultList[-1]
            if "press" in event.description:
                currentResult.nbPressWhileNotAllowed += 1
                if "right" in event.deviceObject.name:
                    logging.info("Press while not allowed (right)")
                if "left" in event.deviceObject.name:
                    logging.info("Press while not allowed (left)")
                
        #if "Animal allowed to cross" in event.description:        
        #if "SIDE B" in event.description:
        
        if "ALLOW_SINGLE_A_TO_B DONE" in event.description:
            phase = self.results[self.animalInRFID]["currentPhase"]
            resultList = self.results[self.animalInRFID][phase]
            currentResult = resultList[-1] 
            
            if "phase1" in phase:
                #phase 1: a drop each time the gate is crossed + one per lever press (any side), stops when max number of presses reached
                #pre-training: one drop each time the gate is crossed (animal in B)
                logging.info(f"[Phase:{phase}/Animal:{self.animalInRFID}] in B for pre-training (entry): pump! nbEntry:{len(resultList)}")
                #delayed pump action
                self.pumpInXseconds( 1 )
                
                self.gateToHouse()
                #self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                
                    
    
        if self.testEnabled == True and not self.errorHoldTest:    
            if event.deviceObject == self.leftLever or event.deviceObject == self.rightLever:
                #rfid = self.animalInRFID
                if "press" in event.description:
                    phase = self.results[self.animalInRFID]["currentPhase"]
                    resultList = self.results[self.animalInRFID][phase]
                    currentResult = resultList[-1] 
                    
                    if "phase1" in phase:
                        #pre-training: one drop each time the gate is crossed (animal in B) and one additional drop if lever press
                        logging.info(f"[Phase:{phase}/Animal:{self.animalInRFID}] in B for pre-training (nose poke): pump!")
                        self.waterPump.pump( 255, dropSizeDic['phase1'] ) #one big drop
                        currentResult.nbPressCorrect += 1
                        if "right" in event.deviceObject.name:
                            currentResult.nbLeverRight += 1
                        if "left" in event.deviceObject.name:
                            currentResult.nbLeverLeft += 1
                        # de-bounce time ?
                            
                    if "phase2" in phase:
                        # phase 2: a drop each time a lever press is done (any side); stop session if ( 10 lever presses or timeout xx s)
                        logging.info(f"[Phase:{phase}/Animal:{self.animalInRFID}] Animal {self.animalInRFID} in B for training: pump!")
                        currentResult.nbPressCorrect+=1
                        self.waterPump.pump( 255, dropSizeDic['phase2'] )
                        if "right" in event.deviceObject.name:
                            currentResult.nbLeverRight += 1
                        if "left" in event.deviceObject.name:
                            currentResult.nbLeverLeft += 1
                        
                        if resultList[-1].nbPressCorrect> MAX_NB_PRESS_SESSION2:
                            self.stopTest()                            
                            self.gateToHouse()
                            #self.ratGate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )                            
                            logging.info("PHASE 2: Session over (nbPress reached) !")
                    
                    if "phase3" in phase:
                        # phase 3: a drop each time a press in a definite side is done; stop session if (10 lever press or timeout of xx s)
                        if "right" in event.deviceObject.name:
                            currentResult.nbLeverRight += 1
                        if "left" in event.deviceObject.name:
                            currentResult.nbLeverLeft += 1
                                                
                        if self.targetSide[self.animalInRFID] in event.deviceObject.name:
                            logging.info(f"[Phase:{phase}/Animal:{self.animalInRFID}] lever press correct side ({self.targetSide[self.animalInRFID]})")
                            currentResult.nbPressCorrect+=1
                            self.results[rfid]["phase3ListPress"].append( True )
                            self.waterPump.pump( 255, dropSizeDic['phase3'] )
                                 
                        
                        if not self.targetSide[self.animalInRFID] in event.deviceObject.name:
                            logging.info("click !")
                            self.errorDateTime = datetime.now()
                            self.errorHoldTest = True
                            currentResult.nbPressFalse+=1
                            self.results[self.animalInRFID]["phase3ListPress"].append( False )                    
                            self.leftLever.click()
                        
                        if currentResult.getTotal() > maxNbTrialPerSession[phase]: 
                            self.stopTest()
                            
                    if "phase4" in phase:
                        # phase 4: a drop each time a press in the other side is done; stop session if (10 lever press or timeout of xx s)
                        
                        if "right" in event.deviceObject.name:
                            currentResult.nbLeverRight += 1
                        if "left" in event.deviceObject.name:
                            currentResult.nbLeverLeft += 1
                                                
                        if self.reversedSide[self.animalInRFID] in event.deviceObject.name:
                            logging.info(f"[Phase:{phase}/Animal:{rfid}] lever press correct side ({self.reversedSide[rfid]})")
                            currentResult.nbPressCorrect+=1
                            self.results[self.animalInRFID]["phase4ListPress"].append( True )
                            self.waterPump.pump( 255, dropSizeDic['phase4'] )
                                 
                        
                        if not self.reversedSide[self.animalInRFID] in event.deviceObject.name:
                            logging.info("click !")
                            self.errorDateTime = datetime.now()
                            self.errorHoldTest = True
                            currentResult.nbPressFalse+=1
                            self.results[self.animalInRFID]["phase4ListPress"].append( False )                    
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




































    
    
    
