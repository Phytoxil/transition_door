'''
Created on 3 mars 2023

@author: eye
'''
from datetime import datetime, timedelta
import time
import logging
from numba.core.types import none
from random import random

sides = {
    'left': {
        'controlLight': 'RGBWdef_R000_G000_B000_W100_SideL',
        'sideToChoose': 'leftIn'
    },
    'right': {
        'controlLight': 'RGBWdef_R000_G000_B000_W100_SideR',
        'sideToChoose': 'rightIn'
    }
}


def TrainingTrial():
    '''
    This is the definition of the training trial
    2 nose pokes active / light on inside both holes until nose poke
    when poke, reward delivered
    trial stopped
    '''
    
    def __init__( self , rfid ): #phaseDoneCallBack, animal = None , gate = None ):
        
        self.sideNosePoke = None
        self.checkNosePoke = False
        self.rfid = rfid
        self.trialCompleted = False
        self.gate = None 
        
    def deviceListener(self, event): #event == fedRead = self.fed.read()
        self.startTimeTrial = datetime.now()
        #initiate the trial by turning on lights in both holes
        self.fed.controlLight('RGBWdef_R100_G000_B000_W000_Sideb') #how to turn both lights on?
        time.sleep(0.5)
        
        if "fed3" in event.deviceType: # test if any nose poke is performed by the animal
            if "nose poke" in event.description:
                # we had a nose poke.
                self.checkNosePoke = True
                #turn off the light
                self.fed.lightoff()
                
                self.sideNosePoke = event.data
                #give the reward: sucrose pump
                #check if reward given
                
                #record that one trial has been done
                logging.info( f"Training trial with animal {self.rfid} / poke side: {event.data}" )
        
        time.sleep(0.5)
        self.trialCompleted = True
                    
    def __str__(self):
        return f"Habituation trial with animal {self.rfid}"


def simpleLearningTrial():
    '''
    This is the definition of the trial for simple poke in an illuminated hole
    
    random side chosen by the system (not more than 3 in a row in the same side)
    the hole at this side gets illuminated for 20s: 
    - if poke in the illuminated side within 20s => reward + inactivity for 10 s
    - if no poke in the illuminated side but poke in the non illuminated side => one center light on and time out of 40 s (punishment)
    - if no poke at all => light off and inactivity for 20s
    '''
    
    def __init__( self , rfid, illuminationDuration, inactivityDurationAfterSuccess, inactivityDurationAfterError ):
        self.randomSide = random.choice(['left', 'right'])
        self.illuminatedHole = None
        self.illuminationDuration = illuminationDuration #in seconds
        self.inactivityDurationAfterSuccess = inactivityDurationAfterSuccess #in seconds
        self.inactivityDurationAfterError = inactivityDurationAfterError #in seconds
        self.gate = None
        self.trialCompleted = False
        self.trialSuccess = False
        self.endTimeTrial = None
    
    
    def deviceListener(self, event): #event == fedRead = self.fed.read()
        self.startTimeTrial = datetime.now()
        #initiate the trial by turning on light a random hole
        self.illuminatedHole = self.randomSide
        self.fed.light(direction = self.randomSide )
        time.sleep(0.5)
        
        while datetime.now() <= self.startTimeTrial + timedelta( seconds = self.illuminationDuration ):
            if 'nose poke' in event.description:
                self.fed.lightoff()
                time.sleep(0.5)
                if sides[self.randomSide]['sideToChoose'] in event.data:
                    self.logging.info( '[FED] trial for simple learning successful' + event.description )
                    self.trialCompleted = True
                    self.trialSuccess = True
                    self.endTimeTrial = datetime.now()
                    time.sleep( self.inactivityDurationAfterSuccess)
                    

                else:
                    self.fed.controlLight('RGBWdef_R100_G000_B000_W000_Sideb') #light in the middle as punishment
                    time.sleep(self.inactivityDurationAfterError)
                    self.fed.lightoff()
                    self.logging.info('[FED] trial for simple learning error' + event.description)
                    self.trialCompleted = True
                    
                
                logging.info( f"Simple learning trial with animal {self.rfid} / poke side: {event.data}" )
        
        time.sleep(0.5)
        self.endingTrial = True
                    
    def __str__(self):
        return f"Simple learning trial with animal {self.rfid}"
