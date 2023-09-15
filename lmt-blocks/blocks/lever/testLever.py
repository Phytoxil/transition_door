'''
Created on 30 mars 2023

@author: Fab
'''
from blocks.lever.Lever import Lever
import time

def listener ( deviceEvent ):
    print( deviceEvent )
    
if __name__ == '__main__':
    
    print("Testing lever")
    
    lever = Lever( comPort="COM24" )
    
    lever.addDeviceListener( listener )
    
    while( True ):
        
        lever.light( True )
        time.sleep ( 1 )
        lever.light( False )
        time.sleep ( 1 )
        