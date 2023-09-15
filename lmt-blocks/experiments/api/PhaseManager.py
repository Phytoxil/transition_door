'''
Created on 22 juin 2022

@author: Fab
'''
from experiments.api.Phase import Phase
import logging

class PhaseManager(object):

    def __init__(self ):
    
        self._phaseList = [ ]
        self._currentPhase = None
        self._phaseIndex = 0
        
    def addPhase(self , phase : Phase ):
        
        self._phaseList.append( phase )
        
    def start(self):
        self._switchToPhaseIndex( 0 )        
        
    def _switchToPhaseIndex(self , index ):
        self._currentPhase.finish()
        self._currentPhase = self._phaseList[ index ]
        self._phaseIndex = index
        logging.info("[Phase Manager] Switch to phase : " + str( self._currentPhase ))
        self._currentPhase.init()
      
    def getPhaseEventFromDevice(self, device ):
        return self._currentPhase.getEventsFromDevice( device )
        
    def callLoopPhase(self ):
        self.getCurrentPhase().loop()        
            
    def switchToLastPhase(self):
        index = len( self._phaseList ) -1 
        self._switchToPhaseIndex( index )
        
    def switchToNextPhase(self):
        
        index = self._phaseIndex+1
        self._switchToPhaseIndex( index )
        
    def getPhaseList(self):
        return self._phaseList
    
    def getCurrentPhase(self):
        return self._currentPhase