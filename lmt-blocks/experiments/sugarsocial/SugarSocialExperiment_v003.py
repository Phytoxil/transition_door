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



class Sequence(object):
    def __init__(self, *args, **kwargs):
        self.value = 0
        self.time = None
    
        
class Experiment(object):

    class Phase(Enum):
        INIT = 100
        PHASE1 = 101
        PHASE_ANY_NOSE_POKE_INIT = 111
        PHASE_ANY_NOSE_POKE = 110
        PHASE2_INIT = 120
        PHASE2 = 102
        PHASE3 = 103
        PHASE4 = 104
        PHASE5 = 105
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
        self._currentPhase = None        
        self.initHardware()
        
        
        # setting initial poke (left or right) for the experiment. 
        self.initialNosePokeDirection = "left"        
        self.oppositeNosePokeDirection = "right"
        if random() < 0.5:
            self.initialNosePokeDirection = "right"
            self.oppositeNosePokeDirection = "left"
                    
        logging.info("Initial Nose poke direction: " + self.initialNosePokeDirection )
        
        self.PERIOD_MAIL_INFO = 60*60 # each hour
            
        self.PHASE1_NB_PASS_OK_IN_SOCIAL = 10 #10
        self.PHASE1_NB_PASS_OK_IN_SUGAR = 10 #10
        self.PHASE1_NB_SECOND_ABORT = 60*60*45 #10
                
        self.TIMEOUT_DOOR_WAITING_FOR_ANIMAL_AFTER_POKE = 60        
        self.TIME_TO_ENTER_OK = 20
        
        self.PERIOD_LOG_SECOND = 10
        
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
                
        # FORCE PHASE
        #self.setPhase( Experiment.Phase.PHASE2 )
        self.setPhase( Experiment.Phase.INIT )
    
    
    def initHardware(self):
        
        logging.info('Init hardware.')
            
        self.sugarGate = Gate( 
            COM_Servo = "COM80", 
            COM_Arduino= "COM81", 
            #COM_RFID = "COM82", 
            name="sugar gate",
            weightFactor = 0.74,
            mouseAverageWeight = 24 #32
            #enableLIDAR = False
             )
        
        self.sugarGate.setRFIDControlEnabled ( False ) 
        self.sugarFed = Fed3Manager( comPort="COM39" , name= "sugarFed")
        
        self.socialGate = Gate( 
            COM_Servo = "COM85", 
            COM_Arduino= "COM86", 
            #COM_RFID = "COM82", 
            name="social gate",
            weightFactor = 0.74,
            mouseAverageWeight = 24 #32,
            
             )
        
        self.deviceEventList = {} # all events from all devices. Phase is key
        
        self.socialGate.setRFIDControlEnabled ( False )        
        self.socialFed = Fed3Manager( comPort="COM43" , name = "socialFed" )        
        self.waterPump = WaterPump(comPort="COM90", name="WaterPump")

        self.socialGate.addDeviceListener( self.deviceListener )
        self.sugarGate.addDeviceListener( self.deviceListener )
        self.waterPump.addDeviceListener( self.deviceListener )
        self.socialFed.addDeviceListener( self.deviceListener )
        self.sugarFed.addDeviceListener( self.deviceListener )
        
    
        
    def getChrono(self, chronoName ):
        if chronoName not in self.chrono:
            self.resetChrono( chronoName )        
        return abs(datetime.now()-self.chrono[chronoName]).seconds

    def getChronoHMS(self, chronoName ):
        if chronoName not in self.chrono:
            self.resetChrono( chronoName )        
        return abs(datetime.now()-self.chrono[chronoName])

    def resetChrono(self, chronoName ):
        self.chrono[chronoName] = datetime.now()
    
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
        if not self._currentPhase in self.deviceEventList:
            self.deviceEventList[self._currentPhase] = []

        if not "TraceLogic" in deviceEvent.description: # avoid recording all tracelogic of gates.            
            self.deviceEventList[self._currentPhase].append( deviceEvent )
        
        # PHASE 2 and Phase 3        
        
        def checkPoke( nature ):
            #nature = "social" or "sugar"
        
            
            if "social" in nature:
                pokeList = self.socialPokeList
                sequence = self.socialSequence                
                gate = self.socialGate
            
            if "sugar" in nature:
                pokeList = self.sugarPokeList
                sequence = self.sugarSequence                
                gate = self.sugarGate
                
            if self._currentPhase not in pokeList:
                pokeList[self._currentPhase] = []
                 
            if nature in deviceEvent.description:            
                if "wrong"  in deviceEvent.description:
                    print( nature + " incorrect")
                    pokeList[self._currentPhase].append( False )
                    logging.info( nature +" nose poke wrong side")
                    print ( "sequence " , sequence)
                    sequence.value = 0
                if "correct" in deviceEvent.description:
                    print( nature + " correct")
                    sequence.value = 1
                    sequence.time= datetime.now()
                    logging.info( "debug time to enter INIT " + nature )
                    #print( "Set time sequence: " + str( sequence.time ) )
                    
            if deviceEvent.deviceObject == gate:
                if "REOPEN_B:OPEN DOOR_B" in deviceEvent.description:
                    timeToEnter = datetime.now()-sequence.time
                    print( nature + " time to enter: " , str( timeToEnter ))
                    if timeToEnter.seconds < self.TIME_TO_ENTER_OK:
                        pokeList[self._currentPhase].append( True )
                        logging.info( nature +" nose poke validated in " + str( timeToEnter.seconds ))
                    else:
                        logging.info( nature +" nose poke sequence with gate too long : " + str( timeToEnter.seconds ))
                        
                    sequence.value = 0
                    
            try:
                # debug tests
                timeToEnter = datetime.now()-sequence.time
                logging.info( "debug time to enter " + nature + " : " + str( timeToEnter.seconds ) )
            except:
                logging.info( "debug time to enter " + nature + " : NONE " )
                
                
        
        if self._currentPhase == self.Phase.PHASE2 or self._currentPhase == self.Phase.PHASE3 or self._currentPhase == self.Phase.PHASE_ANY_NOSE_POKE: 
            checkPoke( "social" )
            checkPoke( "sugar" )
                    
        if self._currentPhase == Experiment.Phase.PHASE1:
            if deviceEvent.deviceObject == self.sugarGate:
                if "REOPEN_B:OPEN DOOR_B" in deviceEvent.description:
                    self.waterPump.drop()
                     
        
        '''
        # prevent from having too much data in memory:
        if len( self.deviceEventList[self._currentPhase] ) > 1000:
            self.deviceEventList[self._currentPhase].pop( 0 )
        '''
            
    
    def mailInfo( self, subject, content=None , sendLog = False ):
        
        if content == None:
            content = subject
        
        mails = ["fabrice.de-chaumont@pasteur.fr","benoit.forget@pasteur.fr"]
        subject = subject + " exp:"+str( self.name ) 
        
        mail = LMTMail()
        
        files = []
        if sendLog == True:
            files.append( self.logFile )
                
        mail.sendInfo(mails, subject, content, files  )
        
        
    def setPhase( self, phase ):
        
        self._currentPhase = phase
        logging.info('Starting phase: ' + str( phase ) )    
        self.mailInfo( self.name , "Starting Phase " + str( phase ) )
        self.resetChrono("timerMail")

    def abort(self,reason):
        logging.info( str(self._currentPhase) + ":" + str( reason ) )
        self.mailInfo( self.experimentName , "EXPERIMENT ERROR - " + str(self._currentPhase) + ":" + str( reason ) , sendLog=True )
        self.setPhase( Experiment.Phase.END )
                
    def runLogic(self):

        if self.getChrono("experiment") > 60*60*45:
            self.setPhase( self.Phase.END )
            return

        socialFedRead = self.socialFed.read()
        sugarFedRead = self.sugarFed.read()

        if self._currentPhase == Experiment.Phase.INIT:
            
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
        
        if self._currentPhase == Experiment.Phase.PHASE1:
            
            # check if we had 10 go-through for both gates.
            
            nbPassOkInSocial = 0
            for event in self.getEventsFromDevice( self._currentPhase , self.socialGate ):
                if "ANIMAL BACK IN SIDE A" in event.description:
                    nbPassOkInSocial+=1
                
            nbPassOkInSugar = 0
            for event in self.getEventsFromDevice( self._currentPhase , self.sugarGate ):
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
                self.setPhase( Experiment.Phase.PHASE_ANY_NOSE_POKE_INIT )                
                self.sugarGate.setOrder( GateOrder.EMPTY_IN_A )
                self.socialGate.setOrder( GateOrder.EMPTY_IN_A )
                                
            
            return
        
        if self._currentPhase == Experiment.Phase.PHASE_ANY_NOSE_POKE_INIT:
            
            # wait empty gates in side A
            
            emptySocial = False
            for event in self.getEventsFromDevice( self._currentPhase , self.socialGate ):
                if "EMPTY IN A DONE" in event.description:
                    emptySocial=True
                
            emptySugar = False
            for event in self.getEventsFromDevice( self._currentPhase , self.sugarGate ):
                if "EMPTY IN A DONE" in event.description:
                    emptySugar=True
            
            if emptySocial and emptySugar:
                self.setPhase( Experiment.Phase.PHASE_ANY_NOSE_POKE )
                self.resetChrono( Experiment.Phase.PHASE_ANY_NOSE_POKE )
                
            
            return
        
        if self._currentPhase == Experiment.Phase.PHASE2_INIT:
            
            # wait empty gates in side A
            
            emptySocial = False
            for event in self.getEventsFromDevice( self._currentPhase , self.socialGate ):
                if "EMPTY IN A DONE" in event.description:
                    emptySocial=True
                
            emptySugar = False
            for event in self.getEventsFromDevice( self._currentPhase , self.sugarGate ):
                if "EMPTY IN A DONE" in event.description:
                    emptySugar=True
            
            if emptySocial and emptySugar:
                self.setPhase( Experiment.Phase.PHASE2 )
                self.resetChrono( Experiment.Phase.PHASE2 )
                
            
            return

        def phaseAnyPokeRead( sugarFedRead, socialFedRead ):            
                    
            # SUGAR 
            
            if sugarFedRead != None:
                                
                # correct nose poke
                if "In" in sugarFedRead:
                    logging.info("Nose poke SUGAR : " + str( sugarFedRead ) )
                    
                    print("current order " + str( self.sugarGate.getOrder() ) )
                    if self.sugarGate.getOrder() == GateOrder.NO_ORDER:
                        self.sugarGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                        self.sugarFed.clickflash()
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar correct" ) )
                        logging.info("SUGAR GATE OPEN")
                        logging.info("SUGAR WATER DROP")                        
                        self.waterPump.drop()
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
                        
            
            # SOCIAL
            
            if socialFedRead != None:
            
                # correct nose poke
                if "In" in socialFedRead:
                    logging.info("Nose poke SOCIAL : " + str( socialFedRead ) )
                    print("current order " + str( self.socialGate.getOrder() ) )
                    if self.socialGate.getOrder() == GateOrder.NO_ORDER:
                        self.socialGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                        self.socialFed.clickflash()
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

            
        def phase2and3PokeRead( sugarFedRead, socialFedRead , nosePokeDirection ):

            # SUGAR 
            
            if sugarFedRead != None:
                
                # incorrect nose poke
                if "In" in sugarFedRead and not nosePokeDirection in sugarFedRead:
                    if self.sugarGate.getOrder() == GateOrder.NO_ORDER:
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar wrong") )                        
                
                # correct nose poke
                if "In" in sugarFedRead and nosePokeDirection in sugarFedRead:
                    logging.info("Nose poke SUGAR")
                    
                    print("current order " + str( self.sugarGate.getOrder() ) )
                    if self.sugarGate.getOrder() == GateOrder.NO_ORDER:
                        self.sugarGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                        self.sugarFed.clickflash()
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar correct" ) )
                        logging.info("SUGAR GATE OPEN")
                        logging.info("SUGAR WATER DROP")                        
                        self.waterPump.drop()
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
                        
            
            # SOCIAL
            
            if socialFedRead != None:
                # incorrect nose poke
                if "In" in socialFedRead and not nosePokeDirection in socialFedRead:
                    if self.socialGate.getOrder() == GateOrder.NO_ORDER:
                        self.deviceListener( DeviceEvent( "experiment" , self, "nose poke social wrong") )
            
                # correct nose poke
                if "In" in socialFedRead and nosePokeDirection in socialFedRead:
                    logging.info("Nose poke SOCIAL")
                    print("current order " + str( self.socialGate.getOrder() ) )
                    if self.socialGate.getOrder() == GateOrder.NO_ORDER:
                        self.socialGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                        self.socialFed.clickflash()
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
            
            # phase 2 and 3 logic
            if "any" in nosePokeDirection:
                phaseAnyPokeRead(sugarFedRead, socialFedRead)
            else:
                phase2and3PokeRead(sugarFedRead, socialFedRead, nosePokeDirection )
            
            # each 10s log
            
            if self._currentPhase not in self.sugarPokeList:                    
                self.sugarPokeList[self._currentPhase]=[]
            if self._currentPhase not in self.socialPokeList:
                self.socialPokeList[self._currentPhase]=[]
                
            sugarOk = 0
            sugarWrong = 0
            lastSugar = self.sugarPokeList[self._currentPhase][-self.NB_LAST_POKE:] 
            for i in lastSugar:
                if i:
                    sugarOk +=1
                else:
                    sugarWrong +=1
            
            socialOk = 0
            socialWrong = 0
            lastSocial = self.socialPokeList[self._currentPhase][-self.NB_LAST_POKE:]
            for i in lastSocial:
                if i:
                    socialOk +=1
                else:
                    socialWrong +=1
                
            
            nbPassInSugar=0
            for event in self.getEventsFromDevice( self._currentPhase , self.sugarGate ):
                if "ANIMAL BACK IN SIDE A" in event.description:
                    nbPassInSugar+=1

            nbPassInSocial=0
            for event in self.getEventsFromDevice( self._currentPhase , self.socialGate ):
                if "ANIMAL BACK IN SIDE A" in event.description:
                    nbPassInSocial+=1
            
                    
            if self.getChrono(0) > self.PERIOD_LOG_SECOND:
                logging.info( str( self._currentPhase ) + " : sugar: " + str( ( sugarOk, sugarWrong ) ) + " social: " + str( ( socialOk, socialWrong ) ) )
                print( "len lastsugar/lastsocial: " , len(lastSugar) , len( lastSocial ) , " nb pass : " , nbPassInSugar , nbPassInSocial )
                self.resetChrono(0)
                
            if self.getChrono("timerMail") > self.PERIOD_MAIL_INFO: # each hour log # TODO 60*60
                text = ""
                text+="Current phase: " + str( self._currentPhase ) + "\n"
                text+="SUGAR ok/wrong: " + str( ( sugarOk, sugarWrong ) ) + "\n"
                text+="SOCIAL ok/wrong: " + str( ( socialOk, socialWrong ) ) + "\n"
                text+="\n"
                text+="NB pass in sugar: " + str( nbPassInSugar ) + "\n"
                text+="NB pass in social: " + str( nbPassInSocial ) + "\n"
                text+="\n"
                text+="Current duration of this phase: " + str( self.getChronoHMS( self._currentPhase ) )  + "\n"
                text+="Current duration of the experiment: " + str( self.getChronoHMS( "experiment" ) ) + "\n"
                text+="\n"
                text+="debug info:\n"
                text+="\n"
                text+="Sugar pokelist of current phase (all):"
                text+="\n"
                text+= str( self.sugarPokeList[self._currentPhase] )
                text+="\n"
                text+="Social pokelist of current phase (all):"
                text+="\n"
                text+= str( self.socialPokeList[self._currentPhase] )
                text+="\n"                
                text+="Sugar pokelist of current phase ([-self.NB_LAST_POKE:]):"
                text+="\n"
                text+= str( self.sugarPokeList[self._currentPhase][-self.NB_LAST_POKE:] )
                text+="\n"
                text+="Social pokelist of current phase ([-self.NB_LAST_POKE:]):"
                text+="\n"
                text+= str( self.socialPokeList[self._currentPhase][-self.NB_LAST_POKE:] )
                text+="\n"                
                text+="\n"
                 
                                
                self.mailInfo( "each 1h Info " + str( self._currentPhase ) , content=text, sendLog=True )                
                self.resetChrono("timerMail")
            
            # tests to enter next phase:
            

            if socialOk> self.NB_POKE_OK_TO_VALIDATE and sugarOk > self.NB_POKE_OK_TO_VALIDATE and len(lastSugar) >= self.NB_LAST_POKE-1 and len( lastSocial ) >=self.NB_LAST_POKE-1:
                if self._currentPhase == self.Phase.PHASE2:
                    self.setPhase( Experiment.Phase.PHASE3 )
                    self.resetChrono( Experiment.Phase.PHASE3 )
                    return
                if self._currentPhase == self.Phase.PHASE3:
                    self.setPhase( Experiment.Phase.PHASE4 )
                    self.resetChrono( Experiment.Phase.PHASE4 )                    
                    return
                
            

            
        
        if self._currentPhase == Experiment.Phase.PHASE_ANY_NOSE_POKE:            
            nosePokePhase( "any" ) #any hole accepted
            
        if self._currentPhase == Experiment.Phase.PHASE2:
            
            nosePokePhase( self.initialNosePokeDirection )
            
        if self._currentPhase == Experiment.Phase.PHASE3: # reversal
            
            nosePokePhase( self.oppositeNosePokeDirection )            
                    
        if self._currentPhase == Experiment.Phase.PHASE4: # progressive ratio
            
            nosePokeDirection = self.initialNosePokeDirection
            
            '''
            self.socialProgressiveRatio = 0
            self.sugarProgressiveRatio = 0
            '''
            
                
            # correct nose poke
            if sugarFedRead != None:
                if "In" in sugarFedRead and nosePokeDirection in sugarFedRead:
                    self.sugarGateNbPoke+=1
                    logging.info("Nose poke progressive SUGAR : " + str( self.sugarGateNbPoke ) + " / " + str( self.progressiveRatio[self.sugarProgressiveRatio] ) )
                    click= False
                    if self.sugarGate.getOrder() == GateOrder.NO_ORDER:
                        click=True
                                            
                    if self.sugarGateNbPoke >= self.progressiveRatio[self.sugarProgressiveRatio]:
                        logging.info("Nose poke progressive ratio SUGAR reached:  #" + str( self.sugarProgressiveRatio ) + " / " + str (self.progressiveRatio[self.sugarProgressiveRatio] ) )
                        self.sugarGateNbPoke=0
                        self.sugarProgressiveRatio+=1                    
                                    
                        print("current order " + str( self.sugarGate.getOrder() ) )
                        if self.sugarGate.getOrder() == GateOrder.NO_ORDER:
                            self.sugarGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                            self.sugarFed.clickflash()
                            click=False                        
                            logging.info("SUGAR GATE OPEN")
                            logging.info("SUGAR WATER DROP")                        
                            self.waterPump.drop()                        
                        else:                        
                            logging.info("SUGAR GATE ALREADY OPEN")
                    if click:
                        self.sugarFed.click()
                        
            if socialFedRead != None:
                if "In" in socialFedRead and nosePokeDirection in socialFedRead:
                    self.socialGateNbPoke+=1
                    logging.info("Nose poke progressive SOCIAL : " + str( self.socialGateNbPoke ) + " / " + str( self.progressiveRatio[self.socialProgressiveRatio] ) )
                    click= False
                    if self.socialGate.getOrder() == GateOrder.NO_ORDER:
                        click=True
                                            
                    if self.socialGateNbPoke >= self.progressiveRatio[self.socialProgressiveRatio]:
                        logging.info("Nose poke progressive ratio SOCIAL reached:  #" + str( self.socialProgressiveRatio ) + " / " + str (self.progressiveRatio[self.socialProgressiveRatio] ) )
                        self.socialGateNbPoke=0
                        self.socialProgressiveRatio+=1                    
                                    
                        print("current order " + str( self.socialGate.getOrder() ) )
                        if self.socialGate.getOrder() == GateOrder.NO_ORDER:
                            self.socialGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                            self.socialFed.clickflash()
                            click=False                        
                            logging.info("SOCIAL GATE OPEN")                                                                        
                        else:                        
                            logging.info("SOCIAL GATE ALREADY OPEN")
                    if click:
                        self.socialFed.click()
            
            
            
            if self.getChrono(0) > self.PERIOD_LOG_SECOND:
                logging.info( str( self._currentPhase ) + " : current ratio: social:" + str( self.socialGateNbPoke ) + " / " + str( self.progressiveRatio[self.socialProgressiveRatio] ) + " sugar:" + str( self.sugarGateNbPoke ) + " / " + str( self.progressiveRatio[self.sugarProgressiveRatio] ) )
                self.resetChrono( 0 )
            
            if self.getChrono("timerMail") > self.PERIOD_MAIL_INFO: # each hour log 
                text = ""

                text+="Current phase: " + str( self._currentPhase ) + "\n"
                text+="current ratio:\n"
                text+="social:" + str( self.socialGateNbPoke ) + " / " + str( self.progressiveRatio[self.socialProgressiveRatio] ) + " step: " + str(self.socialProgressiveRatio) + "\n"
                text+="sugar:" + str( self.sugarGateNbPoke ) + " / " + str( self.progressiveRatio[self.sugarProgressiveRatio] ) + " step: " + str(self.sugarProgressiveRatio) + "\n"
                
                text+="Current duration of this phase: " + str( self.getChronoHMS( self._currentPhase ) ) + "\n"
                text+="Current duration of the experiment: " + str( self.getChronoHMS( "experiment" ) ) + "\n"
                                
                self.mailInfo( "each 1h Info " + str( self._currentPhase ) , content=text, sendLog=True )                
                self.resetChrono("timerMail")
            
            
            # phase logic:
            
            # tests to enter next phase:            
            # 4h sans rien ou fin des 45 heures de manip
            
            
            
                

            return
        
        if self._currentPhase == Experiment.Phase.END:
            self.socialGate.open()
            self.sugarGate.open()
            self.mailInfo( "EXPERIMENT FINISHED - LOG " + str(self._currentPhase), sendLog=True )
            quit()
            

if __name__ == '__main__':
        
    experiment = Experiment()
    
    
    while( True ):
        
        experiment.runLogic()
        sleep( 0.05 )
    
    
    
    '''
    while ( True ):
        
        fedRead = fed.read()
        if fedRead != None:
            if "In" in fedRead :
                logging.info("Nose poke SUGAR")
                
                print("current order " + str( gate.getOrder() ) )
                if gate.getOrder() == GateOrder.NO_ORDER:
                    gate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                    fed.click()
                    logging.info("SUGAR GATE OPEN")
                    logging.info("SUGAR WATER DROP")
                    print("Order SET")
                    print("Dropping")
                    waterPump.drop()
                else:
                    print("Gate already in 1 animal only mode.")
                    logging.info("SUGAR GATE ALREADY OPEN")

        fedRead = fed2.read()
        if fedRead != None:
            if "In" in fedRead :
                logging.info("Nose poke SOCIAL")
                print("current order " + str( gate2.getOrder() ) )
                if gate2.getOrder() == GateOrder.NO_ORDER:
                    gate2.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd = True )
                    fed2.click()
                    logging.info("SOCIAL GATE OPEN")
                    print("Order SET")
                else:
                    print("Gate already in 1 animal only mode.")
                    logging.info("SOCIAL GATE ALREADY OPEN")
            
        sleep( 0.05 )
        
    '''
    
    
    
    