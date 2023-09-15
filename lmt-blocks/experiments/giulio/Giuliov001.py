'''
Created on 16 mars 2022

@author: Fab
'''

from time import sleep

from datetime import datetime
import logging
import sys
from blocks.autogate.Gate import Gate, GateOrder
from blocks.FED3.Fed3Manager import Fed3Manager


if __name__ == '__main__':
    
    logFile = "gateLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".txt"
    
    print("Logfile: " , logFile )
    #logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s:%(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S : ' )    
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    logging.info('Application started.')


    averageWeight = 32

    gate1 = Gate( 
        COM_Servo = "COM80", 
        COM_Arduino= "COM81", 
        COM_RFID = "COM33", 
        name="GATE SOCIAL TEST",
        weightFactor = 0.75,
        mouseAverageWeight = 32,
        lidarPinOrder = ( 1, 0, 2 , 3 ),
        
        
         )    

    gate1.setRFIDControlEnabled( False )

    
    
    gate1.close()
    
    
    logging.info("System ready.")
    
    gate1.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )
    
    
    
    # protocol loguc
    while ( True ):
                

        print("running...")        
        sleep( 0.5 )
        
    
    
    
    
    