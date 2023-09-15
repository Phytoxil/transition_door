'''
Created on 14 mars 2022

@author: Fab
'''

# LMT Visual Gate

MIN_BALANCE_WEIGHT_GRAPH = -10  # min balance of the graph
MAX_BALANCE_WEIGHT_GRAPH = 60   # max balance of the graph

# Gate

MAX_GATE_WEIGHT_LIST_SIZE = 10  # number of sample of weight kept in weight list
NB_VALUE_TO_COMPUTE_MEAN_WEIGHT = 4 # number of sample to compute the mean weight in the gate

OPENED_DOOR_POSITION_MOUSE = 110
CLOSED_DOOR_POSITION_MOUSE = 290

OPENED_DOOR_POSITION_RAT = 50
CLOSED_DOOR_POSITION_RAT = 240 #270#245

NB_OBSERVATION_WEIGHT = 4 # number of measurement for check one animal or no animal
NB_OBSERVATION_RFID = 30 # number of measurement to check RFID of the animal

# Doors

DEFAULT_TORQUE_AND_SPEED_LIMIT_MOUSE = 110 # 120 # 150

DEFAULT_SPEED_LIMIT_RAT = 40 # 120 # 150
DEFAULT_TORQUE_LIMIT_RAT = 600 # 120 # 150

RE_CLOSING_THRESHOLD_PERCENTAGE = 97
OPEN_CLOSE_SENSITIVITY_PERCENTAGE = 95#98 
DURATION_OF_LIDAR_CLOSE_TEST = 2
