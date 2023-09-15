'''
Created on 23 sept. 2021

@author: Fab
'''

from dynamixel_sdk import * 
import logging
import traceback
import threading
from _datetime import datetime
from enum import Enum


    
class MotorManager:
    # Manage Dynamixel AX12A
    # one Motor manager manage all motors on a given com port.
    
    '''
    PROTOCOL_VERSION = 1.0
    BAUDRATE = 1000000             # Dynamixel default baudrate    
    # Dynamixel will rotate between this value
    MIN_POS_VAL = 0
    MAX_POS_VAL = 1023
    
    ERROR = 1
    '''

    
    def open_port(self):
        
        if self.portHandler.openPort():
            print("Motor: Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            quit()
    
    
    def set_baudrate(self):
        if self.portHandler.setBaudRate(self.BAUDRATE):
            print("Motor : Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            quit()

    
    def close_port(self):
        # Close port
        self.portHandler.closePort()
        print('Successfully closed port')

    def __init__(self, comPort ):
        self.comPort = comPort 
        self.PROTOCOL_VERSION = 1.0
        self.BAUDRATE = 1000000            
        self.MIN_POS_VAL = 0
        self.MAX_POS_VAL = 1023
        self.portHandler = PortHandler(self.comPort )
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)
        
        self.open_port()
        self.set_baudrate()
        
    
    def check_error(self, comm_result, dxl_err):
        
        
        
        #print( comm_result )
        #traceback.print_exc()
        
        '''
        known error type:
        
        if the power is lost:
        Error (1) MotorManager: COM80: [TxRxResult] Incorrect status packet!
        
        if the usb cable is removed:
        Error (1) MotorManager: COM80: [TxRxResult] Port is in use!
        '''
        
        
        if comm_result != COMM_SUCCESS:
            logging.info("-------------- MOTOR ERROR : Is the external power switched on ?")
            logging.info( datetime.now() )
            logging.info( threading.current_thread().name )
            logging.info( threading.get_ident() )
            
            for line in traceback.format_stack():
                logging.info(line.strip())
            logging.info( f"Error (1) MotorManager: {self.comPort}: {self.packetHandler.getTxRxResult(comm_result)}" )
            logging.info("--------------")            
            
        elif dxl_err != 0:
            logging.info( f"Error (2) MotorManager: {self.comPort}: {self.packetHandler.getRxPacketError(dxl_err)}" )
            logging.info("Is motor connected to power ?")
            
        '''
        if comm_result != COMM_SUCCESS:
            logging.info("Trying to reconnect motors...")
            self.close_port()
                         
            self.PROTOCOL_VERSION = 1.0
            self.BAUDRATE = 1000000            
            self.MIN_POS_VAL = 0
            self.MAX_POS_VAL = 1023
            self.portHandler = PortHandler(self.comPort )
            self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)
            
            self.open_port()
            self.set_baudrate()
        '''
        
    
