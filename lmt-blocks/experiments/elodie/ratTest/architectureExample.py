'''
Created on 13 mars 2023

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

'''


    critere = xa * a + xb * b + xc * c

    lineiare = log( mayo ) + exp( fraises ) + 4 concombre

    


    1 bloc de test
    x animaux
    pas de sauvegarde d'etat
    pas de phase
    ---- tourner en live > test possibles
    
    2 ème phase    
    ---- > enrichissez
    
    phases generalisée
    ----
    
    phases generalisée + heritage
    ----
        
    sauvegarde
    ---- > nirvana

'''

'''
    fed1
    fed2
    w1
    w2
    G1
    G2
    animal > sessionCurrent
    
    gateListener
      G1 > SessionZ1 ( fed1, w1 ) > animal.sessionCurrent
        
        
        sessionEnded > G1 > ALLOW_B_TO_A >
        30 minutes >  
        
    
    gateListener > ALLOW_B_TO_A > animal > stock result session > animal.sessionCurrent = None
        
        - 



'''




def deviceListener ( event ):
    
    print( f"event received : {event}")

    if "Animal allowed to cross" in event.description:
        print( event.data ) # RFID
        print( event.description.split(":")[-1] ) # RFID
        rfid = event.description.split(":")[-1]
        
        #if "[008] CHECK_ANIMAL_ID" in event.deviceObject.getLogic():
             
        
        '''
        if ( event.deviceObject.getOrder( )  == GateOrder.ALLOW_SINGLE_A_TO_B ):
            print( f'animal vers B avec rfid {rfid}')
            return
        if ( event.deviceObject.getOrder( )  == GateOrder.ALLOW_SINGLE_B_TO_A ):
            print( f'animal vers A avec rfid {rfid}')
            return
        print("ERROR")
        quit()
        '''
        
    

def deviceListerWater( event ):
    pass    

if __name__ == '__main__':
    
    
    ratGate = Gate( 
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
        
        
    '''
    waterPump = WaterPump(comPort="COM3", name="WaterPump")
    fed = Fed3Manager2( comPort="COM7" , name= "Fed")
    '''
                  
    #waterPump.addDeviceListener( deviceListener )  
    #fed.addDeviceListener( deviceListener )  
    ratGate.addDeviceListener( deviceListener )
    #waterPump.addDeviceListener( deviceListerWater )
        
    input("Attente enter")
    
    ratGate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B , noOrderAtEnd = True )
    
    '''
    while( True ):
        
        print( ratGate.getLogic( ) )
        sleep( 0.01 )
    '''
        
        
        
    
        
        
        
        
        