'''
Created on 12 oct. 2021

@author: Fab
'''


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.Qt import QProgressBar, QLabel, QFrame, QPushButton, QSlider,\
    QListWidget

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
from blocks.autogate.Parameters import *
from blocks.autogate.Gate import GateOrder, Gate, GateMode

StyleSheet = '''

#doorTitle {
    text-align: center;
    font-size: 18pt;
    font-family: Arial;
    font-weight:bold;
}
#gateTitle {
    text-align: center;
    font-size: 18pt;
    font-family: Arial;
    font-weight:bold;
}

#rfidTitle {
    text-align: center;
    font-size: 18pt;
    font-family: Arial;
    font-weight:bold;
}
#logicTitle {
    text-align: center;
    font-size: 18pt;
    font-family: Arial;
    font-weight:bold;
}
#balanceTitle {
    text-align: center;
    font-size: 18pt;
    font-family: Arial;
    font-weight:bold;
}
#gateOrder {
    text-align: center;
    font-size: 18pt;
    font-family: Arial;
    font-weight:bold;
}

#doorFrame {
    background-color:lightgray;
}

QProgressBar
{
    border: 2px solid red;
    border-radius: 5px;
    text-align: center;
    font-size:12px;
    color:black;
    background-color: #FF2222;
    border-color:black;
}

QProgressBar::chunk
{
    background-color: #d22FF22;
        
}

'''

'''
def non_blocking_lock(lock):
    if not lock.acquire(blocking=False):        
        try:
            yield lock
        finally:
            lock.release()
''' 

def horizontalWidgets( *widgets ):
    horizontalLayout = QtWidgets.QHBoxLayout()
    for w in widgets:
        horizontalLayout.addWidget( w )
    return horizontalLayout

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class WBalance(QtWidgets.QWidget):

    def __init__(self, gate, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet(StyleSheet)
        layout = QtWidgets.QVBoxLayout()
        title = QLabel( "Balance" , objectName="balanceTitle" )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget( title )
        self.gate = gate
        
        self.balanceWidget = MplCanvas (self, width=5, height=3 )        
        self.balanceWidget.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.balanceAx = self.balanceWidget.axes        
        self.balanceAx.set_ylabel("weight (g)")
        plt.tight_layout()
        layout.addWidget( self.balanceWidget )
        tareButton= QPushButton("Force tare balance")
        layout.addWidget( tareButton )
        tareButton.clicked.connect( self.tare )

        layout.addStretch()
        
        self.setLayout(layout)
    
    def tare(self):
        self.gate.arduino.tare()
    
    def setMeasures( self, data , mouseValue ):
        
        self.balanceAx.clear()
        
        print( data[-NB_VALUE_TO_COMPUTE_MEAN_WEIGHT:] )

        # accepted weight range
        min = self.gate.mouseAverageWeight * ( 1 - self.gate.weightWindowFactor )
        max = self.gate.mouseAverageWeight * ( 1 + self.gate.weightWindowFactor )
        x = [0,len(data)]
        y1 = [min,min]
        y2 = [max,max]        
        self.balanceAx.fill_between(x, y1, y2 , color="lightgray")
        
        # expected mouse weight
        self.balanceAx.axhline( mouseValue , c="green", linestyle=":", label="expected weight" )        
        self.balanceAx.axhline( self.gate.mouseAverageWeight/4 , c="gray", linestyle=":", label="no animal" )
        
        
        if len( data ) > 1:
            mean = np.mean( data[-NB_VALUE_TO_COMPUTE_MEAN_WEIGHT:] )
            self.balanceAx.axhline( mean , c="red", linestyle=":" , label="mean ( over last " + str( NB_VALUE_TO_COMPUTE_MEAN_WEIGHT ) + " reading )")
        
        self.balanceAx.plot( np.arange( 0, len(data) ), data , c="black" , label = "weight")        
        self.balanceAx.set_ylim( MIN_BALANCE_WEIGHT_GRAPH, MAX_BALANCE_WEIGHT_GRAPH )
        self.balanceAx.set_ylabel("weight (g)")
        self.balanceAx.legend( fontsize=6 )
        if self.gate.currentWeight!=None:
            self.balanceAx.text( 7,-5 , str( round( self.gate.currentWeight , 2 ) ) +"g" )
        
        # this is still slow. Should find another rendering method (with cache ?) to improve general FPS of GUI.
        #self.balanceWidget.fig.canvas.update()
        self.balanceWidget.fig.canvas.draw()
        

    
    def sizeHint(self):
        return QtCore.QSize(400, 300)

class WRFID(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet(StyleSheet)
        layout = QtWidgets.QVBoxLayout()
        title = QLabel( "RFID Log" , objectName="rfidTitle" )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget( title )
        
        self.rfidList = QListWidget()
        layout.addWidget( self.rfidList )
        
        self.rfidList.addItems( ["Not defined"] )        
        
        layout.addStretch()
        self.setLayout(layout)
        self.counter = 0
    
    def addRFID( self , rfid ):        
        self.rfidList.addItems( [str( self.counter).zfill(10) + " : " + rfid] )
        if self.rfidList.count() > 8:
            self.rfidList.takeItem( 0 )
        
        self.counter+=1
    
    def sizeHint(self):
        return QtCore.QSize(300, 150)
   
class WLogic(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet(StyleSheet)
        layout = QtWidgets.QVBoxLayout()
        title = QLabel( "Logic tracer" , objectName="logicTitle" )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget( title )
        
        self.wLogicList = QListWidget()
        layout.addWidget( self.wLogicList )
        
        self.wLogicList.addItems( ["Not defined"] )        
        
        layout.addStretch()
        self.setLayout(layout)
    
    def sizeHint(self):
        return QtCore.QSize(300, 150)
   
    def setLogic( self , logicList , selectedItem ):        
        self.wLogicList.clear()
        for logic in logicList:
            self.wLogicList.addItems( [logic] )
        
        if self.wLogicList.count() > selectedItem:
            self.wLogicList.setCurrentRow( selectedItem )
        
        

class WDoor(QtWidgets.QWidget):



    def __init__(self, name="noName", door=None , location="A", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(StyleSheet)
        
        self.door = door
        layout = QtWidgets.QVBoxLayout()
        frame = QFrame( objectName="doorFrame" )
        inFrame = QtWidgets.QVBoxLayout()
        frame.setLayout( inFrame )
        #inFrame.addWidget( QLabel("test"))        
        layout.addWidget ( frame )

        # title
        self.title = QLabel( name , objectName="doorTitle" )
        self.title.setAlignment(Qt.AlignCenter)
        inFrame.addWidget(self.title)
        
        # order
        self.orderLabel = QLabel( "Order : not defined" )
        inFrame.addWidget(self.orderLabel)                

        # status
        self.statusLabel = QLabel( "Status : not defined" )
        #layout.setFrameStyle(QFrame.Box | QFrame.Raised);
        inFrame.addWidget(self.statusLabel)
        
        # progress bar representing the position of the door.        
        self.progressBar = QProgressBar(self, minimum=0, maximum=100, objectName="progressBar")
        inFrame.addWidget( self.progressBar )        
        self.progressBar.setValue( 50 )

        # LIDAR status
        self.lidarLabelIn = QLabel( "LIDAR in: not defined" )
        self.lidarLabelExt = QLabel( "LIDAR ext: not defined" )
        
        if location=="A":
            inFrame.addLayout( horizontalWidgets( self.lidarLabelExt, self.lidarLabelIn ))
        else:
            inFrame.addLayout( horizontalWidgets( self.lidarLabelIn, self.lidarLabelExt ))
        
        self.lidarLabelIn.setStyleSheet("QLabel { padding:10px; qproperty-alignment: AlignCenter; background-color: gray; }")
        self.lidarLabelExt.setStyleSheet("QLabel { padding:10px; qproperty-alignment: AlignCenter; background-color: gray; }")

        # open / close override
        
        # title
        self.override = QLabel( "Order override:" )
        self.override.setAlignment(Qt.AlignCenter)
        inFrame.addWidget(self.override)
        
        openButton = QPushButton( "open")
        openButton.clicked.connect( self.forceOpenDoor )
        closeButton = QPushButton( "close")
        closeButton.clicked.connect( self.forceCloseDoor )        
        inFrame.addLayout( horizontalWidgets( openButton, closeButton ))
        
        
        # Create the QDial widget and set up defaults.
        # - we provide accessors on this class to override.
        '''
        self._dial = QtWidgets.QDial()
        self._dial.setNotchesVisible(True)
        self._dial.setWrapping(False)
        '''
        #self._dial.valueChanged.connect(self._bar._trigger_refresh)

        # Take feedback from click events on the meter.
        #self._bar.clickedValue.connect(self._dial.setValue)

        #inFrame.addWidget(self._dial)
        layout.addStretch()
        self.setLayout(layout)
    
    def sizeHint(self):
        return QtCore.QSize(300, 150)
    
    def forceOpenDoor(self):
        self.door.open()
    
    def forceCloseDoor(self):
        self.door.close()

        
class WGate(QtWidgets.QWidget):

    refresher = QtCore.pyqtSignal()

    def __init__(self, gate , name="Gate 1", *args, **kwargs):
        super().__init__(*args, **kwargs)

        
        self.setStyleSheet(StyleSheet)        
        layout = QtWidgets.QVBoxLayout()
        
        # title
        self.titleLabel = QLabel( name , objectName="gateTitle"  )
        self.titleLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget ( self.titleLabel )

        # doors
        
        horizontalLayout = QtWidgets.QHBoxLayout()
        
        self.wDoorA = WDoor(name ="Door A", door = gate.doorA, location = "A" )
        horizontalLayout.addWidget( self.wDoorA ) 
        
        self.wDoorB = WDoor(name= "Door B" , door = gate.doorB , location ="B" )
        horizontalLayout.addWidget( self.wDoorB )

        layout.addLayout( horizontalLayout )
        
        # gate order
        
        self.orderLabel = QLabel( "Gate order: not defined" , objectName="gateOrder"  )
        self.orderLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget ( self.orderLabel )
        
        # order button
                
        orderOneAB = QPushButton( "single mouse A to B")
        orderOneAB.clicked.connect( self.orderOneAB )
        
        orderOneBA = QPushButton( "single mouse B to A")
        orderOneBA.clicked.connect( self.orderOneBA )

        orderMultipleAB = QPushButton( "multiple mice A to B")
        orderMultipleAB.clicked.connect( self.orderMultipleAB )
        
        orderMultipleBA = QPushButton( "multiple mice B to A")
        orderMultipleBA.clicked.connect( self.orderMultipleBA )
        
        order1inB = QPushButton( "Only 1 animal in B side")
        order1inB.clicked.connect( self.order1inB )

        noOrder = QPushButton( "No order")
        noOrder.clicked.connect( self.noOrder )

        openCloseHabituation = QPushButton( "Open Close habituation")
        openCloseHabituation.clicked.connect( self.openCloseHabituation )
        
        layout.addLayout( horizontalWidgets( orderOneAB , orderOneBA, order1inB , noOrder, orderMultipleAB, orderMultipleBA, openCloseHabituation ))
        
        # speed slider
        
        '''
        self.speed = QSlider( Qt.Horizontal )
        self.speed.setMinimum( 0 )
        self.speed.setMaximum( 1023 )
        self.speed.setTickInterval( 100 )
        self.speed.setTickPosition( QSlider.TicksBelow )        
        layout.addWidget( self.speed )
        '''
        
        horizontalLayoutBottom = QtWidgets.QHBoxLayout()
                
        # balance
        self.wBalance = WBalance( gate )
        horizontalLayoutBottom.addWidget( self.wBalance )
        
        # rfid
        self.rfid = WRFID()
        horizontalLayoutBottom.addWidget( self.rfid )
        
        # logic
        self.wLogic = WLogic()
        horizontalLayoutBottom.addWidget( self.wLogic )
        
        layout.addLayout( horizontalLayoutBottom )
        
        self.setLayout(layout)
        
        
        self.gate = gate        

        self.RFIDDetectionList = []
        if self.gate.antennaRFID!=None:
            print("Listening RFID.")
            self.gate.antennaRFID.addListener( self.rfidDetectionListener )

        self.stopped = False
        thread = threading.Thread( target=self.monitorGateGUI , name = f"Thread VisualGate - {name}")
        #self.data_downloaded = QtCore.pyqtSignal(object)
        self.refresher.connect(self.on_refresh_data)
        thread.start()
        time.sleep(1)    
    
    def on_refresh_data(self):
        #self.titleLabel.setText( data )
        self.gate.lock.acquire()
        self.titleLabel.setText( self.gate.name )
        self.orderLabel.setText( str( self.gate.order ) )
        
        self.wDoorA.progressBar.setValue( int( self.gate.doorA.cacheOpenPercentage ) )
        self.wDoorA.orderLabel.setText( str( self.gate.doorA.doorOrder ) )
        self.wDoorA.statusLabel.setText( str( self.gate.doorA.status ) )
        
        self.wDoorB.progressBar.setValue( int ( self.gate.doorB.cacheOpenPercentage ) )
        self.wDoorB.orderLabel.setText( str( self.gate.doorB.doorOrder ) )
        self.wDoorB.statusLabel.setText( str ( self.gate.doorB.status ) )
        
        self.wBalance.setMeasures( self.gate.weightList, self.gate.mouseAverageWeight )
        
        #self.speed.setValue( self.gate.doorA.speedLimit )
        
        for r in self.RFIDDetectionList:                
            self.rfid.addRFID( r )
        self.RFIDDetectionList.clear()
                        
        self.wLogic.setLogic( self.gate.logicList , self.gate.logicCursor )
        
        # lidar reading
        detectionStyle = "QLabel { padding:10px; qproperty-alignment: AlignCenter; background-color: orange; }"
        noDetectionStyle = "QLabel { padding:10px; qproperty-alignment: AlignCenter; background-color: lightgreen; }"

        if self.gate.doorA.getLidarExt( ):
            self.wDoorA.lidarLabelExt.setStyleSheet( detectionStyle )
            self.wDoorA.lidarLabelExt.setText("Detection")
        else:
            self.wDoorA.lidarLabelExt.setStyleSheet( noDetectionStyle )
            self.wDoorA.lidarLabelExt.setText("Free")
        
        if self.gate.doorA.getLidarIn( ):
            self.wDoorA.lidarLabelIn.setStyleSheet( detectionStyle )
            self.wDoorA.lidarLabelIn.setText("Detection")
        else:
            self.wDoorA.lidarLabelIn.setStyleSheet( noDetectionStyle )
            self.wDoorA.lidarLabelIn.setText("Free")

        if self.gate.doorB.getLidarExt( ):
            self.wDoorB.lidarLabelExt.setStyleSheet( detectionStyle )
            self.wDoorB.lidarLabelExt.setText("Detection")
        else:
            self.wDoorB.lidarLabelExt.setStyleSheet( noDetectionStyle )
            self.wDoorB.lidarLabelExt.setText("Free")
        
        if self.gate.doorB.getLidarIn( ):
            self.wDoorB.lidarLabelIn.setStyleSheet( detectionStyle )
            self.wDoorB.lidarLabelIn.setText("Detection")
        else:
            self.wDoorB.lidarLabelIn.setStyleSheet( noDetectionStyle )
            self.wDoorB.lidarLabelIn.setText("Free")
        
        

        self.gate.lock.release()
    
    def rfidDetectionListener(self, rfid ):            
        self.RFIDDetectionList.append( rfid )
    
    def orderOneAB(self):
        gate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B )
        
    def orderOneBA(self):
        gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )
        
    def orderMultipleAB(self):
        gate.setOrder( GateOrder.ALLOW_MULTIPLE_A_TO_B )
        
    def orderMultipleBA(self):
        gate.setOrder( GateOrder.ALLOW_MULTIPLE_B_TO_A )

        
    def order1inB(self):
        gate.setOrder( GateOrder.ONLY_ONE_ANIMAL_IN_B )

    def noOrder(self):
        gate.setOrder( GateOrder.NO_ORDER )
        
    def openCloseHabituation(self):
        gate.setOrder( GateOrder.OPEN_CLOSE_HABITUATION )
    
    def monitorGateGUI(self):
        
        while( self.stopped == False ):            
            time.sleep( 0.25 )            
            self.refresher.emit()
            
            '''
            locked = self.gate.lock.acquire(blocking=False )
            if locked:
                try:
                    # read data from gate                        
                    #print("------ ENTER LOGIC MONITOR")
                    self.refresher.emit()                    
                    
                finally:
                    self.gate.lock.release()
            '''
    
    def stop(self):
        logging.info("VisualGate Stop")        
        self.stopped = True

def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')

        
if __name__ == '__main__':

    logFile = "log/gateLog - "+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"
    os.makedirs(os.path.dirname(logFile), exist_ok=True)    
    print("Logfile: " , logFile )
    #logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s:%(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S : ' )    
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )        
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    logging.info('Application started.')

    
    sys.excepthook = excepthook
    
    # LIDAR ? est ce qu'elles arrivent à gérer d'etre pincées ?
    # RFID ? est ce que je mets 2 antennes ?
    # est ce que le couloir est trop grand ? est ce que je peux le retrécir de 2 cm en longueur de chaque coté
    # à quel endroit ça va peter physiquement ?
    # 185 g > femmelle ? age
    # male > 700 g
    
    
    gate = Gate( 
        COM_Servo = "COM80", 
        COM_Arduino= "COM81", 
        #COM_RFID = "COM5", 
        name="LMT Block AutoGate",
        weightFactor = 0.74, # 0.74
        mouseAverageWeight = 20,
        #enableLIDAR= True,
        #lidarPinOrder = ( 1, 0, 3 , 2 ), # porte sugar benoit
        #lidarPinOrder = ( 2, 3, 1 , 0 ), # porte social benoit
        gateMode = GateMode.MOUSE,
        enableLIDAR = False,
        invertScale = True
         )
    
    #gate.setRFIDControlEnabled(False)
    #gate.setAllowOverWeight( True )
    
    
    
    #gate.setSpeedAndTorqueLimits(500, 500)
    
    #gate.close()
    
    '''
    gate.stop()
    quit()
    '''
    
    gate.setRFIDControlEnabled ( True ) # will / will not perform ID check    
    #gate.addForbiddenRFID("001039048351")
        
    #gate.setSpeedAndTorqueLimits(150, 150)
    #gate.setOrder( GateOrder.ALLOW_A_TO_B )
    #gate.open()

    app = QtWidgets.QApplication([])    
    wgate = WGate( gate )
    wgate.show()
    wgate.setWindowTitle("LMT Visual Gate")
    def exitHandler():
        wgate.stop()
        gate.stop()
    app.aboutToQuit.connect(exitHandler)
    sys.exit( app.exec_() )
    
        
    