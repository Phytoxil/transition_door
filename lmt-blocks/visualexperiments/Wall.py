'''
Created on 14 mars 2023

@author: Fab
'''

from enum import Enum

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