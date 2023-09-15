'''
Created on 16 mars 2022

@author: Fab
'''

from time import sleep

from datetime import datetime
import logging
import sys
from blocks.autogate.Gate import Gate, GateOrder
from blocks.FED3.Fed3Manager import Fed3Manager
from blocks.waterpump.WaterPump import WaterPump
import socket
from blocks.LMTEvent.LMTEventSender import LMTEventSender

if __name__ == '__main__':
    
    
    while ( True ):
        
        UDP_IP = "127.0.0.1"
        UDP_PORT = 8552
        
        print("stop")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.sendto(bytes("rfid stop " + "test" , "utf-8"), (UDP_IP, UDP_PORT))
            
        sleep( 5 )
        LMTEventSender("test")
            
        sleep( 2 )
        
    
    
    
    
    