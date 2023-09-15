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

from panel.tests.io.test_location import location
from blocks.LMTEvent.LMTEventSender import LMTEventSender
from mail.Mail import LMTMail
import os
from socket import *
from lxml import etree
import traceback
import sys
import xml.etree.ElementTree as ET
import math

from datetime import datetime

class Chronometer(object):
    
    def __init__(self ):
        
        self.chrono = {}

    def getChronoS(self, chronoName ):
        if chronoName not in self.chrono:
            self.resetChrono( chronoName )        
        return abs(datetime.now()-self.chrono[chronoName]).seconds

    def getChronoDHMS(self, chronoName ):
        if chronoName not in self.chrono:
            self.resetChrono( chronoName )        
        return abs(datetime.now()-self.chrono[chronoName])

    def resetChrono(self, chronoName ):
        self.chrono[chronoName] = datetime.now()
        

class ROI(object):
    
    
    def __init__(self , x , y , ray ):
        # define a circle ROI
        self.x = x
        self.y = y
        self.ray = ray
        
    def isIn(self , x, y ):
        # check if the point is within the ROI
        
        if math.dist( [ self.x , self.y ], [ x, y ]) < self.ray:
            return True
        return False        

class RGate(object):
    
    
    
    def __init__(self , gate , roiLeft, roiRight ):
        
        self.gate = gate
        self.roiLeft = roiLeft
        self.roiRight = roiRight
        self.excludedRFID = []
        # init gate extra parameters
        gate.setRFIDControlEnabled( True )
        self.chrono = Chronometer()
        self.orderChronoTimeOut = "orderChronoTimeOut"
        
        
    def performOpenLogic( self , animalPositionList ):
        
        for detection in animalPositionList:
            
            if self.roiLeft.isIn( float(detection["x"]) , float(detection["y"]) ):
                
                logging.info( self.gate.name + " REQUEST ROI LEFT")
                if self.gate.getOrder() == GateOrder.NO_ORDER:
                    self.chrono.resetChrono( self.orderChronoTimeOut )
                    self.gate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )
                    
                
            if self.roiRight.isIn( float(detection["x"]) , float(detection["y"]) ):
                
                logging.info( self.gate.name + " REQUEST ROI R")
                if self.gate.getOrder() == GateOrder.NO_ORDER:
                    self.chrono.resetChrono( self.orderChronoTimeOut )
                    self.gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A , noOrderAtEnd=True )
    
                    
    def checkTimeOut(self):
        
        time = self.chrono.getChronoS( self.orderChronoTimeOut )
        
        if time > 10:
            
            logic = self.gate.getLogic()
            #print("****************** logic found: " , logic )
            
            if logic != None :
                if "WAIT SINGLE_ANIMAL" in logic:
                    
                    if self.gate.getOrder() == GateOrder.ALLOW_SINGLE_A_TO_B:
                        self.gate.setOrder( GateOrder.EMPTY_IN_A , noOrderAtEnd = True )
                                                    
                    if self.gate.getOrder() == GateOrder.ALLOW_SINGLE_B_TO_A:
                        self.gate.setOrder( GateOrder.EMPTY_IN_B , noOrderAtEnd = True )
 
        

    def addExcludedRFID(self , rfid ):
        if rfid not in self.excludedRFID:
            self.excludedRFID.append( rfid )
            self.gate.addForbiddenRFID( rfid )
        
    def removeExcludedRFID(self , rfid ):
        if rfid in self.excludedRFID:
            self.excludedRFID.remove( rfid )
            self.gate.removeForbiddenRFID( rfid )        

class Experiment(object):

    def __init__(self ):
    
        logFile = "log/gateLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"
        
        print("Logfile: " , logFile )
        os.makedirs(os.path.dirname(logFile), exist_ok=True)    
        logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        
        logging.info('Application started.')
        LMTEventSender("Starting GATE CODE")
    
        mouseAverageWeight = 25
    
        gate2 = Gate( 
            COM_Servo = "COM85", 
            COM_Arduino= "COM86", 
            COM_RFID = "COM88", 
            name="Gate 2", # bottom of the cage
            weightFactor = 0.65,
            mouseAverageWeight = mouseAverageWeight,
            lidarPinOrder = ( 0, 1, 3 , 2 ),
            gateMode = GateMode.MOUSE
             )
        
        
        gate1 = Gate( 
            COM_Servo = "COM80", 
            COM_Arduino= "COM81", 
            COM_RFID = "COM83", 
            name="Gate 1", # top of the cage
            weightFactor = 0.69,
            mouseAverageWeight = mouseAverageWeight,
            gateMode = GateMode.MOUSE,
            enableLIDAR = False )
    
        
        
        logging.info("System ready.")
    
        # doors (not gate!) A on left.
        
        self.chrono = Chronometer() 
        self.chrono.resetChrono("experiment")
        
        gate1.addDeviceListener(self.listener)
        gate2.addDeviceListener(self.listener)
        
        gate1.close()
        gate2.close()
        
        # const -----------------------
        
        self.TIMEOUT_WHOLE_EXPERIMENT = 60*60 # in seconds
        
        # ROIs
        
        roiALeft = ROI( 415,137,25)
        roiARight = ROI( 610,137,25)
        
        roiBLeft = ROI( 415,286,25)
        roiBRight = ROI( 610,286,25)
        
        # RGATES
        
        self.Rgate1 = RGate( gate1 , roiALeft , roiARight )
        self.Rgate2 = RGate( gate2 , roiBLeft , roiBRight )
                
        # start LMT data client to grab trajectories live.
        
        serverName = 'localhost'
        serverPort = 55044
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((serverName, serverPort))
        print( "client connected to grab LMT data")
    
    def stop(self):
        self.clientSocket.close()
        quit()
    
    def listener( self, deviceEvent ):
        
        
        logging.info( "*****" + str( deviceEvent ) )
        
        #logging.info( "TEST")
        
        if "allowed" in deviceEvent.description:
            print("################################################")
            print("ALLOWED DETECTED")
            logging.info("ALLOWED DETECTED" )
            LMTEventSender( deviceEvent.description )
            
            # [RFID CHECK][Gate A] Animal allowed to cross: 001039048287
            rfid = deviceEvent.description.split(" ")[-1]
            rfid = rfid.strip()
            logging.info("RFID considered: " + rfid )
            
            if "[Gate 1]" in deviceEvent.description:
                print("################################################")
                
                if self.Rgate1.gate.getOrder() == GateOrder.ALLOW_SINGLE_A_TO_B:
                    self.Rgate1.addExcludedRFID( rfid )
                    self.Rgate2.removeExcludedRFID( rfid )
                    LMTEventSender( f"{self.Rgate1.gate.getOrder()}Gate 1 : {rfid}" )
                    print("################################################")
                    print(self.Rgate1.excludedRFID)
                    print(self.Rgate2.excludedRFID)
                
                if self.Rgate1.gate.getOrder() == GateOrder.ALLOW_SINGLE_B_TO_A:
                    self.Rgate1.removeExcludedRFID( rfid )
                    self.Rgate2.removeExcludedRFID( rfid )
                    LMTEventSender( f"{self.Rgate1.gate.getOrder()}Gate 1 : {rfid}" )
                    print("################################################")
                    print(self.Rgate1.excludedRFID)
                    print(self.Rgate2.excludedRFID)

                
            if "[Gate 2]" in deviceEvent.description:
                print("################################################")
                if self.Rgate2.gate.getOrder() == GateOrder.ALLOW_SINGLE_A_TO_B:
                    self.Rgate2.addExcludedRFID( rfid )
                    self.Rgate1.removeExcludedRFID( rfid )
                    LMTEventSender( f"{self.Rgate2.gate.getOrder()}Gate 2 : {rfid}" )
                    print("################################################")
                    print(self.Rgate1.excludedRFID)
                    print(self.Rgate2.excludedRFID)

                    
                if self.Rgate2.gate.getOrder() == GateOrder.ALLOW_SINGLE_B_TO_A:
                    self.Rgate1.removeExcludedRFID( rfid )
                    self.Rgate2.removeExcludedRFID( rfid )
                    LMTEventSender( f"{self.Rgate2.gate.getOrder()}Gate 2 : {rfid}" )
                    print("################################################")
                    print(self.Rgate1.excludedRFID)
                    print(self.Rgate2.excludedRFID)

        
        
        #LMTEventSender( deviceEvent.description )
    
            
        print("description: " + deviceEvent.description  )
        
    def checkEndExperiment(self):
    
        delay = self.chrono.getChronoS("experiment")
        if delay > self.TIMEOUT_WHOLE_EXPERIMENT:
            logging.info("Experience terminated... timeout.")
            self.stop()
        
    def grabAnimalPosition(self):
    
        result = []
        # check positions from LMT        
        try:
            
            retSentence = self.clientSocket.recv(10000)
            decode = retSentence.decode()[2:]
            #print( decode )
            root = ET.fromstring( decode )
            
            #print ( root )
            for detection in root.iter('detection'):
                result.append( detection.attrib )
            '''
            for detection in root.iter('detection'):
                print("---")
                print( detection.attrib["RFID"] )
                print( detection.attrib["x"] )
                print( detection.attrib["y"] )
            '''
            
        except:
            pass
            # TODO TODO
            #print("Error while parsing XML position data from LMT")
        
        return result

    def runLogic(self):
        
        self.checkEndExperiment()
        
        animalPositionList = self.grabAnimalPosition()
        
        self.Rgate1.performOpenLogic( animalPositionList )
        self.Rgate2.performOpenLogic( animalPositionList )
        
        self.Rgate1.checkTimeOut()
        self.Rgate2.checkTimeOut()
        
        
    
    
if __name__ == '__main__':
        
    experiment = Experiment()
    experiment.TIMEOUT_WHOLE_EXPERIMENT = 60*60*24*25
    
    '''
    input("Enter to close all gates")
    experiment.Rgate1.gate.close()
    experiment.Rgate2.gate.close()
    input("Enter to start experiment !")
    '''
    
    while ( True ):
                
        # timeout of the whole experiment
        '''
        delay = chrono.getChronoS("experiment")
        if delay > TIMEOUT_WHOLE_EXPERIMENT:
            logging.info("Experience terminated... timeout.")
            stop()
        '''
        
        experiment.runLogic()
        
        sleep( 0.05 )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    