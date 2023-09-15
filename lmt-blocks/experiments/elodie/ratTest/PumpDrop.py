'''
Created on 16 mars 2022

@author: Fab
'''
from blocks.waterpump.WaterPump import WaterPump
from time import sleep
import time


if __name__ == '__main__':
    print("Start")
    waterPump = WaterPump(comPort="COM6", name="WaterPump")

    waterPump.pump( 255, 200 ) # pour pompe 2
    
    
    for i in range( 5 ):
        print( i )
        waterPump.pump( 255,200 ) # 95
        time.sleep( 1 )
    
    
    
        
    print("Done")