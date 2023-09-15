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
from blocks.waterpump.WaterPump import WaterPump


if __name__ == '__main__':
    
    logFile = "gateLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".txt"
    
    print("Logfile: " , logFile )
    #logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s:%(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S : ' )    
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    logging.info('Application started.')


    gate = Gate( 
        COM_Servo = "COM80", 
        COM_Balance= "COM81", 
        #COM_RFID = "COM82", 
        name="Sugar Gate",
        weightFactor = 0.74,
        mouseAverageWeight = 32
        #enableLIDAR = False
         )
    
    gate.setRFIDControlEnabled ( False ) 
    
    
    fed = Fed3Manager( comPort="COM39" )
    
    gate2 = Gate( 
        COM_Servo = "COM85", 
        COM_Balance= "COM86", 
        #COM_RFID = "COM82", 
        name="Social Gate",
        weightFactor = 0.74,
        mouseAverageWeight = 32,
        
         )
    
    gate2.setRFIDControlEnabled ( False ) 
    fed2 = Fed3Manager( comPort="COM43" )
    
    waterPump = WaterPump(comPort="COM90", name="WaterPump")
    
    gate.close()
    gate2.close()
    
    logging.info("System ready.")
    
    
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
        
    
    
    
    
    