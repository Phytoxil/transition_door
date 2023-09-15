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
from collections import Counter
from future.backports.test.pystone import TRUE

sides = {
    'left': {
        'controlLight': 'RGBWdef_R000_G000_B000_W100_SideL',
        'sideToChoose': 'leftIn'
    },
    'right': {
        'controlLight': 'RGBWdef_R000_G000_B000_W100_SideR',
        'sideToChoose': 'rightIn'
    }
}


class AnimalManager():
    #this class allows to keep track of what happens to each animal
    
    def __init__( self , rfid ):
        
        # init
        self.rfid = rfid
        self.enableRepeat = False # repeat to phase
        self.currentPhaseIndex = 0
        self.phaseList = []
        self.phaseList.append( Phase1( rfid  ) )        
        self.phaseList.append( Phase2( rfid  ) )
        #self.phaseList.append( Phase2( rfid ) )        
        
        
        self.currentPhase = self.phaseList[self.currentPhaseIndex]
    
    def deviceListener(self , event ):
        
        if "Animal allowed to cross:" in event.description:
            logging.info( event.description )
            logging.info(f"This manager is using the gate with animal {self.rfid}")
            
            
            rfid = event.description.split(" ")[-1]
            if rfid in self.rfid: # means that the animal passing through is the one of this manager
                self.gate = event.deviceObject
                self.currentPhase.gate = self.gate
                logging.info( f"This manager takes over on phase : {self.currentPhase} ")
                self.enableRepeat = True
                
        if self.enableRepeat:
            if self.currentPhase != None:
                self.currentPhase.deviceListener( event )
                
        '''
        check if animal gets out
        
        if rfid in self.rfid: # means that the animal passing through is the one of this manager
            self.gate = event.deviceObject
            self.currentPhase.gate = self.gate
            logging.info( f"This manager takes over on phase : {self.currentPhase} ")
            self.enableRepeat = True
        '''     
           
                
    def phaseDoneCallBack(self):
        print("The current phase is done !!")
        self.currentPhaseIndex+=1
        self.currentPhase = self.phaseList[self.currentPhaseIndex]

def TrainingTrial():
    '''
    This is the definition of the training trial
    2 nose pokes active / light on inside both holes until nose poke
    when poke, reward delivered
    trial stopped
    '''
    
    def __init__( self , rfid ): #phaseDoneCallBack, animal = None , gate = None ):
        
        self.sideNosePoke = None
        self.checkNosePoke = False
        self.rfid = rfid
        self.endingTrial = False
        self.gate = None 
        
    def deviceListener(self, event): #event == fedRead = self.fed.read()
        self.startTimeTrial = datetime.now()
        #initiate the trial by turning on lights in both holes
        self.fed.controlLight('RGBWdef_R100_G000_B000_W000_Sideb') #how to turn both lights on?
        time.sleep(0.5)
        
        if "fed3" in event.deviceType: # test if any nose poke is performed by the animal
            if "nose poke" in event.description:
                # we had a nose poke.
                self.checkNosePoke = True
                #turn off the light
                self.fed.lightoff()
                
                self.sideNosePoke = event.data
                
                logging.info( f"Training trial with animal {self.rfid} / poke side: {event.data}" )
        
        time.sleep(0.5)
        self.endingTrial = True
                    
    def __str__(self):
        return f"Habituation trial with animal {self.rfid}"


class Trial():
    def __init__(self, fed=None, logging=None, delayPhases=None, trialCompleted=False, sideToChoose='lightOn', phase1Completed=False, pelletPicked=False, startTimePhase1: datetime = None, endTimePhase1: datetime = None, startTimePhase2: datetime = None, endTimePhase2: datetime = None, result=None):
        self.fed = fed
        self.delayPhases = delayPhases
        self.logging = logging
        self.trialCompleted = trialCompleted
        self.randomSide = random.choice(['left', 'right'])
        self.phase1Completed = phase1Completed
        self.pelletPicked = pelletPicked
        self.startTimePhase1 = startTimePhase1
        self.endTimePhase1 = endTimePhase1
        self.startTimePhase2 = startTimePhase2
        self.endTimePhase2 = endTimePhase2
        self.result = result
        
    def step1(self):
        self.startTimeStep1 = datetime.now()
        while not self.step1Completed:
            fedRead = self.fed.read()
            if fedRead != None:
                self.fed.lightoff()
                time.sleep(0.5)
                if sideToChoose == 'lightOn':
                    if sides[self.randomSide]['sideToChoose'] in fedRead:
                        self.logging.info('[FED] step 1 success' + fedRead)
                        self.phase1Completed = True
    
                    else:
                        self.fed.controlLight('RGBWdef_R100_G000_B000_W000_Sideb')
                        time.sleep(0.5)
                        self.fed.lightoff()
                        self.logging.info('[FED] phase 1 error' + fedRead)
                        self.trialCompleted = True
                        self.phase1Completed = True
                        self.startTimePhase2 = None
                        self.endTimePhase2 = None
                self.endTimePhase1 = datetime.now()
        
class Phase1():

    '''
    This is the definition of the training phase
    2 nose pokes active / light on inside
    sessions of 20 trials, separated by 20 s of inactivity between trials (lights off)
    reward max reached > stop the winning machine > light off and inactive
    open the door for the back trip in the housing cage (after a max of 20 trials in a session, or when criteria reached or when no pokes for more than 20 min)
    decision to stop this phase: 80 rewards reached?
    data collected: number of pokes when illuminated, number of pokes when inactive
    '''
    
    
    def __init__( self , rfid ): #phaseDoneCallBack, animal = None , gate = None ):
        
        self.nbNosePoke = 0
        self.nbNosePokeTotal = 0
        self.rfid = rfid
        self.endingSession = False
        self.endingPhase = False
        #self.phaseDoneCallBack = phaseDoneCallBack
        self.gate = None 
        
    
    def deviceListener(self, event):
        
        if "fed3" in event.deviceType: # test if any nose poke is performed by the animal
            if "nose poke" in event.description:
                # we had a nose poke.
                self.nbNosePoke += 1
                self.nbNosePokeTotal += 1 
                logging.info( f"PHASE 1 with animal {self.rfid} / current number of poke = {self.nbNosePoke} side: {event.data}" )
        
        if self.nbNosePoke >= 20: #if the max number of pokes is reached for the session, this ends the session and re-opens the gate
            self.endingSession = True
            self.gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )
            self.nbNosePoke = 0
                        
        if self.endingSession: #if the session ends, this logs the info in the log file
            if "gate" in event.deviceType:
                if "ALLOW_SINGLE_B_TO_A DONE" in event.description:
                    # animal is back.
                    logging.info( f"PHASE 1 with animal {self.rfid} ANIMAL is back to A ! ending session...")
                    #self.phaseDoneCallBack()
    
        ####TO DO: end the phase 1 if max number of rewards reached
        if self.nbNosePokeTotal >= 80:
            self.endingPhase = True
            self.gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )
        
        if self.endingPhase: #if the session ends, this logs the info in the log file
            if "gate" in event.deviceType:
                if "ALLOW_SINGLE_B_TO_A DONE" in event.description:
                    # animal is back.
                    logging.info( f"PHASE 1 with animal {self.rfid} ANIMAL is back to A ! ending phase...")
                    #self.phaseDoneCallBack()
    
                    
    def __str__(self):
        return f"PHASE 1 with animal {self.rfid}"


class Phase2():

    '''
    This is the definition of the second phase (simple poke in an illuminated hole)
    
    random side chosen by the system (not more than 3 in a row in the same side)
    the hole at this side gets illuminated for 20s: 
    - if poke in the illuminated side within 20s => reward + inactivity for 20 s
    - if no poke in the illuminated side but poke in the non illuminated side => one center light on and time out of 40 s (punishment)
    - if no poke at all => light off and inactivity for 20s
    Session of 20 trials max or if no pokes for more than 20min
    open the door for the back trip in the housing cage
    turn to next phase if 90% of correct answers in the last 20 trials.
    data collected: time of pokes when illuminated (correct), time of pokes in non illuminated hole (incorrect), time of pokes when inactive, time of missed trials (no pokes)
    '''
    
    def __init__( self , phaseDoneCallBack, animal = None , gate = None ):
        
        self.nosePokeSession = 0
        self.nbNosePokeTotal = 0
        self.nbNosePokeCorrect = 0
        self.nbNosePokeIncorrect = 0
        self.nbNosePokeWhenInactive = 0
        self.NbMissedTrials = 0
        self.trialList = []
        self.animal = animal
        self.endingSession = False
        self.endingPhase = False
        self.phaseDoneCallBack = phaseDoneCallBack
        self.gate = gate
        
        logging.info( "init phase 2")
    
    def deviceListener(self, event):
        
        logging.info("PHASE 2 device listener")
        
        #put light on in a hole on a random side
        
        #within the 20 s of illumination of the nose poke hole
        if "fed3" in event.deviceType: # test if any nose poke is performed by the animal
            if "nose poke" in event.description:
                # we had a nose poke; store it to count the total number of nose pokes.
                self.nbNosePokeTotal += 1
                self.nosePokeSession += 1          
                logging.info( f"PHASE 1 with animal {self.rfid} / current number of pokes = {self.nbNosePokeTotal} side: {event.data}" )
                
                #if nose poke in the correct hole: 
                    #store correct nose poke
                    #self.nosePokeCorrect += 1
                    #self.trialList.append( 'correct' )
                    #turn light off in nose poke hole
                    #inactivity 20 s
                        #if nose poke during inactivity
                        #self.nbNosePokeWhenInactive += 1
                
                #if nose poke in the incorrect hole:
                    #store incorrect nose poke
                    #self.nosePokeIncorrect += 1
                    #self.trialList.append( 'incorrect' )
                    #turn light off in nose poke hole
                    #turn on light in the center as punishment
                    #inactivity 40 s
                        #if nose poke during inactivity
                        #self.nbNosePokeWhenInactive += 1
                
                #if no nose poke:
                    #store missed trial
                    #self.nbMissedTrials += 1
                    #self.trialList.append( 'missed' )
        
        if self.nbNosePokeSession >= 20: #if the max number of pokes is reached for the session, this ends the session and re-opens the gate
            self.endingSession = True
            self.gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )

                        
        if self.endingSession: #if the session ends, this logs the info in the log file
            self.nbNosePokeSession = 0
            if "gate" in event.deviceType:
                if "ALLOW_SINGLE_B_TO_A DONE" in event.description:
                    # animal is back.
                    logging.info( f"Session of PHASE 2 with animal {self.rfid} ANIMAL is back to A ! ending session...")
                    #self.phaseDoneCallBack()
        
        #end of the phase if 90% of correct answers in the last 20 trials
        #if len( trialList ) > 20:
            #counting = Counter( trialList )
            #proportionCorrectPokes = counting['correct'] / 20
            
            #if proportionCorrectPokes >= 0.9:
                #self.endingPhase == True
        
        if self.endingPhase: #if the phase ends, this logs the info in the log file
            if "gate" in event.deviceType:
                if "ALLOW_SINGLE_B_TO_A DONE" in event.description:
                    # animal is back.
                    logging.info( f"PHASE 2 with animal {self.rfid} ANIMAL is back to A ! ending phase...")
                    #self.phaseDoneCallBack()


class Phase3():

    '''
    This is the definition of the third phase (reversal learning to poke in the non illuminated hole)

    random side chosen by the system (not more than 3 in a row in the same side)
    the hole at this side gets illuminated for 20s: 
    - if poke in the non illuminated side within 20s => reward + inactivity for 20 s
    - if no poke in the non illuminated side but poke in the illuminated side => one center light on and time out of 30 s (punishment)
    - if no poke at all => one center light on and inactivity for 20s
    Session of 20 trials max or if no pokes for more than 20min
    open the door for the back trip in the housing cage
    turn to next phase if 90% of correct answers in the last 20 trials.
    data collected: time of pokes when non illuminated (correct), time of pokes in illuminated hole (incorrect), time of pokes when inactive, time of missed trials (no pokes)
    '''
    
    def __init__( self , phaseDoneCallBack, animal = None , gate = None ):
        
        '''
        self.nbNosePoke = 0
        self.animal = animal
        self.endingPhase = False
        self.phaseDoneCallBack = phaseDoneCallBack
        self.gate = gate
        '''
        logging.info( "init phase 3")
    
    def deviceListener(self, event):
        
        logging.info("PHASE 3 device listener")
        

class Phase4():

    '''
    This is the definition of the fourth phase (learning to poke in the non illuminated hole after a delay)

    random side chosen by the system (not more than 3 in a row in the same side)
    the hole at this side gets illuminated for 20s and then extinction. 
    - Within a delay of 3 s: 
        - if poke: one center light on and time out of 30 s (punishment)
        - if no nose poke, wait for a poke with the next 10 s: 
            - if poke in the non illuminated side within 20s => reward + inactivity for 20 s
            - if no poke in the non illuminated side but poke in the illuminated side => one center light on and time out of 30 s (punishment)
            - if no poke at all => light off and inactivity for 20s
    Session of 20 trials max or if no pokes for more than 20min
    open the door for the back trip in the housing cage
    turn to next phase if 90% of correct answers in the last 20 trials.
    data collected: time of correct pokes after the delay, time of correct pokes within the delay (too early), time of incorrect pokes after the delay, time of incorrect pokes within the delay (too early), time of pokes when inactive, time of missed trials (no pokes)
    '''
    
    def __init__( self , phaseDoneCallBack, animal = None , gate = None ):
        
        '''
        self.nbNosePoke = 0
        self.animal = animal
        self.endingPhase = False
        self.phaseDoneCallBack = phaseDoneCallBack
        self.gate = gate
        '''
        logging.info( "init phase 4")
    
    def deviceListener(self, event):
        
        logging.info("PHASE 4 device listener")
        

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
        
        '''
        self.phase1_a1 = Phase1( animal = "12344" )
        self.phase1_a2 = Phase1( animal = "456" )
        '''
        self.animalManager1 = AnimalManager("091061451002")
        self.animalManager2 = AnimalManager("091061450969")
        
        self.name = name        
        self.initHardware()
        
        self.initExperiment()
        
    def initExperiment(self):
        
        self.ratGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )
        
        
        # 12344
        
        
        
        
        #input("Experiment ready - press a key.")
        
    def runLogic(self):
        
        print( self.ratGate.arduino.weight )
        
        
        
        pass
        

    def initHardware(self):
        
        
        logging.info('Init hardware.')
        
        self.ratGate = Gate( 
            COM_Servo = "COM80", 
            COM_Arduino= "COM81", 
            COM_RFID = "COM82", 
            name="rat_gate",
            weightFactor = 0.74,
            mouseAverageWeight = 60, #220, #31
            #lidarPinOrder = ( 1, 0, 3 , 2 )
            enableLIDAR = False,
            invertScale = True,
            gateMode = GateMode.RAT
             )
        
        #self.ratGate.setSpeedAndTorqueLimits(speedLimit, torqueLimit)
        
        self.waterPump = WaterPump(comPort="COM3", name="WaterPump")
        #self.fed = Fed3Manager2( comPort="COM7" , name= "Fed")
        self.fed = Fed3Manager2( comPort="COM94" , name= "Fed")
                  
        self.waterPump.addDeviceListener( self.deviceListener )  
        self.fed.addDeviceListener( self.deviceListener )  
        self.ratGate.addDeviceListener( self.deviceListener )
        
        
        logging.info('Hardware init done.')

    
    def deviceListener(self , event ):
        
        print( event )
        logging.info( "--->" + str(event) )
        
        self.animalManager1.deviceListener( event )
        self.animalManager2.deviceListener( event )
        






































if __name__ == '__main__':
    
    experiment = Experiment()
    
    MAX_NUMBER_REWARDS_PHASE1 = 80
        
    while( True ):
    
        experiment.runLogic()
        sleep( 0.05 )
    
    
    
    
    
