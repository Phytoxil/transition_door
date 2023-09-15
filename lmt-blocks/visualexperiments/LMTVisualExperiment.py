'''
Created on 11 avr. 2022

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
from device.autodoor.Gate import GateOrder, Gate
from device.autodoor.gui.Parameters import NB_VALUE_TO_COMPUTE_MEAN_WEIGHT,\
    MAX_BALANCE_WEIGHT_GRAPH, MIN_BALANCE_WEIGHT_GRAPH,\
    DEFAULT_TORQUE_AND_SPEED_LIMIT
import os


class DragButton(QPushButton):

    def __init__(self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        self.setGeometry(200, 200, 100, 100)

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(DragButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(DragButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(DragButton, self).mouseReleaseEvent(event)

def clicked():
        print ( "click as normal!" )


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = QtWidgets.QWidget()
    w.resize(800,600)

    button = DragButton("Drag", w)
    button.clicked.connect(clicked)

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