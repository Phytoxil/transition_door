'''
Created on 16 mars 2022

@author: Fab
'''
from blocks.waterpump.WaterPump import WaterPump


if __name__ == '__main__':
    waterPump = WaterPump( comPort="COM6" )
    waterPump.pump(255,5000) # 5 seconds at max speed