'''
Created on 16 mars 2022

@author: Fab
'''

from time import sleep

from datetime import datetime
import logging
import sys
from blocks.autogate.Gate import Gate, GateOrder


from blocks.autogate.dxl_control.MotorManager import MotorManager
import threading
from blocks.autogate.Parameters import OPENED_DOOR_POSITION_MOUSE,\
    CLOSED_DOOR_POSITION_MOUSE, DEFAULT_TORQUE_AND_SPEED_LIMIT_MOUSE
from blocks.autogate.Door import Door
from blocks.autogate.dxl_control.Ax12Motor import Ax12Motor


if __name__ == '__main__':
    
    logFile = "gateLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".txt"
    
    print("Logfile: " , logFile )
    #logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s:%(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S : ' )    
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    logging.info('Application started.')

    # INIT SOCIAL PRESENTATION MODULE
    COM_Servo = "COM68"

    try:
        motorManager = MotorManager( COM_Servo )
    except:
        print("Quit: Can't connect motors using port: " , COM_Servo )
        quit()
    
    lock = threading.Lock()
    door = Door( Ax12Motor(1, motorManager) , "A" , lock , False )

    door.setLimits( OPENED_DOOR_POSITION_MOUSE-20, CLOSED_DOOR_POSITION_MOUSE )
    door.setSpeedAndTorqueLimits(DEFAULT_TORQUE_AND_SPEED_LIMIT_MOUSE+100, DEFAULT_TORQUE_AND_SPEED_LIMIT_MOUSE+100)
        
    for i in range(1000):
        door.open()
        sleep(5)
        door.close()
        sleep(5)

    '''
    gate1 = Gate( 
        COM_Servo = "COM68",
        name="GATE SOCIAL PRESENTATION",
        weightFactor = 0.62,
        mouseAverageWeight = 32
         )    
        
    gate1.close()
    '''

    logging.info("System ready.")
    
    
    
    '''
    # protocol logic
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
        
    '''
    
    
    
    