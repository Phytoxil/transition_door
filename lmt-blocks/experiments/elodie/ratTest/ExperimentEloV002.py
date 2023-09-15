'''
Created on 3 févr. 2023

@author: eye
'''
import logging
from random import randint
from datetime import datetime
import sys
from blocks.autogate.Gate import Gate, GateMode, GateOrder

from blocks.waterpump.WaterPump import WaterPump

from time import sleep
from blocks.FED3.Fed3Manager2 import Fed3Manager2


class AnimalManager():
    
    
    def __init__( self , rfid ):
        
        # init
        self.rfid = rfid
        self.enableRepeat = False # repeat to phase
        self.currentPhaseIndex = 0
        self.phaseList = []
        self.phaseList.append( Phase1( rfid  ) )        
        self.phaseList.append( Phase1( rfid  ) )
        self.phaseList.append( Phase1( rfid  ) )
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


class Phase1():


    '''
    2 nose pokes actifs / illuminated dedans
    sessions de 20
    reward max reached > stop the winning machine > light off incactif (et endtre chaque essais pendnt 20 secondes)
    porte ouverte pour le retour
    '''
    
    def __init__( self , rfid ): #phaseDoneCallBack, animal = None , gate = None ):
        
        self.nbNosePoke = 0
        self.rfid = rfid
        self.endingPhase = False
        #self.phaseDoneCallBack = phaseDoneCallBack
        self.gate = None
        
    
    def deviceListener(self, event):
        
        if "fed3" in event.deviceType: # test if any nose poke is performed by the animal
            if "nose poke" in event.description:
                # we had a nose poke.
                self.nbNosePoke+=1                
                logging.info( f"PHASE 1 with animal {self.rfid} / current number of poke = {self.nbNosePoke} side: {event.data}" )
        
        if self.nbNosePoke >= 20:
            self.endingPhase = True
            self.gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )
                        
        if self.endingPhase:
            if "gate" in event.deviceType:
                if "ALLOW_SINGLE_B_TO_A DONE" in event.description:
                    # animal is back.
                    logging.info( f"PHASE 1 with animal {self.rfid} ANIMAL is back to A ! ending phase...")
                    #self.phaseDoneCallBack()
                    
    def __str__(self):
        return f"PHASE 1 with animal {self.rfid}"
    
class Phase2():


    '''
    description to do
    porte ouverte pour le retour
    '''
    
    def __init__( self , phaseDoneCallBack, animal = None , gate = None ):
        
        '''
        self.nbNosePoke = 0
        self.animal = animal
        self.endingPhase = False
        self.phaseDoneCallBack = phaseDoneCallBack
        self.gate = gate
        '''
        logging.info( "init phase 2")
    
    def deviceListener(self, event):
        
        logging.info("PAHSE 2 device listener")
        

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
        self.fed = Fed3Manager2( comPort="COM7" , name= "Fed")
                  
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
        
        
    while( True ):
    
        experiment.runLogic()
        sleep( 0.05 )
    
    
    
    
    
