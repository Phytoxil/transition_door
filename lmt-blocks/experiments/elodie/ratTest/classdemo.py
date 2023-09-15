'''
Created on 14 mars 2023

@author: eye
'''

import threading
import time

def truc():
    
    while(True):
        print("allez hop")
        for i in range( 10 ):
            print( i )
            time.sleep( .3 )
        time.sleep( 5 )

if __name__ == '__main__':
    

    thread = threading.Thread( target= truc )
    thread.start()
    
    
    while( True ):
        print("youhou")
        time.sleep( 1 )