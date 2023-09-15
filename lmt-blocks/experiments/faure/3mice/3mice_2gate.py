'''
Created on 10 mars 2023

@author: LMT_11
'''

from blocks.autogate.Parameters import *
from blocks.autogate.Gate import GateOrder, Gate, GateMode
import time
import threading

from enum import Enum

class ExperimentState(Enum):
    LET_ANIMALS_GET_IN_SETUP = 1  # animals can enter the setup
    LET_ANIMALS_LEAVE_SETUP = 2  # animals can leave the setup
    CLOSE_ALL = 3 # the target is to empty all gates in A zones.


class Experiment():
    
    def __init__(self ):
                
        # input the number of animals currently in the LMT
        
        self.targetNumberOfAnimals = 3
        
        # init hardware
        
        self.gate1 = Gate( 
        COM_Servo = "COM85", 
        COM_Arduino= "COM86", 
        COM_RFID = "COM88", 
        name="Gate with lidar",
         weightFactor = 0.65,
        mouseAverageWeight = 25,
        lidarPinOrder = ( 0, 1, 3 , 2 ),
        gateMode = GateMode.MOUSE,
        invertScale = False
         )
        
        self.gate2 = Gate( 
        COM_Servo = "COM80", 
        COM_Arduino= "COM81", 
        COM_RFID = "COM83", 
        name="Gate without lidar",
        weightFactor = 0.65,
        mouseAverageWeight = 25,        
        gateMode = GateMode.MOUSE,
        enableLIDAR=False        
         )
    
        self.gateList = []
        self.gateList.append( self.gate1 )
        self.gateList.append( self.gate2 )
        
        self.gate1.addDeviceListener( self.listener )
        self.gate2.addDeviceListener( self.listener )        
        
        input("Ready to close all ? (enter to close all)")
        self.gate1.close()
        self.gate2.close()
        
        self.nbAnimalInLMT = int ( input("Number of animals already in LMT ?") )
        self.gate1.tare()
        self.gate2.tare()
        
        
        
        self.logicThread = threading.Thread( target=self.logic , name = f"Thread logic experiment")            
        self.logicThread.start()
        

        if self.nbAnimalInLMT < self.targetNumberOfAnimals:
            self.gate1.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B, noOrderAtEnd=True )
            self.gate2.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B, noOrderAtEnd=True )
        else:
            self.gate1.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
            self.gate2.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )

        
    def listener( self, event ):
        
        adding = None
        if "Animal allowed to cross" in event.description:
            print( event )
            if event.deviceObject.getOrder() == GateOrder.ALLOW_SINGLE_A_TO_B:                
                self.nbAnimalInLMT+=1
                adding=True
                print("adding animal in LMT count")
                
            if event.deviceObject.getOrder() == GateOrder.ALLOW_SINGLE_B_TO_A:                
                self.nbAnimalInLMT-=1
                adding=False
                print("removing animal in LMT count")
                
            print( f"Number of animals in LMT : {self.nbAnimalInLMT}")
            
            if self.nbAnimalInLMT == self.targetNumberOfAnimals:
                
                print( "Correct number of animals reached")
                
                if adding: # animal gets in and right number is reached
                    print( "order from animal gets in and right number is reached")
                    event.deviceObject.setOrder( GateOrder.EMPTY_IN_B, noOrderAtEnd=True )
                    for gate in self.gateList: # reverse order of other gates
                        if event.deviceObject != gate:
                            gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A , noOrderAtEnd=True )
            
                if not adding: # animal gets out and right number is reached
                    print( "order from animal gets OUT and right number is reached")
                    event.deviceObject.setOrder( GateOrder.EMPTY_IN_A, noOrderAtEnd=True )
                    for gate in self.gateList: # reverse order of other gates
                        if event.deviceObject != gate:
                            gate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )

            if self.nbAnimalInLMT == self.targetNumberOfAnimals-1:
                if adding == False:
                    # we now have 2 animals instead of 3
                    for gate in self.gateList: # reverse order of other gates
                        if event.deviceObject != gate:
                            gate.setOrder( GateOrder.EMPTY_IN_B, noOrderAtEnd=True )
                            
                    
            
            '''
            if self.nbAnimalInLMT == 3:
                for gate in self.gateList: # reverse order of other gates
                    if event.deviceObject != gate:
                        gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A , noOrderAtEnd=True )
            '''
        
        
        if "SETORDER NO_ORDER" in event.description:
            if self.nbAnimalInLMT < self.targetNumberOfAnimals:
                print( "order from SETORDER NO_ORDER SECTION")
                event.deviceObject.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B, noOrderAtEnd=True )
            else:
                event.deviceObject.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
        
                                                
        '''
        
        if "SETORDER NO_ORDER" in event.description:
            if self.nbAnimalInLMT < self.targetNumberOfAnimals:
                if self.gate1.getOrder() != GateOrder.NO_ORDER:
                    self.gate1.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B, noOrderAtEnd=True )
                
                if self.gate2.getOrder() != GateOrder.NO_ORDER:
                    self.gate2.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B, noOrderAtEnd=True )
                
                print( f"Not enough animals... Starting new A TO B.... Number of animals in LMT : {self.nbAnimalInLMT}")
            else:
                if self.gate1.getOrder() != GateOrder.NO_ORDER:
                    self.gate1.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                if self.gate2.getOrder() != GateOrder.NO_ORDER:
                    self.gate2.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                print( f"3 animals reached Starting new B TO A.... Number of animals in LMT : {self.nbAnimalInLMT}")
        '''
            
    def logic(self):
        
        # init
        
        
        while True:
            
            print(f"--Nb Animals :{self.nbAnimalInLMT} / {self.targetNumberOfAnimals} g1 Order: {self.gate1.getOrder()} g2 Order : {self.gate2.getOrder()} ")
            try:
                gate = self.gate1
                print(f"logic1 : {gate.logicCursor} : {gate.logicList[gate.logicCursor]} " )
                gate = self.gate2
                print(f"logic2 : {gate.logicCursor} : {gate.logicList[gate.logicCursor]} " )
            except:
                pass            
            time.sleep( 1 )
        
    
    
if __name__ == '__main__':
    

    experiment = Experiment()
        
    while( True ):
        
        time.sleep( 1 )
        
        
        
        
    
    
    
    
    
    