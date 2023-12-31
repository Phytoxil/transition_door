
from dynamixel_sdk import * 
from blocks.autogate.dxl_control.ax12_control_table import TORQUE_ENABLE,\
    ADDR_AX_TORQUE_ENABLE, TORQUE_DISABLE, ADDR_AX_GOAL_POSITION_L,\
    ADDR_AX_GOAL_SPEED_L, ADDR_AX_PRESENT_POSITION_L, ADDR_AX_PRESENT_SPEED_L,\
    ADDR_AX_LED, ADDR_AX_PRESENT_LOAD_L, ADDR_AX_PRESENT_TEMPERATURE,\
    ADDR_AX_PRESENT_VOLTAGE, ADDR_AX_TORQUE_LIMIT_L, ADDR_AX_MOVING
import logging


class Ax12Motor:
    
    def __init__(self, motor_id, motorManager ):
        """Initialize motor id"""
        self.id = motor_id
        self.motorManager = motorManager

    def set_register1(self, reg_num, reg_value):
        
        '''
        dxl_comm_result, dxl_error = self.motorManager.packetHandler.write1ByteTxRx(
            self.motorManager.portHandler, self.id, reg_num, reg_value)
        self.motorManager.check_error(dxl_comm_result, dxl_error)
        '''
        
        writeOk = False
        nbWrite = 0
        while( not writeOk ):
            nbWrite+=1
            try:
                dxl_comm_result, dxl_error = self.motorManager.packetHandler.write1ByteTxRx(
                    self.motorManager.portHandler, self.id, reg_num, reg_value)
                self.motorManager.check_error(dxl_comm_result, dxl_error)
                
                if dxl_comm_result == COMM_SUCCESS:
                    writeOk=True
                else:
                    logging.info(f"AX12Motor not COMM_SUCCESS error: writing attempt: {nbWrite}")
            except Exception as e:
                logging.info(f"AX12Motor set_register1 error")
                logging.info(e)
                
        if nbWrite> 1:
            logging.info(f"AX12Motor COMM_SUCCESS error loop out: total writing attempts: {nbWrite}")
        

    def set_register2(self, reg_num, reg_value):

        '''
        dxl_comm_result, dxl_error = self.motorManager.packetHandler.write2ByteTxRx(
            self.motorManager.portHandler, self.id, reg_num, reg_value)
        self.motorManager.check_error(dxl_comm_result, dxl_error)
        '''

        writeOk = False
        nbWrite = 0
        while( not writeOk ):
            nbWrite+=1
            try:
                dxl_comm_result, dxl_error = self.motorManager.packetHandler.write2ByteTxRx(
                    self.motorManager.portHandler, self.id, reg_num, reg_value)
                self.motorManager.check_error(dxl_comm_result, dxl_error)
                
                if dxl_comm_result == COMM_SUCCESS:
                    writeOk=True
                else:
                    logging.info(f"AX12Motor not COMM_SUCCESS error: writing attempt: {nbWrite}")
            except Exception as e:
                logging.info(f"AX12Motor set_register2 error")
                logging.info(e)
                
        if nbWrite> 1:
            logging.info(f"AX12Motor COMM_SUCCESS error loop out: total writing attempts: {nbWrite}")
        


    def get_register1(self, reg_num):
        reg_data, dxl_comm_result, dxl_error = self.motorManager.packetHandler.read1ByteTxRx(
            self.motorManager.portHandler, self.id, reg_num)
        self.motorManager.check_error(dxl_comm_result, dxl_error)
        return reg_data

    def get_register2(self, reg_num_low):
        
        readOk = False
        nbRead = 0
        while( not readOk ):
            nbRead+=1
            
            try:
                reg_data, dxl_comm_result, dxl_error = self.motorManager.packetHandler.read2ByteTxRx(
                    self.motorManager.portHandler, self.id, reg_num_low)
                self.motorManager.check_error(dxl_comm_result, dxl_error)
            
                if dxl_comm_result == COMM_SUCCESS:
                    readOk=True
                else:
                    logging.info(f"AX12Motor not COMM_SUCCESS error: reading attempt: {nbRead}")
            except Exception as e:
                logging.info(f"AX12Motor get_register2 error")
                logging.info(e)
            
        if nbRead > 1:
            logging.info(f"AX12Motor COMM_SUCCESS error loop out: total reading attempts: {nbRead}")
        
                    
        return reg_data

    def enable_torque(self):
        """Enable torque for motor."""
        self.set_register1(ADDR_AX_TORQUE_ENABLE, TORQUE_ENABLE)
        #print(self.get_register1(ADDR_AX_TORQUE_ENABLE))
        # print("Torque has been successfully enabled for dxl ID: %d" % self.id)

    def disable_torque(self):
        """Disable torque."""
        self.set_register1(ADDR_AX_TORQUE_ENABLE, TORQUE_DISABLE)
        #print(self.get_register1(ADDR_AX_TORQUE_ENABLE))
        # print("Torque has been successfully disabled for dxl ID: %d" % self.id)

    def set_position(self, dxl_goal_position):
        """Write goal position."""
        self.set_register2(ADDR_AX_GOAL_POSITION_L, dxl_goal_position)
        #print("Position of dxl ID: %d set to %d " % (self.id, dxl_goal_position))

    def set_moving_speed(self, dxl_goal_speed):
        """Set the moving speed to goal position [0-1023]."""
        self.set_register2(ADDR_AX_GOAL_SPEED_L, dxl_goal_speed)
        #print("Moving speed of dxl ID: %d set to %d " % (self.id, dxl_goal_speed))

    def get_position(self):
        """Read present position."""
        dxl_present_position = self.get_register2(ADDR_AX_PRESENT_POSITION_L)
        #print("ID:%03d  PresPos:%03d" % (self.id, dxl_present_position))
        return dxl_present_position

    def get_present_speed(self):
        """Returns the current speed of the motor."""
        present_speed = self.get_register2(ADDR_AX_PRESENT_SPEED_L)
        return present_speed

    def get_moving_speed(self):
        """Returns moving speed to goal position [0-1023]."""
        moving_speed = self.get_register2(ADDR_AX_GOAL_SPEED_L)
        return moving_speed

    def led_on(self):
        """Turn on Motor Led."""
        self.set_register1(ADDR_AX_LED, True)

    def led_off(self):
        """Turn off Motor Led."""
        self.set_register1(ADDR_AX_LED, False)

    def get_load(self):
        """Returns current load on motor."""
        dxl_load = self.get_register2(ADDR_AX_PRESENT_LOAD_L)
        # CCW 0-1023 # CW 1024-2047
        return dxl_load

    def get_temperature(self):
        """Returns internal temperature in units of Celsius."""
        dxl_temperature = self.get_register2(ADDR_AX_PRESENT_TEMPERATURE)
        return dxl_temperature

    def get_voltage(self):
        """Returns current voltage supplied to Motor in units of Volts."""
        dxl_voltage = (self.get_register1(ADDR_AX_PRESENT_VOLTAGE))/10
        return dxl_voltage

    def set_torque_limit(self, torque_limit):
        """Sets Torque Limit of Motor."""
        self.set_register2(ADDR_AX_TORQUE_LIMIT_L, torque_limit)        

    def get_torque_limit(self):
        """Returns current Torque Limit of Motor."""
        dxl_torque_limit = self.get_register2(ADDR_AX_TORQUE_LIMIT_L)
        return dxl_torque_limit

    def is_moving(self):
        """Checks to see if motor is still moving to goal position."""
        dxl_motion = self.get_register1(ADDR_AX_MOVING)
        return dxl_motion
    