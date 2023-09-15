'''
Created on 22 juin 2022

@author: Fab
'''
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
        

if __name__ == '__main__':
    pass