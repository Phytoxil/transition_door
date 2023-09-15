'''
Created on 23 mars 2023

@author: eye
'''
from blocks.FED3.Fed3Manager2 import Fed3Manager2
from blocks.waterpump.WaterPump import WaterPump
import time
from datetime import datetime
import logging
import sys

class Experiment(object):
    
    def __init__( self ):
        
        self.waterPump = WaterPump(comPort="COM6", name="WaterPump")    
        self.fed = Fed3Manager2( comPort="COM94" , name= "Fed")
        
        self.fed.addDeviceListener( self.listener )
        self.nbPokeLeft = 0
        self.nbPokeRight = 0
        
    def listener(self , event ):
        
        if "nose poke" in event.description:
            
            self.waterPump.pump( 255, 30 )
            
            if "right" in event.data:
                logging.info("nose poke right")
                self.nbPokeRight+=1
            if "left" in event.data:
                self.nbPokeLeft+=1
                logging.info("nose poke left")
            
        

if __name__ == '__main__':
    
    logFile = "habituation nose poke log - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"    
    print("Logfile: " , logFile )    
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))        
    logging.info('Application started')


    experiment = Experiment()
    
    experiment.waterPump.pump( 255, 30 )
    
    while( True ):
    
        print( datetime.now() , experiment.nbPokeLeft , experiment.nbPokeRight)
        time.sleep(5)
    
        