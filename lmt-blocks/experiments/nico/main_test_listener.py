'''
Created by Nicolas Torquet at 13/03/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

from datetime import datetime
from time import sleep
from blocks.rfidreader.AntennaRFID import AntennaRFID

from blocks.autogate.Gate import Gate, GateOrder
from blocks.FED3.Fed3Manager import Fed3Manager

global currentAnimalGate1
global currentAnimalGate2


def deviceListener(event):
    print(event)
    '''
    ############# Gate #############
    '''
    if "RFID" in event.description:
        print(event.description)

    if "Animal allowed to cross" in event.description:
        print(event.data)  # RFID
        print(event.description.split(":")[-1])  # RFID
        rfid = event.description.split(":")[-1]

        # get Gate
        gate = event.deviceObject
        if "SIDE A" in event.description:
            print(f" {rfid} go to side A")
            if gate.name == "GATE TEST1":
                currentAnimalGate1 = None
            if gate.name == "GATE TEST2":
                currentAnimalGate2 = None
            # gate.setOrder(GateOrder.ALLOW_SINGLE_A_TO_B, noOrderAtEnd=True)

        if "SIDE B" in event.description:
            print(f" {rfid} go to side B")
            if gate.name == "GATE TEST1":
                currentAnimalGate1 = rfid
            if gate.name == "GATE TEST2":
                currentAnimalGate2 = rfid
            # gate.setOrder(GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True)


    '''
    ############# FED #############
    '''
    if "nose poke" in event.description:
        print(event.description)
        if "right" in event.data:
            print("nose poke right side")

        if "left" in event.data:
            print("nose poke left side")






if __name__ == '__main__':
    ### Variables
    averageWeight = 22

    ### Define hardwares
    # Gates
    gate1 = Gate(
        COM_Servo="COM80",
        COM_Arduino="COM81",
        COM_RFID="COM82",
        name="GATE TEST1",
        weightFactor=0.62,
        mouseAverageWeight=averageWeight,
        enableLIDAR=False,
    )
    gate1.setLidarPinOrder((0, 1, 2, 3))

    gate1.setRFIDControlEnabled(True)
    gate1.addDeviceListener(deviceListener)
    gate1.setOrder(GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd=True)

    gate2 = Gate(
        COM_Servo="COM85",
        COM_Arduino="COM86",
        COM_RFID="COM87",
        name="GATE TEST2",
        weightFactor=0.63,
        mouseAverageWeight=averageWeight
        # enableLIDAR= False
    )
    gate2.setLidarPinOrder((3, 2, 1, 0))
    gate2.setRFIDControlEnabled(True)
    gate2.addDeviceListener(deviceListener)
    gate2.setOrder(GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd=True)


    # # FED
    fed1 = Fed3Manager(name="fed1", comPort="COM84")
    # fed2 = Fed3Manager(name="fed2", comPort="COM89")
    fed1.addDeviceListener(deviceListener)
    # fed2.addDeviceListener(deviceListener)
    fed1.lightoff()


    while (True):
        print(gate1.currentWeight)
        # print(gate2.currentWeight)
        sleep(1)