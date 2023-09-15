'''
Created on 16 mars 2022

@author: Fab
'''

from time import sleep

from datetime import datetime
import logging
import sys
from blocks.autogate.Gate import Gate, GateOrder, GateMode
from blocks.FED3.Fed3Manager import Fed3Manager
from experiments.api.Chronometer import Chronometer
from panel.tests.io.test_location import location
from blocks.LMTEvent.LMTEventSender import LMTEventSender
from mail.Mail import LMTMail


if __name__ == '__main__':
    
    logFile = "gateLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"
    
    print("Logfile: " , logFile )
    #logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s:%(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S : ' )    
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    logging.info('Application started.')
    LMTEventSender("Starting GATE CODE")

    averageWeight = 25

    gateRobin = Gate( 
        COM_Servo = "COM85", 
        COM_Arduino= "COM86", 
        COM_RFID = "COM88", 
        name="LMT Block RobinGate",
        weightFactor = 0.73,
        mouseAverageWeight = 25,
        lidarPinOrder = ( 0, 1, 3 , 2 ),
        gateMode = GateMode.MOUSE
         )
    
    
    gatePhi = Gate( 
        COM_Servo = "COM80", 
        COM_Arduino= "COM81", 
        COM_RFID = "COM83", 
        name="LMT Block PhiGate",
        weightFactor = 0.73,
        mouseAverageWeight = 25,
        gateMode = GateMode.MOUSE,
        enableLIDAR = False )

    
    logging.info("System ready.")
    
    
    '''
    gateRobin.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )
    gatePhi.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )
    '''
    
    '''
    input("Hit enter to close !")
    gateRobin.open()
    gatePhi.open()
    input("Hit enter to close !")
    '''
    '''
    input("Hit enter to close !")
    gateRobin.close()
    gatePhi.close()
    input("Hit enter to start !")
    quit()
    gateRobin.open()
    gatePhi.open()
    '''
    
   # gateRobin.setRFIDControlEnabled( True )
    #gatePhi.setRFIDControlEnabled( True )
    #LMTEventSender("GATE READY")
   # input("Hit enter to close !")
    #LMTEventSender("GATE RUNNING")
   # gateRobin.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B )
   # gatePhi.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )


    '''
    gateRobin.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B )
    gatePhi.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B )
    '''


    gateRobin.open()

    gatePhi.open()


    '''
    GateOrder.ALLOW_SINGLE_A_TO_B
    
    GateOrder.ALLOW_SINGLE_B_TO_A
    '''

    '''
    location
       + souris[]
       
    '''
    
    
    

    
    def listener( deviceEvent ):
        #print("Coucou")
        logging.info( deviceEvent )
        if "[LMT Block RobinGate][004] WAIT SINGLE_ANIMAL" in deviceEvent.description:
            print("HELLO HELLO HELLO HELLO HELLO HELLO HELLO HELLO HELLO HELLO ")
    
        LMTEventSender( deviceEvent.description )
    
        # j'ai telle porte qui vient de donner à mon cote B. location = salon
        '''
        salon.append( ma souris qui a la rfid )
        
        if not le salon empety :
            gateRobin > gatePhi.setOrder( GateOrder.EMPTY_IN_A )
            gatePhi >
        '''
            
        #print("description: " + deviceEvent.description  )
        
    
    '''
    lmt = LMTEventSender("C'est bon la souris est bien rose")    
    m = LMTMail( ["robin.justo22@gmail.com"], "coucou", "coucou encore" )
    '''
    
    
    gatePhi.addDeviceListener(listener)
    gateRobin.addDeviceListener(listener)
    
    
    chrono = Chronometer() 
    chrono.resetChrono("experiment")
    
    while ( True ):
                
        delay = chrono.getChronoS("experiment")
        if delay > 60*60:
            logging.info("Experience terminated... timeout.")
            quit()
        
        
        sleep( 0.05 )
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    