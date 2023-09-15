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
        COM_RFID = "COM82", 
        name="GATE TEST1",
        weightFactor = 0.62,
        mouseAverageWeight = 32
         )    
    gate1.setLidarPinOrder( ( 0,1,2,3 ) )
    gate1.setRFIDControlEnabled ( True ) 
    

    gate2 = Gate( 
        COM_Servo = "COM85", 
        COM_Arduino= "COM86", 
        COM_RFID = "COM87", 
        name="GATE TEST2",
        weightFactor = 0.63,
        mouseAverageWeight = averageWeight
        #enableLIDAR= False        
         )
    gate2.setLidarPinOrder( ( 3,2,1,0 ) )
    gate2.setRFIDControlEnabled ( True ) 
    

    fed1 = Fed3Manager( comPort="COM84" )
    fed2 = Fed3Manager( comPort="COM89" )
    
    '''
    print("Order list:")
    print("a: open gates")
    print("enter: start protocol")
    
    order = input("Order: ")
    
    
    if "a"  in order:
        gate1.open()
        gate2.open()
        logging.info("open gates and Quit.")
        quit()
    '''
    
    
    
    '''
    fed1.click()
    fed2.click()
    sleep( 1 )
    fed1.feed()
    fed2.feed()
    '''

    
    gate1.close()
    gate2.close()
    
    rfids  = [ "001038125005" , "001038125045","001038124994","001038125001","001038125023","001038124996", "001038125044" ]
    '''
    for rfid in rfids:
    
        gate1.addForbiddenRFID( rfid )
        gate2.addForbiddenRFID( rfid )
    '''
    
    
    
    #quit()

    
    logging.info("System ready.")
    
    gate1.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )
    gate2.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )
    
    
    
    # protocol loguc
    while ( True ):
                
        # manage fed 1
        fedRead = fed1.read()        
        if fedRead != None:
            logging.info( "[FED1]:" + fedRead )
            
            if "In" in fedRead:
                logging.info("Nose poke TEST1")
                fed1.click()
                sleep(0.1)
                fed1.feed()
        
        # manage fed 2
        fedRead = fed2.read()                
        if fedRead != None:
            if "In" in fedRead:
                logging.info( "[FED2]:" + fedRead )
                logging.info("Nose poke TEST2")
                fed2.click()
                sleep(0.1)
                fed2.feed()
        
        sleep( 0.05 )
        
    
    
    
    
    