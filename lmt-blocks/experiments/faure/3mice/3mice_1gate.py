'''
Created on 10 mars 2023

@author: LMT_11
'''

from blocks.autogate.Parameters import *
from blocks.autogate.Gate import GateOrder, Gate, GateMode
import time


class Experiment(): # check if only 1 animal is present
    
    def __init__(self ):
                
        # input the number of animals currently in the LMT
        self.nbAnimalInLMT = int ( input("Number of animals already in LMT ?") )
        
        self.targetNumberOfAnimals = 3
        
        # init hardware
        
        self.gate1 = Gate( 
        COM_Servo = "COM85", 
        COM_Arduino= "COM86", 
        COM_RFID = "COM88", 
        name="Gate with lidar", # bottom of the cage
         weightFactor = 0.65,
        mouseAverageWeight = 25,
        lidarPinOrder = ( 0, 1, 3 , 2 ),
        gateMode = GateMode.MOUSE,
        invertScale = False
         )
    
        self.gate1.addDeviceListener( self.listener )        
        
        if self.nbAnimalInLMT < self.targetNumberOfAnimals:
            self.gate1.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B, noOrderAtEnd=True )
        else:
            self.gate1.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
        
        
    def listener( self, event ):
        
        if "Animal allowed to cross" in event.description:
            print( event )
            if self.gate1.getOrder() == GateOrder.ALLOW_SINGLE_A_TO_B:                
                self.nbAnimalInLMT+=1
                print("adding animal in LMT count")
                
            if self.gate1.getOrder() == GateOrder.ALLOW_SINGLE_B_TO_A:                
                self.nbAnimalInLMT-=1
                print("removing animal in LMT count")
                
            print( f"Number of animals in LMT : {self.nbAnimalInLMT}")
            
        if "SETORDER NO_ORDER" in event.description:
            if self.nbAnimalInLMT < self.targetNumberOfAnimals:
                self.gate1.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B, noOrderAtEnd=True )
                print( f"Not enough animals... Starting new A TO B.... Number of animals in LMT : {self.nbAnimalInLMT}")
            else:
                self.gate1.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                print( f"3 animals reached Starting new B TO A.... Number of animals in LMT : {self.nbAnimalInLMT}")
            
            #if self.gate1.getOrder() == GateOrder.ALLOW_SINGLE_A_TO_B:
                

    
    
if __name__ == '__main__':
    

    experiment = Experiment()
        
    while( True ):
        
        time.sleep( 1 )
        
        
        
        
    
    
    
    
    
    