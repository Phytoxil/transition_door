'''
Created on 11 avr. 2022

@author: Fab
'''


import logging
import sys
import threading
import time
import traceback
from _datetime import datetime
from typing import cast

from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import QLabel, QPushButton
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from transition_doors.transition_doors import TransitionDoors, GateWrapper
from visualexperiments.Block import Block
from visualexperiments.WWGate import WWGate
from visualexperiments.Wall import WWWall, WWWallSide


class Experiment():
    
    def __init__(self, transition_doors: TransitionDoors):#gate1: Gate, gate2: Gate ):

        self.transition_doors = transition_doors

        gate_enter = cast(GateWrapper, transition_doors.sas_enter).gate
        gate_exit = cast(GateWrapper, transition_doors.sas_exit).gate

        if transition_doors.sas_enter.position.lower() == "right":
            self.gate1 = gate_enter
            self.gate2 = gate_exit
        else:
            self.gate1 = gate_exit
            self.gate2 = gate_enter

        # self.gate1 = Gate(
        # COM_Servo = "COM85",
        # COM_Arduino= "COM86",
        # COM_RFID = "COM88",
        # name="Gate 1",
        # weightFactor = 0.65,
        # mouseAverageWeight = 25,
        # lidarPinOrder = ( 0, 1, 3 , 2 ),
        # gateMode = GateMode.MOUSE,
        # invertScale = False
        #  )
        #
        # self.gate2 = Gate(
        # COM_Servo = "COM80",
        # COM_Arduino= "COM81",
        # COM_RFID = "COM83",
        # name="Gate 2",
        # weightFactor = 0.65,
        # mouseAverageWeight = 25,
        # gateMode = GateMode.MOUSE,
        # enableLIDAR=False
        #  )
        #
        # self.gate1.doorB.setLimits( OPENED_DOOR_POSITION_MOUSE, CLOSED_DOOR_POSITION_MOUSE-20 )
        
        # self.nbAnimalsInLMT = 3
        # self.targetNbAnimalInLMT = 3
        
        # self.gate1.addDeviceListener( self.listener )
        # self.gate2.addDeviceListener( self.listener )
        # self.gateList = [ self.gate1 , self.gate2 ]
        
        self.enabled = False
        
        self.threadTempo= threading.Thread( target= self.tempo )
        
    def tempo(self):
        while(True):
            self.refresh()
            time.sleep(1)
        
    def startExperiment(self):
        self.transition_doors.startExperiment()
        # print("Start experiment")
        # self.enabled = True
        # self.gate1.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )
        # self.gate2.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )
    
    def pauseExperiment(self):
        self.transition_doors.pauseExperiment()
        # print("Pause experiment")
        # self.enabled = False
        
    def refresh(self):
        # call this if you change a parameter of the experiment so that it takes it into account
        # self.listener( DeviceEvent( "refresh", self, "", None ))
        pass

        

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
    
    def __init__(self, transition_doors: TransitionDoors): #gate_1: Gate, gate_2: Gate):
        super().__init__()
        
        self.name ="Visual experiment monitoring"
        self.stopped = False

        self.transition_doors = transition_doors

        # if transition_doors.sas_enter.position.lower() is 'left':
        #     left_gate = transition_doors.sas_enter.
        # self.gate1 = cast(GateWrapper, transition_doors.sas_enter).gate
        # self.gate2 = cast(GateWrapper, transition_doors.sas_exit).gate

        gate_enter = cast(GateWrapper, transition_doors.sas_enter).gate
        gate_exit = cast(GateWrapper, transition_doors.sas_exit).gate

        if transition_doors.sas_enter.position.lower() == "right":
            self.gate1 = gate_enter
            self.gate2 = gate_exit
        else:
            self.gate1 = gate_exit
            self.gate2 = gate_enter

        print("hello")
        '''
        self.refresher.connect(self.on_refresh_data)
        self.blockList = []
        self.thread = threading.Thread( target=self.monitorGUI )
        '''
        
    def stop(self):
        print("Exiting...")
        self.stopped=True    
        self.gate1.stop()
        self.gate2.stop()
    
    def on_refresh_data(self):
        self.clockLabel.setText( str( datetime.now() ) )
        # self.nbAnimalsLabel.setText( f"Number of animals in LMT: {self.experiment.nbAnimalsInLMT} / {self.experiment.targetNbAnimalInLMT}")
        self.nbAnimalsLabel.setText( f"Number of animals in LMT: {self.transition_doors.nb_mice_in_limited} / {self.transition_doors.max_number}")
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
        
        # self.experiment= Experiment(self.gate1, self.gate2)
        self.experiment= Experiment(transition_doors=self.transition_doors)
        # self.gate1 = self.experiment.gate1
        # self.gate2 = self.experiment.gate2
        
        '''
        
        '''
        
        # start display

        self.block = Block( 0,0 , self )
        self.block.setName("BlackBox")
        self.block.setSize( 800 , 200 )
        self.block.addWall( WWWall ( WWWallSide.BOTTOM ) )
        self.block.addWall( WWWall ( WWWallSide.TOP ) )
        self.block.addWall( WWWall ( WWWallSide.LEFT ) )
        self.block.addWall( WWWall ( WWWallSide.RIGHT ) )

        block3 = WWGate( 2.3,1, self )
        block3.setName("Gate 1")
        block3.setAngle(90)
        block3.bindToGate( self.gate1 )
        
        block4 = WWGate( 0.8,1, self )
        block4.setName("Gate 2")
        block4.setAngle(90)
        block4.bindToGate( self.gate2 )

        self.block = Block( 0.8,2 , self )
        self.block.setName("LMT")
        self.block.setSize( 500 , 500 )
        self.block.addWall( WWWall ( WWWallSide.BOTTOM ) )
        self.block.addWall( WWWall ( WWWallSide.TOP ) )
        self.block.addWall( WWWall ( WWWallSide.LEFT ) )
        self.block.addWall( WWWall ( WWWallSide.RIGHT ) )
        
        
        
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
        
        x+=160
        self.forceDoorButton= QPushButton("Force door" , self )
        self.forceDoorButton.move( x , y )
        self.forceDoorButton.clicked.connect( self.forceDoor )        
        self.forceDoorButton.resize( 150,50)
        
        
        x=20
        y=20        
        self.clockLabel = QLabel("Clock" , self )
        self.clockLabel.move( x , y )            
        self.clockLabel.resize( 150,50)

        self.nbAnimalsLabel = QLabel("NbAnimalsInLMT" , self )
        self.nbAnimalsLabel.setAlignment(Qt.AlignCenter)
        self.nbAnimalsLabel.move( 400 , 700 )            
        self.nbAnimalsLabel.resize( 200,50)
                
        self.nbMiceLMTDownButton= QPushButton("Remove 1 animal" , self )
        self.nbMiceLMTDownButton.move( 300 , 800 )
        self.nbMiceLMTDownButton.clicked.connect( self.nbMiceLMTDownButtonAction )        
        self.nbMiceLMTDownButton.resize( 200,50)
        
        self.nbMiceLMTUpButton= QPushButton("Add 1 animal" , self )
        self.nbMiceLMTUpButton.move( 500 , 800 )
        self.nbMiceLMTUpButton.clicked.connect( self.nbMiceLMTUpButtonAction )        
        self.nbMiceLMTUpButton.resize( 200,50)
        
        
        self.resize(1000,1000)
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
        # self.experiment.nbAnimalsInLMT +=1
        self.transition_doors.nb_mice_in_limited +=1
        self.experiment.refresh()
    
    def nbMiceLMTDownButtonAction(self):
        # self.experiment.nbAnimalsInLMT -=1
        self.transition_doors.nb_mice_in_limited -=1
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
        self.gate2.close()
            
    def openAllDoors(self):
        print("Open all doors")
        self.gate1.open()
        self.gate2.open()
    
    
        
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

    