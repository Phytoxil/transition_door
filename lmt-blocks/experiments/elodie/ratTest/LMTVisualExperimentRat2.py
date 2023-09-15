'''
Created on 11 avr. 2022

@author: Fab
'''


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QPainter, QPaintEvent, QColor, QFont

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import threading
import time
import traceback
import sys
import logging
from _datetime import datetime

import os
from PyQt5.Qt import QRect, QImage, QRegion, QLabel, QPushButton,\
    QCoreApplication
from enum import Enum
from random import randint
from visualexperiments.WWMouse import WWMouse
from visualexperiments.Block import Block
from visualexperiments.Wall import WWWallSide, WWWall, WWWallType
from visualexperiments.WWGate import WWGate
from visualexperiments.WWFed import WWWFed
from blocks.autogate.Gate import Gate, GateMode, GateOrder
from blocks.DeviceEvent import DeviceEvent
from blocks.autogate.Parameters import OPENED_DOOR_POSITION_MOUSE,\
    CLOSED_DOOR_POSITION_MOUSE
from experiments.elodie.ratTest.ExperimentEloSuperSimplev5NORFID2Lever import Experiment




StyleSheet = '''

#phaseLabel {
    text-align: center;
    font-size: 18pt;
    font-family: Arial;
    font-weight:bold;
}

#resultLabel {
    text-align: left;
    font-size: 7pt;
    font-family: Arial;    
    background-color:lightgray;
}
'''
        

class MplCanvas(FigureCanvasQTAgg): #for matplotlib

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


def clicked():
        print ( "click as normal!" )


def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')

class WWVisualExperiment(QtWidgets.QWidget):
    
    refresher = QtCore.pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setStyleSheet(StyleSheet)
        
        self.name ="Visual experiment monitoring"
        self.stopped = False
        
        print("hello")
        '''
        self.refresher.connect(self.on_refresh_data)
        self.blockList = []
        self.thread = threading.Thread( target=self.monitorGUI )
        '''
        
    def stop(self):
        print("Exiting...")
        self.stopped=True    
        self.experiment.stop()
        
    
    def on_refresh_data(self):
        self.clockLabel.setText( str( datetime.now() ) )
        #self.nbAnimalsLabel.setText( f"Number of animals in LMT: {self.experiment.nbAnimalsInLMT} / {self.experiment.targetNbAnimalInLMT}")
        phase = None
        try:
            phase = self.experiment.results[self.animalInRFID]["currentPhase"]
        except:
            pass
        self.currentPhaseLabel.setText( f"Animal: {self.experiment.animalInRFID} / Phase: {phase}" )
        self.results = None
        
        try:
            self.results = self.experiment.results
            display = ""        
            for rfid in self.results:
                display+=f"{rfid}\n"
                for phase in self.results[rfid]:
                    display+=f"{phase}\n"
                    if "phase3ListPoke" in phase:
                        for b in self.results[rfid]["phase3ListPoke"]:
                            if b:
                                display+="X"
                            else:
                                display+="_"
                        continue
                    if "currentPhase" in phase:
                        display+= self.results[rfid]["currentPhase"]
                    if "currentPhase" not in phase:
                        for r in self.results[rfid][phase]:
                            display+= str( r )+ "\n"
                        
            
            self.resultLabel.setText( display )
        except:
            pass        
        
        '''
        rfid="12345"
        self.results = {}
        self.results[rfid]= {}
        self.results[rfid]["phase1"]= [Result()] # phase 1: a drop each time the gate is crossed + one per nose poke (any hole)
        self.results[rfid]["phase2"]= [Result()] # phase 2: a drop each time a nose poke is done (any hole) stop session if ( 10 nose poke or timeout xx s)
        self.results[rfid]["phase3"]= [Result()] # phase 3: a drop each time a nose poke in the right side is done
        self.results[rfid]["phase4"]= [Result()] # phase 4: fin de test, attente dans la tente
        self.results[rfid]["phase3ListPoke"] = [] # list of poke with true or false in it.
        self.results[rfid]["currentPhase"] = "phase3"
        print ( self.results )
        '''
       
        
        
        
        #self.resultLabel.setText( str(results) )
        self.update()
    
    def monitorGUI(self):
        
        while( self.stopped == False ):            
    
            self.refresher.emit()
            #self.update()
            #QCoreApplication.processEvents( )
            #self.qWait(0.1)
            time.sleep( 0.1 )  
            #self.mouse.angle+=1
            #self.mouse.update()
            '''          
            self.block.angle+=1
            self.block.update()        
            self.fed.tare()
            '''    
    
    
    def start(self ):
        
        # start hardware
        
        self.experiment= Experiment( name="rat experiment" , startExperimentNow = False )
        self.gate1 = self.experiment.ratGate
        
        self.waterPump = self.experiment.waterPump        
        #self.fed = self.experiment.fed
        
        '''
        
        '''
        
        # start display
        shiftY = -1

        self.block = Block( 2.5,1+shiftY , self )
        self.block.setName("Test")        
        self.block.addWall( WWWall ( WWWallSide.BOTTOM ) )
        self.block.addWall( WWWall ( WWWallSide.TOP ) )
        self.block.addWall( WWWall ( WWWallSide.LEFT , WWWallType.DOOR  ) )
        self.block.addWall( WWWall ( WWWallSide.RIGHT ) )

        block3 = WWGate( 1.5,1+shiftY, self )
        block3.setName("Gate")        
        block3.bindToGate( self.gate1 )
        
        self.block = Block( 0.5,1+shiftY , self )
        self.block.setName("House")        
        self.block.addWall( WWWall ( WWWallSide.BOTTOM ) )
        self.block.addWall( WWWall ( WWWallSide.TOP ) )
        self.block.addWall( WWWall ( WWWallSide.RIGHT, WWWallType.DOOR ) )
        self.block.addWall( WWWall ( WWWallSide.LEFT ) )
        
        #self.fedBlock = WWWFed(3.5, 1.25+shiftY , self )
        #self.fedBlock.setAngle( 90 )
        
        self.resultLabel = QLabel("Clock\n\ntest\ntest" , self , objectName="resultLabel" )
        self.resultLabel.move( 150 , 320 )            
        self.resultLabel.resize( 700,350)

        
        
        y = 20
        x = 200
        self.startButton= QPushButton("Start experiment" , self )
        self.startButton.move( x , y )
        self.startButton.clicked.connect( self.startExperiment )        
        self.startButton.resize( 150,50)
                
        x+=160
        self.pauseButton= QPushButton("Pause experiment" , self )
        self.pauseButton.move( x , y )
        self.pauseButton.clicked.connect( self.pauseExperiment )
        self.pauseButton.setEnabled( False )
        self.pauseButton.resize( 150,50)

        x+=160
        self.closeDoorsButton= QPushButton("Close all doors" , self )
        self.closeDoorsButton.move( x , y )
        self.closeDoorsButton.clicked.connect( self.closeAllDoors )        
        self.closeDoorsButton.resize( 150,50)
        
        x+=160
        self.openDoorsButton= QPushButton("Open all doors" , self )
        self.openDoorsButton.move( x , y )
        self.openDoorsButton.clicked.connect( self.openAllDoors )        
        self.openDoorsButton.resize( 150,50)

        x=20
        y=100
        self.primePumpButton= QPushButton("Prime pump" , self )
        self.primePumpButton.move( x , y )
        self.primePumpButton.clicked.connect( self.primePump )        
        self.primePumpButton.resize( 150,50)
        
        y+=70
        self.dropPumpButton= QPushButton("water drop" , self )
        self.dropPumpButton.move( x , y )
        self.dropPumpButton.clicked.connect( self.dropPump )        
        self.dropPumpButton.resize( 150,50)

        y+=70
        self.readAntennaFrequencyButton= QPushButton("read\nAntenna Frequency" , self )
        self.readAntennaFrequencyButton.move( x , y )
        self.readAntennaFrequencyButton.clicked.connect( self.readAntennaFrequency )        
        self.readAntennaFrequencyButton.resize( 150,50)
        
        y+=70
        self.openBButton= QPushButton("openB" , self )
        self.openBButton.move( x , y )
        self.openBButton.clicked.connect( self.openB )        
        self.openBButton.resize( 150,50)
        
        
        
        '''
        x+=160
        self.forceDoorButton= QPushButton("Force door" , self )
        self.forceDoorButton.move( x , y )
        self.forceDoorButton.clicked.connect( self.forceDoor )        
        self.forceDoorButton.resize( 150,50)
        '''
        
        x=20
        y=20        
        self.clockLabel = QLabel("Clock" , self )
        self.clockLabel.move( x , y )            
        self.clockLabel.resize( 150,50)

        self.currentPhaseLabel = QLabel("Current phase: " , self , objectName="phaseLabel")
        self.currentPhaseLabel.setAlignment(Qt.AlignCenter)
        self.currentPhaseLabel.move( 200 , 700 )            
        self.currentPhaseLabel.resize( 600,50)
        
        '''
        self.nbMiceLMTDownButton= QPushButton("Remove 1 animal" , self )
        self.nbMiceLMTDownButton.move( 300 , 800 )
        self.nbMiceLMTDownButton.clicked.connect( self.nbMiceLMTDownButtonAction )        
        self.nbMiceLMTDownButton.resize( 200,50)
        
        self.nbMiceLMTUpButton= QPushButton("Add 1 animal" , self )
        self.nbMiceLMTUpButton.move( 500 , 800 )
        self.nbMiceLMTUpButton.clicked.connect( self.nbMiceLMTUpButtonAction )        
        self.nbMiceLMTUpButton.resize( 200,50)
        '''
        
        self.resize(1000,800 )
        self.setWindowTitle( "LMT blocks - Experiment Monitor" )
        

        
        self.thread = threading.Thread( target=self.monitorGUI )
        self.refresher.connect(self.on_refresh_data)
        self.thread.start()
            
    def startExperiment(self):
        print("Starting experiment")
        self.startButton.setEnabled(False)
        self.pauseButton.setEnabled(True)
        self.experiment.startExperiment()
        
    def pauseExperiment(self):
        print("Pause experiment")
        self.startButton.setEnabled(True)
        self.pauseButton.setEnabled(False)
        self.experiment.pauseExperiment()
    
    def nbMiceLMTUpButtonAction(self):
        self.experiment.nbAnimalsInLMT +=1
        self.experiment.refresh()
    
    def nbMiceLMTDownButtonAction(self):
        self.experiment.nbAnimalsInLMT -=1
        self.experiment.refresh()
    
    def forceDoor(self):
        print("Forcing doors !")
        
        door = self.gate1.doorA
        
        torqueLimit = door.torqueLimit
        speedLimit = door.speedLimit
        
        door.speedLimit = 500
        door.torqueLimit = 500
        door.open()
        time.sleep(0.3)
        door.close()
        time.sleep(0.3)
        door.open()
        
        door.torqueLimit = torqueLimit
        door.speedLimit = speedLimit
        
        
    def closeAllDoors(self):
        print("Closing all doors")

        self.gate1.close()
        
            
    def openAllDoors(self):
        print("Open all doors")
        self.gate1.open()
        
    def primePump(self):
        self.experiment.waterPump.pump(255,5000)
    
    def dropPump(self):
        self.experiment.waterPump.pump( 255, 30 )
    
    def openB(self):
        self.gate1.doorB.open()
        
    def readAntennaFrequency(self):
        self.gate1.antennaRFID.readFrequency()
        
if __name__ == "__main__":
    
    sys.excepthook = excepthook

    # setup logfiles
    logFile = "testLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"    
    print("Logfile: " , logFile )    
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))        
    logging.info('Application started')
    
    def exitHandler():
        visualExperiment.stop()
    
    app = QtWidgets.QApplication([])
    
    app.aboutToQuit.connect(exitHandler)
    visualExperiment = WWVisualExperiment()
    visualExperiment.start()
    visualExperiment.show()
    
    sys.exit( app.exec_() )
    
    print("ok")

    