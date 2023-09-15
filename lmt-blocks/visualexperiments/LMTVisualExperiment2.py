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
from device.autodoor.Gate import GateOrder, Gate
from device.autodoor.gui.Parameters import NB_VALUE_TO_COMPUTE_MEAN_WEIGHT,\
    MAX_BALANCE_WEIGHT_GRAPH, MIN_BALANCE_WEIGHT_GRAPH,\
    DEFAULT_TORQUE_AND_SPEED_LIMIT
import os
from PyQt5.Qt import QRect, QImage, QRegion, QLabel, QPushButton
from enum import Enum
from random import randint

class WWWallSide( Enum ):
    TOP = 1
    BOTTOM= 2
    LEFT = 3
    RIGHT = 4

class WWWallType( Enum ):
    PLAIN = 1
    DOOR = 2
    GRID = 3    

    
class WWWall:
    
    def __init__(self , wallSide : WWWallSide, wallType = WWWallType.PLAIN ):
        self.side = wallSide
        self.type = wallType


        
class WWMouse(QtWidgets.QWidget):

    
    def __init__(self, x,y, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        self.x = x*200+100
        self.y = y*200+100
        
        self.setGeometry(self.x, self.y, 100, 100)
        self.name ="block"
        self.angle = 0
        self.img = QImage()
        self.img.load("mouse.jpg")
        
        mask = QRegion( 0,0,100,100, QRegion.Ellipse)
        self.setMask( mask )
        
        
        
        #self.keyPressed.connect(self.on_key)
    
    def setName(self , name ):
        self.name = name
        self.update()
    
    def setAngle(self , angle ):
        self.angle = angle
        self.update()


    
    
    def paintEvent(self, event: QPaintEvent):
        
        painter = QPainter()
        painter.begin(self)
            
        painter.translate(100,100);
        painter.rotate(self.angle);
        painter.translate(-100,-100);
        
        painter.drawImage(self.rect(), self.img)
        
        painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 4))
        painter.drawEllipse(0, 0, self.width(), self.height())
        
        '''
        painter.fillRect(0, 0, 200, 200, QColor(220, 220, 220))

        painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 4)) 
        painter.drawRect(0,0,200,200)
        
        #painter.drawEllipse(0, 0, 40, 40)
        painter.setPen(QtGui.QPen(QtGui.QColor(200,200,200), 4))
        font = QFont('Times', 30)
        font.setBold(True)
        painter.setFont( font )
        painter.drawText( QRect( 0,0,200,50) , Qt.AlignCenter, self.name )
        '''

        painter.end()
    
        
    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(WWMouse, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(WWMouse, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(WWMouse, self).mouseReleaseEvent(event)



class Block(QtWidgets.QWidget):


    def __init__(self, x,y, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        self.x = x*200+100
        self.y = y*200+100
        
        self.setGeometry(self.x, self.y, 200, 200)
        self.name ="block"
        self.angle = 0
        self.wallList = []
        
        self.selected = False
        self.setFocusPolicy( Qt.StrongFocus );
    
    def setName(self , name ):
        self.name = name
        self.update()
    
    def setAngle(self , angle ):
        self.angle = angle
        self.update()
        
    def addWall(self , wall ):
        self.wallList.append( wall )
        
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selected = True        
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.selected = False
        
    
    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_R:
            self.angle+=90
            self.update()
        
            
             
        event.accept()
        
    def paintEvent(self, event: QPaintEvent):
        
        painter = QPainter()
        painter.begin(self)
            
        painter.translate(100,100);
        painter.rotate(self.angle);
        painter.translate(-100,-100);
        
        painter.fillRect(0, 0, 200, 200, QColor(220, 220, 220))

        painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 2)) 
        painter.drawRect(0,0,200,200)
        
        #painter.drawEllipse(0, 0, 40, 40)
        painter.setPen(QtGui.QPen(QtGui.QColor(200,200,200), 4))
        font = QFont('Times', 30)
        font.setBold(True)
        painter.setFont( font )
        painter.drawText( QRect( 0,0,200,50) , Qt.AlignCenter, self.name )

        # draw walls
        
        for wall in self.wallList:
            
                            
            painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 16 , Qt.SolidLine ))                
                
            if wall.type == WWWallType.GRID:                
                painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 16 , Qt.DotLine ))

            if wall.type == WWWallType.PLAIN or wall.type == WWWallType.GRID:
            
                if wall.side == WWWallSide.BOTTOM:
                    painter.drawLine( 0,200,200,200 )
                if wall.side == WWWallSide.TOP:
                    painter.drawLine( 0,0,200,0 )
                if wall.side == WWWallSide.LEFT:
                    painter.drawLine( 0,0,0,200 )
                if wall.side == WWWallSide.RIGHT:
                    painter.drawLine( 200,0,200,200 )
                    
            if wall.type == WWWallType.DOOR:
            
                if wall.side == WWWallSide.BOTTOM:
                    painter.drawLine( 0,200,100-25,200 )
                    painter.drawLine( 100+25,200,200,200 )
                if wall.side == WWWallSide.TOP:                                        
                    painter.drawLine( 0,0,100-25,0 )
                    painter.drawLine( 100+25,0,200,0 )
                if wall.side == WWWallSide.LEFT:
                    painter.drawLine( 0,0,0,100-25 )
                    painter.drawLine( 0,100+25,0,200 )
                if wall.side == WWWallSide.RIGHT:
                    painter.drawLine( 200,0,200,100-25 )
                    painter.drawLine( 200,100+25,200,200 )

        if self.selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 2 , Qt.DotLine ))
            distance = 20
            painter.drawRect( 0+distance,0+distance,200-distance*2,200-distance*2 )
        
        painter.end()
        
        
    

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(Block, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(Block, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(Block, self).mouseReleaseEvent(event)


class MplCanvas(FigureCanvasQTAgg): #for matplotlib

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class WWWFed(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setGeometry(100,200,200,200)

        #self.setStyleSheet(StyleSheet)
        layout = QtWidgets.QVBoxLayout()
        title = QLabel( "Fed" , objectName="balanceTitle" )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget( title )
        #self.gate = gate
        
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
        print( "tare")
        self.balanceAx.clear()
        
        a = []
        b = []
        for i in range(10):
            a.append( randint(0,40) )
            b.append( randint(0,40) )
            
        self.balanceWidget.axes.plot(a,b)
        self.balanceWidget.fig.canvas.draw()
        
        


    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(WWWFed, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(WWWFed, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(WWWFed, self).mouseReleaseEvent(event)

class WWGate(Block):
    
    def __init__(self, x,y, *args, **kwargs ):
        
        super().__init__( x, y , *args, **kwargs )
        
        '''
        self.x = x*200+100
        self.y = y*200+100
        
        self.setGeometry(self.x, self.y, 200, 200)
        '''
        
        self.name ="GATE"
    

    def paintEvent(self, event: QPaintEvent):
        
        super().paintEvent( event )
        
        painter = QPainter()
        painter.begin(self)

        painter.translate(100,100);
        painter.rotate(self.angle);
        painter.translate(-100,-100);
        
        # tunnel
        painter.fillRect(0, 100-25, 200, 50, QColor(240, 240, 240))
        painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 4)) 
        painter.drawRect(0, 100-25,200, 50)
        
        # door A
        painter.fillRect(20, 100-25, 10, 50, QColor(255, 165, 0))
        painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 1)) 
        painter.drawRect(20, 100-25, 10, 50)
        
        # door B
        painter.fillRect(160, 100-25, 10, 50, QColor(255, 165, 0))
        painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 1)) 
        painter.drawRect(160, 100-25, 10, 50)
        
        # draw A
        painter.setPen(QtGui.QPen(QtGui.QColor(255,255,255), 4))
        font = QFont('Times', 30)
        font.setBold(True)
        painter.setFont( font )
        painter.drawText( QRect( 0,125,50,75) , Qt.AlignCenter, "A" )
        painter.drawText( QRect( 140,125,50,75) , Qt.AlignCenter, "B" )

        
        #print( Block.blockList )
        
        '''
        if ( self.orientation == WWOrientation.LEFT or self.orientation == WWOrientation.RIGHT ):             
            
        if ( self.orientation == WWOrientation.TOP or self.orientation == WWOrientation.BOTTOM ):             
            painter.fillRect(0, 100-25, 200, 50, QColor(240, 240, 240))
            painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 4)) 
            painter.drawRect(0, 100-25,200, 50)
        '''

        
        '''
        painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 4)) 
        painter.drawRect(0,0,200,200)
        
        #painter.drawEllipse(0, 0, 40, 40)
        painter.setPen(QtGui.QPen(QtGui.QColor(200,200,200), 4))
        font = QFont('Times', 30)
        font.setBold(True)
        painter.setFont( font )
        painter.drawText( QRect( 0,0,200,50) , Qt.AlignCenter, self.name )
        '''
        painter.end()
        


def clicked():
        print ( "click as normal!" )


def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')

class WWVisualExperiment:
    
    def __init__(self ):
        
        self.blockList = []
        
        
        
        
if __name__ == "__main__":
    
    sys.excepthook = excepthook

    visualExperiment = WWVisualExperiment()

    app = QtWidgets.QApplication([])
    w = QtWidgets.QWidget()
    
    
    

    block = Block( 0,0 , w )
    block.setName("Social")
    block.addWall( WWWall ( WWWallSide.BOTTOM ) )
    block.addWall( WWWall ( WWWallSide.TOP ) )
    block.addWall( WWWall ( WWWallSide.LEFT ) )
    block.addWall( WWWall ( WWWallSide.RIGHT, WWWallType.GRID ) )    
    
    block2 = Block( 1,0, w )
    block2.setName("Social")
    block2.addWall( WWWall ( WWWallSide.BOTTOM ) )
    block2.addWall( WWWall ( WWWallSide.TOP ) )
    block2.addWall( WWWall ( WWWallSide.RIGHT, WWWallType.DOOR ) )
    
    block3 = WWGate( 2,0, w )
    block3.setName("Gate")
    
    block4 = Block( 3,0, w )    
    block4.setName("House")
    block4.addWall( WWWall ( WWWallSide.TOP ) )
    block4.addWall( WWWall ( WWWallSide.RIGHT ) )
    block4.addWall( WWWall ( WWWallSide.LEFT, WWWallType.DOOR ) )
    
    
    block5 = Block( 3,1, w )
    block5.setName("House")
    block5.addWall( WWWall ( WWWallSide.LEFT ) )
    block5.addWall( WWWall ( WWWallSide.RIGHT ) )
    block5.addWall( WWWall ( WWWallSide.BOTTOM, WWWallType.DOOR ) )


    block7 = WWGate( 3,2, w )
    block7.setName("Gate")
    block7.setAngle(90)
    
    block8 = Block( 3,3, w )
    block8.setName("Water")
    block8.addWall( WWWall ( WWWallSide.TOP, WWWallType.DOOR ) )
    block8.addWall( WWWall ( WWWallSide.LEFT ) )
    block8.addWall( WWWall ( WWWallSide.RIGHT ) )
    block8.addWall( WWWall ( WWWallSide.BOTTOM ) )


    mouse = WWMouse( 0.5,1.8 , w )
    mouse2 = WWMouse( 0.8,2 , w )
    mouse3 = WWMouse( 1,2.5 , w )

    fed = WWWFed( w )
    fed = WWWFed( w )
    fed = WWWFed( w )

    w.resize(1000,1000)
    w.setWindowTitle( "LMT block - Experiment Monitor" )
    
    #button.clicked.connect(clicked)

    w.show()
    app.exec_()

'''
class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(30,30,600,400)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))  
        qp.setBrush(br)   
        qp.drawRect(QtCore.QRect(self.begin, self.end))       

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    
    
    
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())
'''