'''
Created on 1 juin 2023

@author: eye
'''

import logging
import time
from random import randint, random
from datetime import datetime
import sys
from blocks.autogate.Gate import Gate, GateMode, GateOrder

from blocks.waterpump.WaterPump import WaterPump

from time import sleep

from blocks.DeviceEvent import DeviceEvent
import traceback

import threading
from experiments.elodie.ratTest.utilRatExp import *
from blocks.lever.Lever import Lever
from mail.Mail import LMTMail


def thread1():
    global gate
    
    while( True ):
        gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )
        if randint(0,100)<5:
            if randint(0,10)<5:
                gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )
                #gate.open()
            else:
                gate.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B )
                #gate.close()
        sleep(0.1)

if __name__ == '__main__':
        
    gate = Gate( 
        COM_Servo = "COM80", 
        COM_Arduino= "COM81", 
        COM_RFID = "COM82", 
        name="rat_gate",
        weightFactor = 2.14 , #2.14,
        mouseAverageWeight =  292, #350, #264, #270, #412.2, # #230, #600, #150, #220, #31
        #lidarPinOrder = ( 1, 0, 3 , 2 )
        enableLIDAR = True,
        gateMode = GateMode.RAT
         )
    
    gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )
    
    thread = threading.Thread( target=thread1 , name = f"Thread timer")
    thread.start()
    thread2 = threading.Thread( target=thread1 , name = f"Thread timer")
    thread2.start()
    
    