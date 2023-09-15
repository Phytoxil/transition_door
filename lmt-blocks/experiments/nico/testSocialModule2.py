'''
Created on 10 oct. 2022

@author: Fab
'''

import time

import logging
import sys
from blocks.autogate.MonoDoor import MonoDoor
from blocks.FED3.Fed3Manager import Fed3Manager

def listener( deviceEvent ):
    print("Message received: " , deviceEvent )
    

def chrono(startTime):
    now = time.perf_counter()
    return now - startTime

def checkTimer(startTime):
    duration = chrono(startTime)
    if duration >= 30:
        return True
    else:
        return False


if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout, level=logging.INFO )
    
    print( "Testing.")
    
    # self.lock = threading.Lock()

    # socialBlock = MonoDoor(  COM_Servo = "COM69", name="Social block" )
    fed1 = Fed3Manager(comPort="COM84")
    # fed1.lightoff()
    # fed2 = Fed3Manager(comPort="COM89")
    
    # socialBlock.setSpeedAndTorqueLimits(100, 1023)
    # socialBlock.close()
    #
    # socialBlock.addDeviceListener( listener )
    # now = time.perf_counter()
    timeCheck = True
    print("running...")
    while True:
        fedRead = fed1.read()
        if timeCheck:
            fed1.lightoff()
            if fedRead != None:
                if "leftIn" in fedRead:
                    print("left")
                    fed1.click()
                    time.sleep(0.5)
                    fed1.controlLight('RGBWdef_R000_G000_B000_W100_Sideb')
                    # eventTime = time.perf_counter()
                    # checkTimer(eventTime)
                    # fed1.feed()
                    # fed1.light("left")

                if "rightIn" in fedRead:
                    print("right")
                    fed1.click()
                    print('ouverture porte')
                    time.sleep(0.5)
                    fed1.controlLight('RGBWdef_R000_G000_B000_W100_Sideb')
                    # eventTime = time.perf_counter()
                    # checkTimer(eventTime)

        eventTime = time.perf_counter()
        checkTimer(eventTime)


        # if fedRead != None:
        #     if "InLeft" in fedRead:
        #         # logging.info("[FED2]:" + fedRead)
        #         # logging.info("Nose poke TEST2")
        #         print('nosepoke left -> open the door')
        #         fed1.click()
        #         # socialBlock.open()
        #         time.sleep(1)
        #         print('time out -> close the door')
        #         # socialBlock.close()
        #         fed1.light()
        #         time.sleep(3)
        #         fed1.lightoff()
        #
        #     if "InRight" in fedRead:
        #         # logging.info("[FED2]:" + fedRead)
        #         # logging.info("Nose poke TEST2")
        #         print('nosepoke right -> open the door')
        #         fed1.click()
        #         # socialBlock.open()
        #         fed1.feed()
        #         print('time out -> close the door')
        #         fed1.light()
        #         time.sleep(3)
        #         fed1.lightoff()

        # socialBlock.close()
        # time.sleep(5)
        # socialBlock.open()
        # time.sleep(5)
        
    
    
    
    
    
    