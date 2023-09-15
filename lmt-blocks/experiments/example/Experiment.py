'''
Created on 22 juin 2022

@author: Fab
'''
from time import sleep
import threading
from blocks.DeviceEvent import DeviceEvent
import logging
from datetime import datetime
import sys
import os
from random import randint, random
from blocks.FED3.Fed3Manager import Fed3Manager
from blocks.waterpump.WaterPump import WaterPump
from blocks.autogate.Gate import Gate, GateOrder
from experiments.api.PhaseManager import PhaseManager
from experiments.api.Phase import Phase
from mail.Mail import LMTMail
from experiments.api.Chronometer import Chronometer

class Experiment(object):
    '''
    
    This an experiment skeleton example    
    
    The class is composed by an init part, a loop, and an event part.
    - The init starts the experiment and initiates threads.
    - The event will receive messages from all the devices
    - The loop will run until self.isRunning == True
    
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


    def __init__(self , name ):
        
        # setup logfile
        self.logFile = "log/gateLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"    
        os.makedirs(os.path.dirname(self.logFile), exist_ok=True)
        logging.basicConfig(level=logging.INFO, filename=self.logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))        
        logging.info('Log file: ' + self.logFile )
        logging.info('Application started')
        
        if name == None:
            name = "exp#"+str( randint( 0 , 1000 ) )
        logging.info('Experiment created: ' + name )
        self.name = name
          
        self.chronometer = Chronometer()
        self.chronometer.resetChrono("experiment")
        
        # this is a threading lock used to avoid several concurrent codes running at the same time.
        # it prevents from having several events called in different threads that may create race condition
        self.lock = threading.Lock()
        
        self.initHardware()
        self.initSoftware()
        
        
                
        
        # creates the loop thread so that the loop function will monitor the experiment until self.isRunning==True
        self.loopThread = threading.Thread(target=self.loop)

        # initialize self.isRunning
        self.isRunning = True
        
        self.phaseManager.start() 
        
        # start loop
        self.loopThread.start()
    
    def P_init_Phase1(self):
    
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
        
    def P_loop_Phase1(self):
        
        # check if we had 10 go-through for both gates.
            
        nbPassOkInSocial = 0
        for event in self.phaseManager.getPhaseEventFromDevice( self.socialGate ):
            if "ANIMAL BACK IN SIDE A" in event.description:
                nbPassOkInSocial+=1
            
        nbPassOkInSugar = 0
        for event in self.phaseManager.getPhaseEventFromDevice( self.sugarGate ):
            if "ANIMAL BACK IN SIDE A" in event.description:
                nbPassOkInSugar+=1

        '''
        # TODO
        if self.getChrono(0) > self.PERIOD_LOG_SECOND:            
            logging.info( "PHASE 1 : Nb pass in Social : " + str( nbPassOkInSocial ) + " Nb pass in Sugar : " + str ( nbPassOkInSugar ) )
            self.resetChrono(0)
        '''
            
        '''
        if self.getChrono( Experiment.Phase.PHASE1 ) > self.PHASE1_NB_SECOND_ABORT:
            self.abort("timeout")
        '''
            

        if nbPassOkInSocial >= self.PHASE1_NB_PASS_OK_IN_SOCIAL and nbPassOkInSugar >= self.PHASE1_NB_PASS_OK_IN_SUGAR:

            # empty gates in A if needed
            self.sugarGate.setOrder( GateOrder.EMPTY_IN_A )
            self.socialGate.setOrder( GateOrder.EMPTY_IN_A )
            self.phaseManager.switchToNextPhase()

                
                                
            

    
    def initSoftware(self):
        
        # init phases
        
        self.phaseManager = PhaseManager()
        #self.phaseManager.addPhase( Phase("Init experiment" , P_initE) )
        self.phaseManager.addPhase( Phase("Phase 1 : any nose poke" , initFunction = self.P_init_Phase1, loopFunction= self.P_loop_Phase1 ) )
        self.phaseManager.addPhase( Phase("Phase 2 : sided nose poke") )
        self.phaseManager.addPhase( Phase("Phase 3 : reversal nose poke") )
        self.phaseManager.addPhase( Phase("Phase 4 : progressive ratio") )
        self.phaseManager.addPhase( Phase("End of experiment") )
        
        # init data
        
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

        self.socialGate.addDeviceListener( self.event )
        self.sugarGate.addDeviceListener( self.event )
        self.waterPump.addDeviceListener( self.event )
        self.socialFed.addDeviceListener( self.event )
        self.sugarFed.addDeviceListener( self.event )
        
        
    def event(self, deviceEvent : DeviceEvent ):
        
        # a deviceEvent is received
        
        # acquire the lock to be the only code passing in this critical section
        self.lock.acquire()
        
        self.phaseManager.callPhaseLoop()
        
        
        # management of events goes here.        
        # .
        # .
        # .
        
        # release the lock so that other caller can send events.
        self.lock.release()
    
        
    def loop(self): # TODO faire sauter la loop avec un timer d'experience
        
        while( self.isRunning ):
            # acquire the lock to be sure no event will change the data during the run of this function
            self.lock.acquire()
            
            # management of the experiment goes here
            # .
            # .
            # .
            
            # test end condition (timeout)
            if self.getChrono("experiment") > 60*60*45:
                self.phaseManager.switchToLastPhase()
            return                
            
            # release the lock to let other process like events run
            self.lock.release()
            sleep( 0.05 )
    
        
if __name__ == '__main__':
        
    experiment = Experiment()

    while( experiment.isRunning ):        
        sleep( 1 )
    
    logging.info("Experiment stopped.")
