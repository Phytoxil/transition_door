'''
Created on 14 mars 2023

@author: Fab
'''

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QPainter, QPaintEvent, QColor, QFont
from PyQt5.Qt import QRect, QImage, QRegion, QLabel, QPushButton
from visualexperiments.Wall import WWWallType, WWWallSide


class Block(QtWidgets.QWidget):


    def __init__(self, x,y, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        self.x = x*200+100
        self.y = y*200+100
        self.w = 200
        self.h = 200
        self.setGeometry( int( self.x ) , int ( self.y ) , self.w, self.h)
        self.name ="block"
        self.angle = 0
        self.wallList = []
        
        self.selected = False
        self.setFocusPolicy( Qt.StrongFocus );
    
    def setSize(self ,w , h ):
        self.w = w
        self.h = h
        self.setGeometry( int( self.x ) , int ( self.y ) , self.w, self.h)
        
        
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
        
        painter.fillRect(0, 0, self.w, self.h, QColor(220, 220, 220))

        painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 2)) 
        painter.drawRect(0,0,self.w,self.h)
        
        #painter.drawEllipse(0, 0, 40, 40)
        painter.setPen(QtGui.QPen(QtGui.QColor(200,200,200), 4))
        font = QFont('Times', 30)
        font.setBold(True)
        painter.setFont( font )
        painter.drawText( QRect( 0,0,self.w,int(self.h/2) ) , Qt.AlignCenter, self.name )

        # draw walls
        
        for wall in self.wallList:
            
                            
            painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 16 , Qt.SolidLine ))                
                
            if wall.type == WWWallType.GRID:                
                painter.setPen(QtGui.QPen(QtGui.QColor(100,100,100), 16 , Qt.DotLine ))

            if wall.type == WWWallType.PLAIN or wall.type == WWWallType.GRID:
            
                if wall.side == WWWallSide.BOTTOM:
                    painter.drawLine( 0,self.h,self.w,self.h )
                if wall.side == WWWallSide.TOP:
                    painter.drawLine( 0,0,self.w,0 )
                if wall.side == WWWallSide.LEFT:
                    painter.drawLine( 0,0,0,self.h )
                if wall.side == WWWallSide.RIGHT:
                    painter.drawLine( self.w,0,self.w,self.h )
                    
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
            painter.drawRect( 0+distance,0+distance,self.w-distance*2,self.h-distance*2 )
        
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
