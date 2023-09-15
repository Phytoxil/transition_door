'''
Created on 16 mars 2022

@author: Fab
'''

from time import sleep

from datetime import datetime
import logging
import sys
from blocks.autogate.Gate import Gate, GateOrder
from blocks.waterpump.WaterPump import WaterPump
from random import randint, random
from mail.Mail import LMTMail

from enum import Enum
from blocks.FED3.Fed3Manager import Fed3Manager
from blocks.DeviceEvent import DeviceEvent
from math import exp

setupHardwareID = 2 # setup hardware ID

class Sequence(object):
    def __init__(self, *args, **kwargs):
        self.value = 0
        self.time = None
    
        
class Experiment(object):

    class Phase(Enum):
        INIT = 100
        PHASE1 = 101
        PHASE2_INIT = 120
        PHASE2 = 102
        PHASE3 = 103
        PHASE4 = 104 # progressive ratio
        PHASE5 = 105 # = phase 3 / 20 passages total
        PHASE6 = 108 # reversal phase of 3 ?
        END = 106
        ABORT = 107    
        
    def __init__( self , name = None ):
        
        # setup logfile
        self.logFile = "gateLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"    
        print("Logfile: " , self.logFile )    
        logging.basicConfig(level=logging.INFO, filename=self.logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))        
        logging.info('Application started')

        
        if name == None:
            name = "exp#"+str( randint( 0 , 1000 ) )
        logging.info('Experiment created: ' + name )
        self.name = name
        self.currentPhase = None        
        self.initHardware()
        
        
        
        # setting initial poke (left or right) for the experiment. 
        self.initialNosePokeDirection = "left"        
        self.oppositeNosePokeDirection = "right"
        if random() < 0.5:
            self.initialNosePokeDirection = "right"
            self.oppositeNosePokeDirection = "left"
        
        '''
        self.initialNosePokeDirection = "right"
        self.oppositeNosePokeDirection = "left"
        '''
        
            
        logging.info("Initial Nose poke direction: " + self.initialNosePokeDirection )
        
        self.PERIOD_MAIL_INFO = 60*60 # each hour
            
        self.PHASE1_NB_PASS_OK_IN_SOCIAL = 10 #10
        self.PHASE1_NB_PASS_OK_IN_SUGAR = 10 #10
        self.PHASE1_NB_SECOND_ABORT = 60*60*45 #10
                
        self.TIMEOUT_DOOR_WAITING_FOR_ANIMAL_AFTER_POKE = 20        
        self.TIME_TO_ENTER_OK = 20 # 20 before
        
        self.PERIOD_LOG_SECOND = 10
        
        self.PHASE_4_CHRONO_IDLE = "phase4 chrono idle"
        self.IDLE_DURATION_PHASE_4 = 60*60 #  1 hour
        #self.IDLE_DURATION_PHASE_4 = 30 #  1 hour
        
        self.TIME_ERROR_CHRONO = 20# number of second where the opening of the gate is disabled.
        
        self.NB_LAST_POKE = 20
        self.NB_POKE_OK_TO_VALIDATE = self.NB_LAST_POKE * ( 2/3 )  
        
        
        '''
        self.PHASE1_NB_PASS_OK_IN_SOCIAL = 4 #10
        self.PHASE1_NB_PASS_OK_IN_SUGAR = 4 #10
        self.PHASE1_NB_SECOND_ABORT = 60*60*45 #10
                
        self.TIMEOUT_DOOR_WAITING_FOR_ANIMAL_AFTER_POKE = 60        
        self.TIME_TO_ENTER_OK = 60        
        self.PERIOD_LOG_SECOND = 10        
        self.NB_POKE_OK_TO_VALIDATE = 10
        self.NB_LAST_POKE = 20        
        '''
        
        
        
        self.chrono = {}
        self.resetChrono("experiment")
        
        
        # list of correct nose poke sequence ( false or true if ok. )
        self.socialPokeList = { } 
        self.sugarPokeList = { }
        self.sugarAndSocialPokeList = {}
        
        self.sugarSequence = Sequence()
        self.socialSequence = Sequence()
        
        self.progressiveRatio = []
        for i in range( 0 , 100 ):
            self.progressiveRatio.append( int( 5* exp( 0.2 * i ) -4 ) ) #5 × e0.2n -5
            #self.progressiveRatio.append( int( 5* exp( 0.2 * i )  ) ) #5 × e0.2n -5
            
        print ( self.progressiveRatio )
            
        self.socialProgressiveRatio = 0
        self.sugarProgressiveRatio = 0
        self.sugarGateNbPoke = 0
        self.socialGateNbPoke = 0
        
        self.socialFed.lightoff()
        self.sugarFed.lightoff()
                
        self.socialGate.close()
        self.sugarGate.close()
        
        '''
        self.socialGate.open()        
        self.sugarGate.open()
        quit()
        '''
        
                
        #self.socialGate.close()
        #self.sugarGate.close()
        # FORCE PHASE
        #self.setPhase( Experiment.Phase.PHASE2 )
        #self.setPhase( Experiment.Phase.PHASE3 )
        #self.setPhase( Experiment.Phase.PHASE4 )
        #self.setPhase( Experiment.Phase.PHASE5 )
        #self.setPhase( Experiment.Phase.PHASE6 )
        self.setPhase( Experiment.Phase.INIT )

    '''    
    def signal(self):
        self.sugarFed.click()
        #self.sugarFed.clickflash()
    '''
    
    def initHardware(self):
        
        logging.info('Init hardware.')
        
        if setupHardwareID == 1:
            
            self.sugarGate = Gate( 
                COM_Servo = "COM80", 
                COM_Arduino= "COM81", 
                #COM_RFID = "COM82", 
                name="sugar gate",
                weightFactor = 0.74,
                mouseAverageWeight = 20, #31
                lidarPinOrder = ( 1, 0, 3 , 2 )
                #enableLIDAR = False
                 )
                        
            self.socialGate = Gate( 
                COM_Servo = "COM85", 
                COM_Arduino= "COM86", 
                #COM_RFID = "COM82", 
                name="social gate",
                weightFactor = 0.74,
                lidarPinOrder = ( 2, 3, 1 , 0 ),
                mouseAverageWeight = 20 #31,
                
                 )
        
        if setupHardwareID == 2: # ROOM B
            
            self.sugarGate = Gate( 
                COM_Servo = "COM80", 
                COM_Arduino= "COM81", 
                #COM_RFID = "COM82", 
                name="sugar gate",
                weightFactor = 0.65,
                mouseAverageWeight = 20, #31
                lidarPinOrder = ( 0, 3, 2 , 1 )
                #enableLIDAR = False
                 )
                        
            self.socialGate = Gate( 
                COM_Servo = "COM85", 
                COM_Arduino= "COM86", 
                #COM_RFID = "COM82", 
                name="social gate",
                weightFactor = 0.65,
                lidarPinOrder = ( 2, 3, 1 , 0 ),
                mouseAverageWeight = 20, #31,,
                invertScale = True
                
                 )


        self.sugarGate.setRFIDControlEnabled ( False )
        self.sugarGate.setAllowOverWeight( True )

        self.socialGate.setRFIDControlEnabled ( False )
        self.socialGate.setAllowOverWeight( True )        
        
        # TODO: [TxRxResult] Incorrect status packet! CHECK BAUD RATE 1000000 ? metter dans le log aussi
        
        self.deviceEventList = {} # all events from all devices. Phase is key
        
        self.sugarFed = Fed3Manager( comPort="COM39" , name= "sugarFed")
        self.socialFed = Fed3Manager( comPort="COM43" , name = "socialFed" )        
        self.waterPump = WaterPump(comPort="COM90", name="WaterPump")

        self.socialGate.addDeviceListener( self.deviceListener )
        self.sugarGate.addDeviceListener( self.deviceListener )
        self.waterPump.addDeviceListener( self.deviceListener )
        self.socialFed.addDeviceListener( self.deviceListener )
        self.sugarFed.addDeviceListener( self.deviceListener )
        
    
    def removeChrono(self, chronoName ):
        if chronoName in self.chrono:
            self.chrono.pop( chronoName )         
    
    def chronoExists(self, chronoName ):
        return chronoName in self.chrono         
         
    def getChrono(self, chronoName ):
        if chronoName not in self.chrono:
            self.resetChrono( chronoName )        
        return abs(datetime.now()-self.chrono[chronoName]).seconds

    def getChronoHMS(self, chronoNumber ):
        if chronoNumber not in self.chrono:
            self.resetChrono( chronoNumber )        
        return abs(datetime.now()-self.chrono[chronoNumber])

    def resetChrono(self, chronoNumber ):
        self.chrono[chronoNumber] = datetime.now()
    
    def getEventsFromDevice(self , phase, device ):
        if phase not in self.deviceEventList:
            self.deviceEventList[phase] = []
            
        returnList = []
        for event in self.deviceEventList[phase]:
            if event.deviceObject == device:
                returnList.append( event )
        return returnList
    
    def getEventsFromDevices(self , phase, devices ):
        if phase not in self.deviceEventList:
            self.deviceEventList[phase] = []
            
        returnList = []
        for event in self.deviceEventList[phase]:
            if event.deviceObject in devices:
                returnList.append( event )
        return returnList

    
    def deviceListener(self, deviceEvent ):
        
        logging.info( deviceEvent )
        logging.info( "nb event in memory: " + str( len( self.deviceEventList)  ) )
        if not self.currentPhase in self.deviceEventList:
            self.deviceEventList[self.currentPhase] = []

        if not "TraceLogic" in deviceEvent.description: # avoid recording all tracelogic of gates.            
            self.deviceEventList[self.currentPhase].append( deviceEvent )
        
        # PHASE 2 and Phase 3        
        
        def checkPoke( nature ):
            #nature = "social" or "sugar"
        
            
            if "social" in nature:
                pokeList = self.socialPokeList
                sequence = self.socialSequence                
                gate = self.socialGate
                errorChrono = "errorSocialChrono"
                fed = self.socialFed
            
            if "sugar" in nature:
                pokeList = self.sugarPokeList
                sequence = self.sugarSequence                
                gate = self.sugarGate
                errorChrono = "errorSugarChrono"
                fed = self.sugarFed
                
            if self.currentPhase not in pokeList:
                pokeList[self.currentPhase] = []
            
            if self.currentPhase not in self.sugarAndSocialPokeList:
                self.sugarAndSocialPokeList[self.currentPhase] = []
                 
            if nature in deviceEvent.description:            
                if "wrong"  in deviceEvent.description:
                    print( nature + " incorrect")
                    pokeList[self.currentPhase].append( False )
                    self.sugarAndSocialPokeList[self.currentPhase].append( nature + " FALSE")
                    #logging.info( nature +" nose poke wrong side starting error timer")
                    #self.resetChrono( errorChrono )
                    #fed.light()
                    
                    print ( "sequence " , sequence)
                    sequence.value = 0
                if "correct" in deviceEvent.description:
                    print( nature + " correct")
                    
                    #if not self.chronoExists( errorChrono ):                    
                    sequence.value = 1
                    sequence.time= datetime.now()
                    #print( "Set time sequence: " + str( sequence.time ) )
                    '''
                    else:
                        logging.info(gate.name + "nose poke canceled: error timer" )
                    '''
                    
            if deviceEvent.deviceObject == gate:
                if "REOPEN_B:OPEN DOOR_B" in deviceEvent.description:
                    timeToEnter = datetime.now()-sequence.time
                    print( nature + " time to enter: " , str( timeToEnter ))
                    if timeToEnter.seconds < self.TIME_TO_ENTER_OK:
                        pokeList[self.currentPhase].append( True )
                        self.sugarAndSocialPokeList[self.currentPhase].append( nature + " TRUE")
                        logging.info( nature +" nose poke validated in " + str( timeToEnter.seconds ))
                    else:
                        logging.info( nature +" nose poke sequence with gate too long : " + str( timeToEnter.seconds ))
                        
                    sequence.value = 0
        
        if self.currentPhase == self.Phase.PHASE2 or self.currentPhase == self.Phase.PHASE3 or self.currentPhase == self.Phase.PHASE5 or self.currentPhase == self.Phase.PHASE6: 
            checkPoke( "social" )
            checkPoke( "sugar" )
                    
        if self.currentPhase == Experiment.Phase.PHASE1:
            if deviceEvent.deviceObject == self.sugarGate:
                if "REOPEN_B:OPEN DOOR_B" in deviceEvent.description:
                    self.waterdrop()
                    
                    
                     
        
        '''
        # prevent from having too much data in memory:
        if len( self.deviceEventList[self.currentPhase] ) > 1000:
            self.deviceEventList[self.currentPhase].pop( 0 )
        '''
            
    def waterdrop( self ):
        if setupHardwareID == 1:
            self.waterPump.pump( 255, 30 )
        if setupHardwareID == 2:
            self.waterPump.pump( 255, 18 )
    
    def mailInfo( self, subject, content=None , sendLog = False ):
        
        if content == None:
            content = subject
        
        mails = ["fabrice.de.chaumont@gmail.com","benoit.forget@pasteur.fr"]
        subject = subject + " exp:"+str( self.name ) 
        
        mail = LMTMail()
        
        files = []
        if sendLog == True:
            files.append( self.logFile )
                
        mail.sendInfo(mails, subject, content, files  )
        
        
    def setPhase( self, phase ):
        
        self.currentPhase = phase
        logging.info('Starting phase: ' + str( phase ) )    
        self.mailInfo( self.name , "Starting Phase " + str( phase ) )
        self.resetChrono("timerMail")

    def abort(self,reason):
        logging.info( str(self.currentPhase) + ":" + str( reason ) )
        self.mailInfo( self.experimentName , "EXPERIMENT ERROR - " + str(self.currentPhase) + ":" + str( reason ) , sendLog=True )
        self.setPhase( Experiment.Phase.END )
                
    def runLogic(self):

        '''
        if self.getChrono("experiment") > 60*60*45:
            self.setPhase( self.Phase.END )
            return
        '''

        socialFedRead = self.socialFed.read()
        sugarFedRead = self.sugarFed.read()

        
        chronoName = "errorSocialChrono"
        if self.chronoExists( chronoName ):
            if ( self.getChrono( chronoName ) > self.TIME_ERROR_CHRONO ):
                self.chrono.pop( chronoName )                
                logging.info( chronoName + " : removing lock on error" )
                
        chronoName = "errorSugarChrono"
        if self.chronoExists( chronoName ):
            if ( self.getChrono( chronoName ) > self.TIME_ERROR_CHRONO ):
                self.chrono.pop( chronoName )                
                logging.info( chronoName + " : removing lock on error" )
        


        if self.currentPhase == Experiment.Phase.INIT:
            
            # close doors
            self.socialGate.close()
            self.sugarGate.close()            
            
            sleep( 5 )
            
            logging.info("*******************************************************")
            logging.info("Please put the animals in the home area and social area")
            input("Hit enter to start experiment")
            
            # set gates in open mode, let 1 animal pass through 
            self.sugarGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )
            self.socialGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )
                        
            self.setPhase( Experiment.Phase.PHASE1 )
            self.resetChrono( Experiment.Phase.PHASE1 )
            
            
            
            return
        
        if self.currentPhase == Experiment.Phase.PHASE1:
            
            # check if we had 10 go-through for both gates.
            
            nbPassOkInSocial = 0
            for event in self.getEventsFromDevice( self.currentPhase , self.socialGate ):
                if "ANIMAL BACK IN SIDE A" in event.description:
                    nbPassOkInSocial+=1
                
            nbPassOkInSugar = 0
            for event in self.getEventsFromDevice( self.currentPhase , self.sugarGate ):
                if "ANIMAL BACK IN SIDE A" in event.description:
                    nbPassOkInSugar+=1

            if self.getChrono(0) > self.PERIOD_LOG_SECOND:            
                logging.info( "PHASE 1 : Nb pass in Social : " + str( nbPassOkInSocial ) + " Nb pass in Sugar : " + str ( nbPassOkInSugar ) )
                self.resetChrono(0)
                
            '''
            if self.getChrono( Experiment.Phase.PHASE1 ) > self.PHASE1_NB_SECOND_ABORT:
                self.abort("timeout")
            '''
                

            if nbPassOkInSocial >= self.PHASE1_NB_PASS_OK_IN_SOCIAL and nbPassOkInSugar >= self.PHASE1_NB_PASS_OK_IN_SUGAR:

                # empty gates in A if needed
                self.setPhase( Experiment.Phase.PHASE2_INIT )                
                self.sugarGate.setOrder( GateOrder.EMPTY_IN_A )
                self.socialGate.setOrder( GateOrder.EMPTY_IN_A )
                                
            
            return
        
        if self.currentPhase == Experiment.Phase.PHASE2_INIT:
            
            # wait empty gates in side A
            
            emptySocial = False
            for event in self.getEventsFromDevice( self.currentPhase , self.socialGate ):
                if "EMPTY IN A DONE" in event.description:
                    emptySocial=True
                
            emptySugar = False
            for event in self.getEventsFromDevice( self.currentPhase , self.sugarGate ):
                if "EMPTY IN A DONE" in event.description:
                    emptySugar=True
            
            if emptySocial and emptySugar:
                self.setPhase( Experiment.Phase.PHASE2 )
                self.resetChrono( Experiment.Phase.PHASE2 )
                
            
            return
            
        def phase3PokeRead( sugarFedRead, socialFedRead , nosePokeDirection ):

            if sugarFedRead != None:
                
                # incorrect nose poke
                if "In" in sugarFedRead and not nosePokeDirection in sugarFedRead:
                    if self.sugarGate.getOrder() == GateOrder.NO_ORDER and not self.chronoExists( "sugarLight" ) and not self.chronoExists( "errorSugarChrono" ):
                        self.deviceListener( DeviceEvent( "experiment" , self, "NPNOTOKSugar" ) )
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar wrong") )
                        self.resetChrono("errorSugarChrono")
                                                                
                # correct nose poke
                if "In" in sugarFedRead and nosePokeDirection in sugarFedRead and not self.chronoExists( "sugarLight" ):
                    self.deviceListener( DeviceEvent( "experiment" , self, "NPOKSugar" ) )
                    
                    logging.info("Nose poke SUGAR")                    
                    print("current order " + str( self.sugarGate.getOrder() ) )

                    if self.sugarGate.getOrder() == GateOrder.NO_ORDER:
                        self.sugarGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                        self.sugarFed.light( direction = nosePokeDirection )
                        self.resetChrono("sugarLight")
                        #self.signal()
                        
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar correct" ) )
                        logging.info("SUGAR GATE OPEN")
                        logging.info("SUGAR WATER DROP")                        
                        self.waterdrop()
                        self.resetChrono( "sugarGate" )
                        if self.socialGate.getOrder() == GateOrder.ONLY_ONE_ANIMAL_IN_B: # close opposite door if open 
                            logging.info("FORCING CLOSE SOCIAL GATE")
                            self.deviceListener( DeviceEvent( "experiment" , self, "nose poke social cancel other nose poke") )
                            self.socialGate.setOrder( GateOrder.EMPTY_IN_A )
                    else:                        
                        logging.info("SUGAR GATE ALREADY OPEN")
    
            if self.sugarGate.getOrder() == GateOrder.ONLY_ONE_ANIMAL_IN_B:
                if self.getChrono("sugarGate" ) > self.TIMEOUT_DOOR_WAITING_FOR_ANIMAL_AFTER_POKE:
                    if self.sugarGate.logicCursor == 4: # [004] WAIT SINGLE_ANIMAL
                        self.sugarGate.setOrder( GateOrder.EMPTY_IN_A )
                        logging.info("TIMEOUT: CLOSING SUGAR GATE")
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar cancel timeout") )
                        
            
            if socialFedRead != None:
                # incorrect nose poke
                if "In" in socialFedRead and not nosePokeDirection in socialFedRead:
                    if self.socialGate.getOrder() == GateOrder.NO_ORDER and not self.chronoExists( "socialLight" ) and not self.chronoExists( "errorSocialChrono" ):
                        self.deviceListener( DeviceEvent( "experiment" , self, "NPNOTOKSocial" ) )
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke social wrong") )
                        self.resetChrono("errorSocialChrono")
            
                # correct nose poke
                if "In" in socialFedRead and nosePokeDirection in socialFedRead and not self.chronoExists( "socialLight" ):
                    logging.info("Nose poke SOCIAL")
                    self.deviceListener( DeviceEvent( "experiment" , self, "NPOKSocial" ) )
                    print("current order " + str( self.socialGate.getOrder() ) )
                    
                    if self.socialGate.getOrder() == GateOrder.NO_ORDER:
                        self.socialGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                        self.socialFed.light( direction = nosePokeDirection )
                        self.resetChrono("socialLight")
                        #self.signal()
                        #self.socialFed.click()
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke social correct" ) )
                        logging.info("SOCIAL GATE OPEN")
                        self.resetChrono( "socialGate" )
                        if self.sugarGate.getOrder() == GateOrder.ONLY_ONE_ANIMAL_IN_B: # close opposite door if open 
                            logging.info("FORCING CLOSE SUGAR GATE")
                            self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar cancel other nose poke") )
                            self.sugarGate.setOrder( GateOrder.EMPTY_IN_A )    
                    else:                        
                        logging.info("SOCIAL GATE ALREADY OPEN")

            if self.socialGate.getOrder() == GateOrder.ONLY_ONE_ANIMAL_IN_B:
                if self.getChrono("socialGate" ) > self.TIMEOUT_DOOR_WAITING_FOR_ANIMAL_AFTER_POKE:
                    if self.socialGate.logicCursor == 4: # [004] WAIT SINGLE_ANIMAL
                        self.socialGate.setOrder( GateOrder.EMPTY_IN_A )
                        logging.info("TIMEOUT: CLOSING SOCIAL GATE")
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke social cancel timeout") )

        def phase2PokeRead( sugarFedRead, socialFedRead ): # read accept for any hole.

            if sugarFedRead != None:
                
                # correct nose poke
                if "In" in sugarFedRead:
                    logging.info("Nose poke SUGAR")
                    
                    print("current order " + str( self.sugarGate.getOrder() ) )
                    if self.sugarGate.getOrder() == GateOrder.NO_ORDER:
                        self.sugarGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                        
                        if "right" in sugarFedRead:
                            self.sugarFed.light( direction="right" )
                        if "left" in sugarFedRead:
                            self.sugarFed.light( direction="left" )
                        self.resetChrono("sugarFedPhase2Light")                         

                        #self.signal()
                        
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar correct" ) )
                        logging.info("SUGAR GATE OPEN")
                        logging.info("SUGAR WATER DROP")                        
                        self.waterdrop()
                        self.resetChrono( "sugarGate" )
                        if self.socialGate.getOrder() == GateOrder.ONLY_ONE_ANIMAL_IN_B: # close opposite door if open 
                            logging.info("FORCING CLOSE SOCIAL GATE")
                            self.deviceListener( DeviceEvent( "experiment" , self, "nose poke social cancel other nose poke") )
                            self.socialGate.setOrder( GateOrder.EMPTY_IN_A )
                    else:                        
                        logging.info("SUGAR GATE ALREADY OPEN")
    
            if self.sugarGate.getOrder() == GateOrder.ONLY_ONE_ANIMAL_IN_B:
                if self.getChrono("sugarGate" ) > self.TIMEOUT_DOOR_WAITING_FOR_ANIMAL_AFTER_POKE:
                    if self.sugarGate.logicCursor == 4: # [004] WAIT SINGLE_ANIMAL
                        self.sugarGate.setOrder( GateOrder.EMPTY_IN_A )
                        logging.info("TIMEOUT: CLOSING SUGAR GATE")
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar cancel timeout") )
                        
            
            if socialFedRead != None:
                
                # correct nose poke
                if "In" in socialFedRead:
                    logging.info("Nose poke SOCIAL")
                    print("current order " + str( self.socialGate.getOrder() ) )
                    if self.socialGate.getOrder() == GateOrder.NO_ORDER:
                        self.socialGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                        
                        if "right" in socialFedRead:
                            self.socialFed.light( direction="right" )
                        if "left" in socialFedRead:
                            self.socialFed.light( direction="left" )
                        self.resetChrono("socialFedPhase2Light") 
                        
                        #self.signal

                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke social correct" ) )
                        logging.info("SOCIAL GATE OPEN")
                        self.resetChrono( "socialGate" )
                        if self.sugarGate.getOrder() == GateOrder.ONLY_ONE_ANIMAL_IN_B: # close opposite door if open 
                            logging.info("FORCING CLOSE SUGAR GATE")
                            self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar cancel other nose poke") )
                            self.sugarGate.setOrder( GateOrder.EMPTY_IN_A )    
                    else:                        
                        logging.info("SOCIAL GATE ALREADY OPEN")

            if self.socialGate.getOrder() == GateOrder.ONLY_ONE_ANIMAL_IN_B:
                if self.getChrono("socialGate" ) > self.TIMEOUT_DOOR_WAITING_FOR_ANIMAL_AFTER_POKE:
                    if self.socialGate.logicCursor == 4: # [004] WAIT SINGLE_ANIMAL
                        self.socialGate.setOrder( GateOrder.EMPTY_IN_A )
                        logging.info("TIMEOUT: CLOSING SOCIAL GATE")
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke social cancel timeout") )

            
        def nosePokePhase( nosePokeDirection ):
            # TODO: rajouter un phase data
            
            if "any" in nosePokeDirection:
                phase2PokeRead( sugarFedRead, socialFedRead )
            else:
            
                # phase 3 logic
                phase3PokeRead(sugarFedRead, socialFedRead, nosePokeDirection )
            
            # each 10s log
            
            if self.currentPhase not in self.sugarPokeList:                    
                self.sugarPokeList[self.currentPhase]=[]
            if self.currentPhase not in self.socialPokeList:
                self.socialPokeList[self.currentPhase]=[]
            if self.currentPhase not in self.sugarAndSocialPokeList:
                self.sugarAndSocialPokeList[self.currentPhase]=[]
                
            sugarOk = 0
            sugarWrong = 0
            lastSugar = self.sugarPokeList[self.currentPhase][-self.NB_LAST_POKE:] 
            for i in lastSugar:
                if i:
                    sugarOk +=1
                else:
                    sugarWrong +=1
            
            socialOk = 0
            socialWrong = 0
            lastSocial = self.socialPokeList[self.currentPhase][-self.NB_LAST_POKE:]
            for i in lastSocial:
                if i:
                    socialOk +=1
                else:
                    socialWrong +=1
                
            
            nbPassInSugar=0
            for event in self.getEventsFromDevice( self.currentPhase , self.sugarGate ):
                if "ANIMAL BACK IN SIDE A" in event.description:
                    nbPassInSugar+=1

            nbPassInSocial=0
            for event in self.getEventsFromDevice( self.currentPhase , self.socialGate ):
                if "ANIMAL BACK IN SIDE A" in event.description:
                    nbPassInSocial+=1
            
                    
            if self.getChrono(0) > self.PERIOD_LOG_SECOND:
                logging.info( str( self.currentPhase ) + " : sugar: " + str( ( sugarOk, sugarWrong ) ) + " social: " + str( ( socialOk, socialWrong ) ) )
                print( "len lastsugar/lastsocial: " , len(lastSugar) , len( lastSocial ) , " nb pass : " , nbPassInSugar , nbPassInSocial )
                
                wrongSocial = 0
                okSocial = 0
                wrongSugar = 0
                okSugar = 0
                
                for event in self.getEventsFromDevice( self.currentPhase , self ):
                    #print(event.description)
                    if "NPNOTOKSocial" in event.description:
                        wrongSocial+=1
                        
                    if "NPOKSocial" in event.description:
                        okSocial+=1                
                        
                    if "NPNOTOKSugar" in event.description:
                        wrongSugar+=1                    
                    
                    if "NPOKSugar" in event.description:
                        okSugar+=1
                        
                logging.info("Number of nose poke ok/wrong : sugar: ( " + str( okSugar ) + ", " + str( wrongSugar ) + " ) -- social : ( " + str( okSocial ) + ", " + str( wrongSocial ) + " ) " )
                
                self.resetChrono(0)
                
            if self.getChrono("timerMail") > self.PERIOD_MAIL_INFO: # each hour log # TODO 60*60
                text = ""
                text+="Current phase: " + str( self.currentPhase ) + "\n"
                text+="SUGAR ok/wrong: " + str( ( sugarOk, sugarWrong ) ) + "\n"
                text+="SOCIAL ok/wrong: " + str( ( socialOk, socialWrong ) ) + "\n"
                text+="\n"
                text+="NB pass in sugar: " + str( nbPassInSugar ) + "\n"
                text+="NB pass in social: " + str( nbPassInSocial ) + "\n"
                text+="\n"
                text+="Current duration of this phase: " + str( self.getChronoHMS( self.currentPhase ) )  + "\n"
                text+="Current duration of the experiment: " + str( self.getChronoHMS( "experiment" ) ) + "\n"
                text+="\n"
                text+="debug info:\n"
                text+="\n"
                text+="Sugar + social pokelist of current phase (all):"
                text+="\n"
                text+= str( self.sugarAndSocialPokeList[self.currentPhase] )
                text+="Sugar pokelist of current phase (all):"
                text+="\n"
                text+= str( self.sugarPokeList[self.currentPhase] )
                text+="\n"
                text+="Social pokelist of current phase (all):"
                text+="\n"
                text+= str( self.socialPokeList[self.currentPhase] )
                text+="\n"                
                text+="Sugar pokelist of current phase ([-self.NB_LAST_POKE:]):"
                text+="\n"
                text+= str( self.sugarPokeList[self.currentPhase][-self.NB_LAST_POKE:] )
                text+="\n"
                text+="Social pokelist of current phase ([-self.NB_LAST_POKE:]):"
                text+="\n"
                text+= str( self.socialPokeList[self.currentPhase][-self.NB_LAST_POKE:] )
                text+="\n"                
                text+="\n"
                 
                                
                self.mailInfo( "each 1h Info " + str( self.currentPhase ) , content=text, sendLog=True )                
                self.resetChrono("timerMail")
            
            # tests to enter next phase:
            
            sugarAndSocialPokeList = self.sugarAndSocialPokeList[self.currentPhase] 
            if len ( sugarAndSocialPokeList ) >40 :
                nbOK = 0                
                for val in sugarAndSocialPokeList[-40:]:
                    if "TRUE" in val:
                        nbOK+=1
                if nbOK > 26: # 2/3*40
                    if self.currentPhase == self.Phase.PHASE2:
                        self.setPhase( Experiment.Phase.PHASE3 )
                        self.resetChrono( Experiment.Phase.PHASE3 )
                        return
                    if self.currentPhase == self.Phase.PHASE3:
                        self.setPhase( Experiment.Phase.PHASE4 )
                        self.resetChrono( Experiment.Phase.PHASE4 )                    
                        return
            
            '''
            if socialOk> self.NB_POKE_OK_TO_VALIDATE and sugarOk > self.NB_POKE_OK_TO_VALIDATE and len(lastSugar) >= self.NB_LAST_POKE-1 and len( lastSocial ) >=self.NB_LAST_POKE-1:
                if self.currentPhase == self.Phase.PHASE2:
                    self.setPhase( Experiment.Phase.PHASE3 )
                    self.resetChrono( Experiment.Phase.PHASE3 )
                    return
                if self.currentPhase == self.Phase.PHASE3:
                    self.setPhase( Experiment.Phase.PHASE4 )
                    self.resetChrono( Experiment.Phase.PHASE4 )                    
                    return
                    
            '''
                
            
        # ---------------------------------------------------------------------------
        
        def nosePokePhase5( nosePokeDirection ):
            
            # same as phase 5
            phase3PokeRead(sugarFedRead, socialFedRead, nosePokeDirection )
            
            # each 10s log
            
            if self.currentPhase not in self.sugarPokeList:                    
                self.sugarPokeList[self.currentPhase]=[]
            if self.currentPhase not in self.socialPokeList:
                self.socialPokeList[self.currentPhase]=[]
            if self.currentPhase not in self.sugarAndSocialPokeList:
                self.sugarAndSocialPokeList[self.currentPhase]=[]
                
            sugarOk = 0
            sugarWrong = 0
            lastSugar = self.sugarPokeList[self.currentPhase][-self.NB_LAST_POKE:] 
            for i in lastSugar:
                if i:
                    sugarOk +=1
                else:
                    sugarWrong +=1
            
            socialOk = 0
            socialWrong = 0
            lastSocial = self.socialPokeList[self.currentPhase][-self.NB_LAST_POKE:]
            for i in lastSocial:
                if i:
                    socialOk +=1
                else:
                    socialWrong +=1
                
            
            nbPassInSugar=0
            for event in self.getEventsFromDevice( self.currentPhase , self.sugarGate ):
                if "ANIMAL BACK IN SIDE A" in event.description:
                    nbPassInSugar+=1

            nbPassInSocial=0
            for event in self.getEventsFromDevice( self.currentPhase , self.socialGate ):
                if "ANIMAL BACK IN SIDE A" in event.description:
                    nbPassInSocial+=1
            
                    
            if self.getChrono(0) > self.PERIOD_LOG_SECOND:
                logging.info( str( self.currentPhase ) + " : sugar: " + str( ( sugarOk, sugarWrong ) ) + " social: " + str( ( socialOk, socialWrong ) ) )
                print( "len lastsugar/lastsocial: " , len(lastSugar) , len( lastSocial ) , " nb pass : " , nbPassInSugar , nbPassInSocial )
                
                wrongSocial = 0
                okSocial = 0
                wrongSugar = 0
                okSugar = 0
                
                print( self.sugarAndSocialPokeList[self.currentPhase] )
                
                for event in self.getEventsFromDevice( self.currentPhase , self ):
                    #print(event.description)
                    if "NPNOTOKSocial" in event.description:
                        wrongSocial+=1
                        
                    if "NPOKSocial" in event.description:
                        okSocial+=1                
                        
                    if "NPNOTOKSugar" in event.description:
                        wrongSugar+=1                    
                    
                    if "NPOKSugar" in event.description:
                        okSugar+=1
                        
                logging.info("Number of nose poke ok/wrong : sugar: ( " + str( okSugar ) + ", " + str( wrongSugar ) + " ) -- social : ( " + str( okSocial ) + ", " + str( wrongSocial ) + " ) " )
                
                self.resetChrono(0)
                
            if self.getChrono("timerMail") > self.PERIOD_MAIL_INFO: # each hour log # TODO 60*60
                text = ""
                text+="Current phase: " + str( self.currentPhase ) + "\n"
                text+="SUGAR ok/wrong: " + str( ( sugarOk, sugarWrong ) ) + "\n"
                text+="SOCIAL ok/wrong: " + str( ( socialOk, socialWrong ) ) + "\n"
                text+="\n"
                text+="NB pass in sugar: " + str( nbPassInSugar ) + "\n"
                text+="NB pass in social: " + str( nbPassInSocial ) + "\n"
                text+="\n"
                text+="Current duration of this phase: " + str( self.getChronoHMS( self.currentPhase ) )  + "\n"
                text+="Current duration of the experiment: " + str( self.getChronoHMS( "experiment" ) ) + "\n"
                text+="\n"
                text+="debug info:\n"
                text+="\n"
                text+="Sugar and social pokelist of current phase (all):"
                text+="\n"
                text+= str( self.sugarAndSocialPokeList[self.currentPhase] )
                text+="Sugar pokelist of current phase (all):"
                text+="\n"
                text+= str( self.sugarPokeList[self.currentPhase] )
                text+="\n"
                text+="Social pokelist of current phase (all):"
                text+="\n"
                text+= str( self.socialPokeList[self.currentPhase] )
                text+="\n"                
                text+="Sugar pokelist of current phase ([-self.NB_LAST_POKE:]):"
                text+="\n"
                text+= str( self.sugarPokeList[self.currentPhase][-self.NB_LAST_POKE:] )
                text+="\n"
                text+="Social pokelist of current phase ([-self.NB_LAST_POKE:]):"
                text+="\n"
                text+= str( self.socialPokeList[self.currentPhase][-self.NB_LAST_POKE:] )
                text+="\n"                
                text+="\n"
                 
                                
                self.mailInfo( "each 1h Info " + str( self.currentPhase ) , content=text, sendLog=True )                
                self.resetChrono("timerMail")
            
            
            # tests to enter next phase:

            sugarAndSocialPokeList = self.sugarAndSocialPokeList[self.currentPhase] 
            if self.currentPhase == self.Phase.PHASE5:
                if len ( sugarAndSocialPokeList ) >20 :
                    nbOK = 0                
                    for val in sugarAndSocialPokeList[-20:]:
                        if "TRUE" in val:
                            nbOK+=1
                    if nbOK > (0.66*20): # 2/3*40
                        self.setPhase( Experiment.Phase.PHASE6 )
                        self.resetChrono( Experiment.Phase.PHASE6 )
                        return
                
            
            # OR TEST >13 on (for each GATE)
            '''
            if ( socialOk> self.NB_POKE_OK_TO_VALIDATE and sugarOk > self.NB_POKE_OK_TO_VALIDATE ) or ( len(lastSugar) >= self.NB_LAST_POKE-1 and len( lastSocial ) >=self.NB_LAST_POKE-1 ):
                
                if self.currentPhase == self.Phase.PHASE5:
                    self.setPhase( Experiment.Phase.PHASE6 )
                    self.resetChrono( Experiment.Phase.PHASE6 )                    
                    return
                
                if self.currentPhase == self.Phase.PHASE6:
                    self.setPhase( Experiment.Phase.END )
                    self.resetChrono( Experiment.Phase.END )                    
                    return
            '''
                
            

        
        #---------------------------------------------------------------------------
            
        if self.currentPhase == Experiment.Phase.PHASE2:
            
            nosePokePhase( "any" )
            
            c = "sugarFedPhase2Light"
            if self.chronoExists( c ):
                if self.getChrono( c ) > 20:                    
                    self.sugarFed.lightoff()
                    self.removeChrono( c )
            
            c = "socialFedPhase2Light"
            if self.chronoExists( c ):
                if self.getChrono( c ) > 20:                    
                    self.socialFed.lightoff()
                    self.removeChrono( c )

            
            
        if self.currentPhase == Experiment.Phase.PHASE3: 
            
            #nosePokePhase( self.oppositeNosePokeDirection ) # reversal            
            nosePokePhase( self.initialNosePokeDirection )

            c = "sugarLight"
            if self.chronoExists( c ):
                if self.getChrono( c ) > 20:                    
                    self.sugarFed.lightoff()
                    self.removeChrono( c )
            
            c = "socialLight"
            if self.chronoExists( c ):
                if self.getChrono( c ) > 20:                    
                    self.socialFed.lightoff()
                    self.removeChrono( c )            
            
                    
        if self.currentPhase == Experiment.Phase.PHASE4: # progressive ratio
            
            nosePokeDirection = self.initialNosePokeDirection
            
            c = "sugarFedPhase4Light"
            if self.chronoExists( c ):
                if self.getChrono( c ) > 20:                    
                    self.sugarFed.lightoff()
                    self.removeChrono( c )
            
            c = "socialFedPhase4Light"
            if self.chronoExists( c ):
                if self.getChrono( c ) > 20:                    
                    self.socialFed.lightoff()
                    self.removeChrono( c )
                        
            '''
            self.socialProgressiveRatio = 0
            self.sugarProgressiveRatio = 0
            '''            
            
            # check if anything has been poked in feds to reset idle time.
            if sugarFedRead != None:                
                if "In" in sugarFedRead:
                    if self.sugarGate.getOrder() == GateOrder.NO_ORDER:  # ensure animal is in his house area
                        self.resetChrono( self.PHASE_4_CHRONO_IDLE )
            if socialFedRead != None:
                if "In" in socialFedRead:
                    if self.socialGate.getOrder() == GateOrder.NO_ORDER: # ensure animal is in his house area
                        self.resetChrono( self.PHASE_4_CHRONO_IDLE )
                    
                
            # correct nose poke
            if sugarFedRead != None:
                if "In" in sugarFedRead and nosePokeDirection in sugarFedRead:
                    
                    if self.sugarGate.getOrder() == GateOrder.NO_ORDER:
                        self.sugarGateNbPoke+=1
                        logging.info("Nose poke progressive SUGAR : " + str( self.sugarGateNbPoke ) + " / " + str( self.progressiveRatio[self.sugarProgressiveRatio] ) )                        
                                            
                    if self.sugarGateNbPoke >= self.progressiveRatio[self.sugarProgressiveRatio]:
                        logging.info("Nose poke progressive ratio SUGAR reached:  #" + str( self.sugarProgressiveRatio ) + " / " + str (self.progressiveRatio[self.sugarProgressiveRatio] ) )
                        self.sugarGateNbPoke=0
                        self.sugarProgressiveRatio+=1                    
                                    
                        print("current order " + str( self.sugarGate.getOrder() ) )
                        if self.sugarGate.getOrder() == GateOrder.NO_ORDER:
                            self.sugarGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                            
                            self.sugarFed.light( direction = nosePokeDirection )
                            self.resetChrono( "sugarFedPhase4Light" )                            
                                                  
                            logging.info("SUGAR GATE OPEN")
                            logging.info("SUGAR WATER DROP")                        
                            self.waterdrop()
                        else:                        
                            logging.info("SUGAR GATE ALREADY OPEN")
                    
                        
            if socialFedRead != None:
                if "In" in socialFedRead and nosePokeDirection in socialFedRead:
                    
                    
                    if self.socialGate.getOrder() == GateOrder.NO_ORDER:
                        self.socialGateNbPoke+=1
                        logging.info("Nose poke progressive SOCIAL : " + str( self.socialGateNbPoke ) + " / " + str( self.progressiveRatio[self.socialProgressiveRatio] ) )
                                            
                    if self.socialGateNbPoke >= self.progressiveRatio[self.socialProgressiveRatio]:
                        logging.info("Nose poke progressive ratio SOCIAL reached:  #" + str( self.socialProgressiveRatio ) + " / " + str (self.progressiveRatio[self.socialProgressiveRatio] ) )
                        self.socialGateNbPoke=0
                        self.socialProgressiveRatio+=1                    
                                    
                        print("current order " + str( self.socialGate.getOrder() ) )
                        if self.socialGate.getOrder() == GateOrder.NO_ORDER:
                            self.socialGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                            
                            self.socialFed.light( direction = nosePokeDirection )
                            self.resetChrono( "socialFedPhase4Light" )
                                                    
                            logging.info("SOCIAL GATE OPEN")                                                                        
                        else:                        
                            logging.info("SOCIAL GATE ALREADY OPEN")
            
            if self.getChrono( self.currentPhase ) > 8*60*60: # 8 hours
                self.setPhase( Experiment.Phase.PHASE5 )
                self.resetChrono( Experiment.Phase.PHASE5 )
                
                 
            '''
            if self.getChrono( self.PHASE_4_CHRONO_IDLE ) > self.IDLE_DURATION_PHASE_4:
                self.setPhase( Experiment.Phase.PHASE5 )
                self.resetChrono( Experiment.Phase.PHASE5 )
            '''                
                
            
            if self.getChrono(0) > self.PERIOD_LOG_SECOND:
                logging.info( str( self.currentPhase ) + " : current ratio: social:" + str( self.socialGateNbPoke ) + " / " + str( self.progressiveRatio[self.socialProgressiveRatio] ) + " sugar:" + str( self.sugarGateNbPoke ) + " / " + str( self.progressiveRatio[self.sugarProgressiveRatio] ) )
                logging.info( str( "idle time: " + str ( self.getChronoHMS( self.PHASE_4_CHRONO_IDLE ) ) ) )
                logging.info( str( "current phase duration: " + str ( self.getChronoHMS( self.currentPhase ) ) ) )
                self.resetChrono( 0 )
            
            if self.getChrono("timerMail") > self.PERIOD_MAIL_INFO: # each hour log 
                text = ""

                text+="Current phase: " + str( self.currentPhase ) + "\n"
                text+="current ratio:\n"
                text+="social:" + str( self.socialGateNbPoke ) + " / " + str( self.progressiveRatio[self.socialProgressiveRatio] ) + " step: " + str(self.socialProgressiveRatio) + "\n"
                text+="sugar:" + str( self.sugarGateNbPoke ) + " / " + str( self.progressiveRatio[self.sugarProgressiveRatio] ) + " step: " + str(self.sugarProgressiveRatio) + "\n"
                
                text+="Current duration of this phase: " + str( self.getChronoHMS( self.currentPhase ) ) + "\n"
                text+="Current duration of the experiment: " + str( self.getChronoHMS( "experiment" ) ) + "\n"
                
                text+="Last idle time: " + str( self.getChronoHMS( self.PHASE_4_CHRONO_IDLE ) ) + "\n"
                
                                
                self.mailInfo( "each 1h Info " + str( self.currentPhase ) , content=text, sendLog=True )                
                self.resetChrono("timerMail")
            
            
            # phase logic:
            
            # tests to enter next phase:            
            # 4h sans rien ou fin des 45 heures de manip
            
            
            
                

            return
        
        if self.currentPhase == Experiment.Phase.PHASE5:
        
            #nosePokePhase( self.oppositeNosePokeDirection ) # reversal            
            nosePokePhase5( self.initialNosePokeDirection )

        if self.currentPhase == Experiment.Phase.PHASE6:
        
            nosePokePhase5( self.oppositeNosePokeDirection )            
            #nosePokePhase5( self.initialNosePokeDirection )

        c = "sugarLight"
        if self.chronoExists( c ):
            if self.getChrono( c ) > 20:                    
                self.sugarFed.lightoff()
                self.removeChrono( c )
        
        c = "socialLight"
        if self.chronoExists( c ):
            if self.getChrono( c ) > 20:                    
                self.socialFed.lightoff()
                self.removeChrono( c )            

        
        if self.currentPhase == Experiment.Phase.END:
            self.socialGate.open()
            self.sugarGate.open()
            self.mailInfo( "EXPERIMENT FINISHED - LOG " + str(self.currentPhase), sendLog=True )
            logging.info("5 Seconds to quit...")
            sleep(5)
            logging.info("quit.")
            quit()
            

if __name__ == '__main__':
        
    experiment = Experiment()
    
    
    while( True ):
        
        experiment.runLogic()
        sleep( 0.05 )
    
    
    
    
    