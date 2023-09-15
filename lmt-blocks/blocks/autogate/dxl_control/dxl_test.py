from blocks.autogate.dxl_control.Ax12 import Ax12deprecated

# create motor object
#my_dxl = Ax12(11)
my_dxl = Ax12(3)

# connecting
Ax12.open_port()
Ax12.set_baudrate()


def test_pos(motor_object):

    
    my_dxl.set_moving_speed(1023)
    my_dxl.set_torque_limit(1023)    
    print( motor_object.get_moving_speed() )
    motor_object.get_position()        
    input_pos = int(input("input pos: "))
    motor_object.set_position(input_pos)

test_pos(my_dxl)
#my_dxl.disable_torque()

input("Enter to quit")


Ax12.close_port()
