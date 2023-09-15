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
from blocks.lever.Lever import Lever

class Experiment(object):
    
    def __init__( self ):
        
        self.waterPump = WaterPump(comPort="COM6", name="WaterPump")    
        self.leftLever = Lever(comPort="COM4", name="Lever left")
        self.rightLever = Lever(comPort="COM8", name="Lever right")    
        
        self.leftLever.addDeviceListener( self.listener )
        self.rightLever.addDeviceListener( self.listener )
                
        self.nbLeverLeft = 0
        self.nbLeverRight = 0
        
    def listener(self , event ):
        
        #print( event.description )        
        
        if "press" in event.description:
            
            self.waterPump.pump( 255, 30 )
            
            if "right" in event.deviceObject.name:
                logging.info("lever right")
                self.nbLeverRight+=1
                                
            if "left" in event.deviceObject.name:
                logging.info("lever left")
                self.nbLeverLeft+=1
        
        if "release" in event.description:
            
            if "right" in event.deviceObject.name:
                logging.info("lever right release")
                self.nbLeverRight+=1
                                
            if "left" in event.deviceObject.name:
                logging.info("lever left release")
                self.nbLeverLeft+=1        
        
            
        

if __name__ == '__main__':
    
    logFile = "habituation lever log - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"    
    print("Logfile: " , logFile )    
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))        
    logging.info('Application started')


    experiment = Experiment()
    
    #experiment.waterPump.pump( 255, 30 )
    
    while( True ):
    
        print( datetime.now() , experiment.nbLeverLeft , experiment.nbLeverRight)
        time.sleep(5)
    
        