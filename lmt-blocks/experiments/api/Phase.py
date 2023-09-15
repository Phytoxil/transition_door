'''
Created on 22 juin 2022

@author: Fab
'''
from experiments.api.Chronometer import Chronometer
import logging


class Phase(object):
    '''
    Experiment phase
    '''

    def __init__(self, name , initFunction = None, loopFunction = None, finishFunction = None ):
        
        self.name = name
        self.chrono = Chronometer()
        self.initFunction = initFunction
        self.loopFunction = loopFunction
        self.finishFunction = finishFunction
        self.eventList = []
        self.data = {} # user data
        
    def getEventsFromDevice(self , device ):
                
        returnList = []
        for event in self.eventList:
            if event.deviceObject == device:
                returnList.append( event )
        return returnList
        
    def start(self):
        self.chrono.resetChrono("phase")
        self.init()
    
    def log(self, log ):
        logging.info("[Phase:"+self.name+"]" + log )
    
    def setInitCallBack(self , initFunction ):
        self.initFunction = initFunction
        
    def setLoopCallBack(self , loopFunction ):
        self.loopFunction = loopFunction
        
    def setFinishCallBack(self , finishFunction ):
        self.finishFunction = finishFunction
        
    def init(self):
        if self.initFunction != None:
            self.log("[init]")
            self.initFunction()
            
    def loop(self):
        if self.loopFunction != None:
            self.loopFunction()
            
    def finish(self):
        if self.finishFunction != None:
            self.log("[finish]")
            self.finishFunction()

        
        
        