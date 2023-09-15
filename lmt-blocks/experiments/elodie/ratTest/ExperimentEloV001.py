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

class Phase1(object):


    '''
    2 nose pokes actifs / illuminated dedans
    sessions de 20
    reward max reached > stop the winning machine > light off incactif (et endtre chaque essais pendnt 20 secondes)
    porte ouverte pour le retour
    '''
    
    def __init__( self , animal = None ):
        
        self.nbNosePoke = 0
        self.animal = animal
        
    
    def deviceListener(self, event):
        
        if "fed3" in event.deviceType:
            if "nose poke" in event.description:
                # we had a nose poke.
                self.nbNosePoke+=1                
                logging.info( f"PHASE 1 with animal {self.animal} / current number of poke = {self.nbNosePoke} side: {event.data}" )
        
        
    
        

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
        
        
        self.phase1_a1 = Phase1( animal = "12344" )
        self.phase1_a2 = Phase1( animal = "456" )
        
        
        self.name = name        
        self.initHardware()
        
        self.initExperiment()
        
    def initExperiment(self):
        
        self.ratGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )
        
        
        # 12344
        
        
        
        
        #input("Experiment ready - press a key.")
        
    def runLogic(self):
        
        pass
        

    def initHardware(self):
        
        
        logging.info('Init hardware.')
        
        self.ratGate = Gate( 
            COM_Servo = "COM80", 
            COM_Arduino= "COM81", 
            COM_RFID = "COM82", 
            name="rat_gate",
            weightFactor = 0.74,
            mouseAverageWeight = 220, #31
            #lidarPinOrder = ( 1, 0, 3 , 2 )
            enableLIDAR = False,
            invertScale = True,
            gateMode = GateMode.RAT
             )
        
        self.waterPump = WaterPump(comPort="COM3", name="WaterPump")
        self.fed = Fed3Manager2( comPort="COM7" , name= "Fed")
                  
        self.waterPump.addDeviceListener( self.deviceListener )  
        self.fed.addDeviceListener( self.deviceListener )  
        self.ratGate.addDeviceListener( self.deviceListener )
        
        
        logging.info('Hardware init done.')

    
    def deviceListener(self , event ):
        
        print( event )
        logging.info( "--->" + str(event) )
        
        self.phase1_a1.deviceListener( event )







































if __name__ == '__main__':
    
    experiment = Experiment()
        
        
    while( True ):
    
        experiment.runLogic()
        sleep( 0.05 )
    
    
    
    
    
