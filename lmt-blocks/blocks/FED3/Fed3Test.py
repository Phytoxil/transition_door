'''
Created on 10 mars 2022

@author: Fab
'''
from LMT.FED3.Fed3Manager import Fed3Manager

if __name__ == '__main__':
    
    fed = Fed3Manager( comPort="COM39" )
    
    #fed.send( "feed")
    #fed.send( "click")
    
    while( True ):
        fed.read()
        