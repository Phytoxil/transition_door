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
        
        PHASE1 = 101        
        PHASE2 = 102        
        END = 106           
        
    def __init__( self , name = None ):
        
        # setup logfile
        self.logFile = "control_sucrose_motivation - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"    
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
        
        
        # choose initial poke:
        
        self.initialNosePokeDirection = "left"        
        self.oppositeNosePokeDirection = "right"
        
        
        print("------------------")
        print("1: left / 2: right")        
        answer = input("Select hole:")
        if "2" in answer:            
            self.initialNosePokeDirection = "right"
            self.oppositeNosePokeDirection = "left"
        
        
        logging.info("Initial Nose poke direction: " + self.initialNosePokeDirection )
        
        
        self.PERIOD_MAIL_INFO = 60*60 # each hour
            
        self.PHASE1_NB_PASS_OK_IN_SOCIAL = 10 #10
        self.PHASE1_NB_PASS_OK_IN_SUGAR = 10 #10
                
        self.PERIOD_LOG_SECOND = 10
        
        
        self.TIME_ERROR_CHRONO = 10 # number of second where the opening of the gate is disabled.
        
        self.NB_LAST_POKE = 10
        self.NB_POKE_OK_TO_VALIDATE = self.NB_LAST_POKE * ( 2/3 )  
        
        
        self.chrono = {}
        self.resetChrono("experiment")
        
        self.deviceEventList = {}
        
        '''
        # list of correct nose poke sequence ( false or true if ok. )
        self.socialPokeList = { } 
        self.sugarPokeList = { }
        self.sugarAndSocialPokeList = {}
        
        self.sugarSequence = Sequence()
        self.socialSequence = Sequence()
        '''
        
        self.sugarPokeList = []
        
        self.progressiveRatio = []
        for i in range( 0 , 100 ):
            self.progressiveRatio.append( int( 5* exp( 0.2 * i ) -4 ) ) #5 × e0.2n -5
            #self.progressiveRatio.append( int( 5* exp( 0.2 * i )  ) ) #5 × e0.2n -5
            
        print ( self.progressiveRatio )            
        
        self.sugarProgressiveRatio = 0
        self.sugarGateNbPoke = 0
        
        self.sugarFed.lightoff()
                        
        
        #self.setPhase( Experiment.Phase.PHASE2 )        
        self.setPhase( Experiment.Phase.PHASE1 )

    '''    
    def signal(self):
        self.sugarFed.click()
        #self.sugarFed.clickflash()
    '''
    
    def initHardware(self):
        
        logging.info('Init hardware.')
                    
        self.sugarFed = Fed3Manager( comPort="COM4" , name= "sugarFed")        
        self.waterPump = WaterPump(comPort="COM90", name="WaterPump" )
        
        self.waterPump.addDeviceListener( self.deviceListener )
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
        #logging.info( "nb event in memory: " + str( len( self.deviceEventList)  ) )
        if not self.currentPhase in self.deviceEventList:
            self.deviceEventList[self.currentPhase] = []

                    
        self.deviceEventList[self.currentPhase].append( deviceEvent )
        
        # PHASE 2
        '''        
        
        def checkPoke( nature ):            
            
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
                     
        
        '''
        # prevent from having too much data in memory:
        if len( self.deviceEventList[self.currentPhase] ) > 1000:
            self.deviceEventList[self.currentPhase].pop( 0 )
        '''
            
    def waterdrop( self ):
        logging.info("Water drop")
        self.waterPump.pump( 255, 30 )
    
    def mailInfo( self, subject, content=None , sendLog = False ):
        
        if content == None:
            content = subject
        
        mails = ["fabrice.de.chaumont@gmail.com","benoit.forget@pasteur.fr"]
        subject = subject + " ctrl_sucrose_motiv exp:"+str( self.name ) 
        
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

        socialFedRead = self.socialFed.read()
        '''
        sugarFedRead = self.sugarFed.read()
        
        # check lights and chronos        
        
        c = "sugarLight"
        if self.chronoExists( c ):
            if self.getChrono( c ) > self.TIME_ERROR_CHRONO:                    
                self.sugarFed.lightoff()
                self.removeChrono( c )
                
        c = "errorSugarChrono"
        if self.chronoExists( c ):
            if self.getChrono( c ) > self.TIME_ERROR_CHRONO:                
                self.removeChrono( c )
        
        
        
        if self.currentPhase == Experiment.Phase.PHASE1:
            
            nosePokeDirection = self.initialNosePokeDirection
            
            if sugarFedRead != None:

                if "In" in sugarFedRead:
                                
                    if self.chronoExists( "sugarLight" ) or self.chronoExists( "errorSugarChrono" ):
                        if nosePokeDirection in sugarFedRead:
                            logging.info( "nose poke canceled (but good hole)" )
                        else:
                            logging.info( "nose poke canceled (and wrong hole)" )
                        
                    if not self.chronoExists( "sugarLight" ) and not self.chronoExists( "errorSugarChrono" ):
                    
                        # wrong nose poke
                        if not nosePokeDirection in sugarFedRead:
                            
                            #logging.info("Nose poke SUGAR")
                            self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar wrong") )
                            self.resetChrono( "errorSugarChrono" )
                            self.sugarPokeList.append( "sugar FALSE")
                                                                        
                        # correct nose poke
                        if nosePokeDirection in sugarFedRead and not self.chronoExists( "sugarLight" ):
                            
                            self.deviceListener( DeviceEvent( "experiment" , self, "nose poke sugar ok") )                
                            if "right" in sugarFedRead:
                                self.sugarFed.light( direction="right" )
                            if "left" in sugarFedRead:
                                self.sugarFed.light( direction="left" )
                            self.resetChrono( "sugarLight" )
                            self.waterdrop()
                            self.sugarPokeList.append( "sugar TRUE")                        
        
                
        # check end of phase 1:
        
        if self.currentPhase == Experiment.Phase.PHASE1:
            
            if len ( self.sugarPokeList ) > 20:                
                nbOk= 0                
                for poke in self.sugarPokeList[-20:]:
                    if "TRUE" in poke:
                        nbOk +=1
                print(f"Nb correct nose poke: {nbOk}")
                if nbOk>13:
                    self.setPhase( Experiment.Phase.PHASE2 )
                    return


        if self.currentPhase == Experiment.Phase.PHASE1:
            if self.getChrono(0) > self.PERIOD_LOG_SECOND:            
                logging.info( f"PHASE 1 : *pokeList* {self.sugarPokeList}" ) #Nb pass in Social : " + str( nbPassOkInSocial ) + " Nb pass in Sugar : " + str ( nbPassOkInSugar ) )
                self.resetChrono(0)
                            
        
        if self.currentPhase == Experiment.Phase.PHASE2:
                
            nosePokeDirection = self.initialNosePokeDirection
            

            # correct nose poke
            if sugarFedRead != None:

                if self.chronoExists( "sugarLight" ) and "In" in sugarFedRead:
                
                    if nosePokeDirection in sugarFedRead:
                        logging.info( "nose poke canceled (but good hole)" )
                    else:
                        logging.info( "nose poke canceled (and wrong hole)" )
                    return
                    
                if "In" in sugarFedRead and nosePokeDirection in sugarFedRead:
                    
                    logging.info("Nose poke progressive SUGAR : " + str( self.sugarGateNbPoke ) + " / " + str( self.progressiveRatio[self.sugarProgressiveRatio] ) )                        
                        
                    self.sugarGateNbPoke+=1                   
                                            
                    if self.sugarGateNbPoke >= self.progressiveRatio[self.sugarProgressiveRatio]:
                        logging.info("Nose poke progressive ratio SUGAR reached:  #" + str( self.sugarProgressiveRatio ) + " / " + str (self.progressiveRatio[self.sugarProgressiveRatio] ) )
                        self.sugarGateNbPoke=0
                        self.sugarProgressiveRatio+=1                    
                                    
                        logging.info("SUGAR WATER DROP")                        
                        self.sugarFed.light( direction = nosePokeDirection )
                        self.resetChrono( "sugarLight" )
                        self.waterdrop()
                
                if "In" in sugarFedRead and nosePokeDirection not in sugarFedRead:
                    
                    logging.info("wrong nose poke")
                    
            
            if self.getChrono( self.currentPhase ) > 4*60*60: # 4 hours
                self.setPhase( Experiment.Phase.END )
                self.resetChrono( Experiment.Phase.END )
                self.sugarFed.lightoff()
                
            
            if self.getChrono(0) > self.PERIOD_LOG_SECOND:
                logging.info( str( self.currentPhase ) + " : current ratio: sugar:" + str( self.sugarGateNbPoke ) + " / " + str( self.progressiveRatio[self.sugarProgressiveRatio] ) )
                logging.info( str( "current phase duration: " + str ( self.getChronoHMS( self.currentPhase ) ) ) )
                self.resetChrono( 0 )
            
        # ---------------------------------------------------------------------------
        
                        
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
    
    
    
    
    