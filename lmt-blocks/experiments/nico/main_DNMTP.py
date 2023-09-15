'''
Created by Nicolas Torquet at 06/03/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''


# TODO:
#  - compute score and store results


import logging
import sys
import time
from datetime import datetime
from blocks.autogate.Gate import Gate, GateOrder
from blocks.FED3.Fed3Manager3 import Fed3Manager3

from ExperimentConfig import Experiment, Animal, Session, Phase
import Trial_DNMTP

import threading



def deviceListener(event):
    '''
    Listen the gate:
     - an animal entered the test zone -> get its RFID number -> start a session
     - an animal exit the test zone - end a session
    '''
    if "Animal allowed to cross" in event.description:
        rfid = event.data  # RFID
        print(event.description.split(":")[-1])  # RFID
        if rfid in experiment.getAnimalList():
            # Animal already in the experiment
            animal = experiment.getAnimal(rfid)
        else:
            # Animal not yet in the experiment
            animal = Animal(rfid, rfid=rfid)
            experiment.addAnimal(animal)
        print("Animal list: "+str(experiment.getAnimalList()))

        # get Gate
        gate = event.deviceObject
        if "SIDE B" in event.description:
            # animal enters the side B (test zone)
            print(f"Animal {rfid} is going to zone B")
            logging.info(f"Animal {rfid} is going to zone B")
            # session creation
            session = Session(experiment, animal, gate)
            animal.setCurrentSession(session)

            # session.currentPhase is found during creation of the session
            animal.getCurrentPhase().addSession(session)
            # change the gate's logic to let animal exit
            # do the trials for this session
            print(f'Run session phase number {session.currentPhase.getNumberPhase()}: {session.currentPhase.getPhaseModelName()}')
            #session.doSession()
            thread = threading.Thread( target=session.doSession , name=f"Thread doSession {rfid}")
            session.setThread(thread)
            thread.start()

        if "SIDE A" in event.description:
            # animal enters the side A (social environment)
            print(f"Animal {rfid} is going to zone A")
            logging.info(f"Animal {rfid} is going the zone A")
            # session end
            session = animal.getCurrentSession()
            if session.getIsProcessing:
                session.endsTheSession()
            animal.setCurrentSession(None)
            # check the score to move on to the next phase if necessary
            if animal.currentPhase.getCompleted():
                # create next phase
                currentPhaseNumber = experiment.getPhaseNumberFromPhaseName(animal.getCurrentPhase().getPhaseModelName())
                if currentPhaseNumber != -1:
                    newPhase = Phase(experiment.getPhaseModelFromIndex(currentPhaseNumber+1), *experiment.getPhaseModelFromIndex(currentPhaseNumber+1).getConfig())
                    animal.addPhaseToPhaseList(newPhase)
                    logging.info(f'[Experiment]: animal {rfid} goes to the next phase: {newPhase.getPhaseModelName()}')
                else:
                    print(f'[ERROR]: next phase has not been found for animal {rfid}')
                    logging.info(f'[ERROR]: next phase has not been found for animal {rfid}')

            # change the gate's logic to let a new animal enter

    if "Checking RFID: Can't read ID of animal" in event.description:
        print("PROBLEM: CANT READ RFID!")
        logging.info("PROBLEM: CANT READ RFID!")


if __name__ == '__main__':
    ### experiment creation
    global experiment
    experiment = Experiment('DNMTP_experiment')

    ### Variables
    averageWeight = 36

    ### Define hardwares
    # Gates
    gate1 = Gate(
        COM_Servo="COM80",
        COM_Arduino="COM81",
        COM_RFID="COM82",
        name="GATE TEST1",
        weightFactor=0.62,
        mouseAverageWeight=averageWeight,
    )
    gate1.setLidarPinOrder((0, 1, 2, 3))
    gate1.setRFIDControlEnabled(True)
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
    gate2.setOrder(GateOrder.ONLY_ONE_ANIMAL_IN_B, noOrderAtEnd=True)


    # FED
    fed1 = Fed3Manager3(name="fed1", comPort="COM84")
    fed2 = Fed3Manager3(name="fed2", comPort="COM90")


    ### Experiment initialization
    experiment.addGate(gate1)
    experiment.addGate(gate2)
    experiment.addFedToGate(gateName="GATE TEST1", fed=fed1)
    experiment.addFedToGate(gateName="GATE TEST2", fed=fed2)
    experiment.createAndAddPhaseModel(namePhase='habituation', numberPhase=1, percentToSucceed=80, numberOfLastTrialToSucceed=100,
                                      delayTrials=10, maxSessionTime=500)
    experiment.createAndAddPhaseModel(namePhase='DNMTP 1s', numberPhase=2, percentToSucceed=80, numberOfLastTrialToSucceed=30,
                                      delayTrials=10, delaySteps=1, maxSessionTime=500, maxTimeBetweenSteps=20)
    experiment.createAndAddPhaseModel(namePhase='DNMTP 3s', numberPhase=2, percentToSucceed=80, numberOfLastTrialToSucceed=30,
                                      delayTrials=10, delaySteps=3, maxSessionTime=500, maxTimeBetweenSteps=20)
    experiment.createAndAddPhaseModel(namePhase='DNMTP 5s', numberPhase=2, percentToSucceed=80, numberOfLastTrialToSucceed=30,
                                      delayTrials=10, delaySteps=5, maxSessionTime=500, maxTimeBetweenSteps=20)
    experiment.createAndAddPhaseModel(namePhase='DNMTP 7s', numberPhase=2, percentToSucceed=80, numberOfLastTrialToSucceed=30,
                                      delayTrials=10, delaySteps=7, maxSessionTime=500, maxTimeBetweenSteps=20)
    experiment.createAndAddPhaseModel(namePhase='DNMTP 9s', numberPhase=2, percentToSucceed=80, numberOfLastTrialToSucceed=30,
                                      delayTrials=10, delaySteps=9, maxSessionTime=500, maxTimeBetweenSteps=20)
    # experiment.createAndAddPhaseModel('DNMTP 1s', 1, 80, 30, 10, 1, numberOfTrialsPerSession=10, maxSessionTime=30, maxTimeBetweenSteps=10)
    # experiment.createAndAddPhaseModel('DNMTP 3s', 1, 80, 30, 10, 3, numberOfTrialsPerSession=10, maxSessionTime=300, maxTimeBetweenSteps=30)
    # experiment.createAndAddPhaseModel('DNMTP 5s', 1, 80, 30, 10, 5, numberOfTrialsPerSession=10, maxSessionTime=300, maxTimeBetweenSteps=30)
    # experiment.createAndAddPhaseModel('DNMTP 7s', 1, 80, 30, 10, 7, numberOfTrialsPerSession=10, maxSessionTime=300, maxTimeBetweenSteps=30)
    # experiment.createAndAddPhaseModel('DNMTP 9s', 1, 80, 30, 10, 9, numberOfTrialsPerSession=10, maxSessionTime=300, maxTimeBetweenSteps=30)
    experiment.initGateMode()

    ### Initialize the listeners
    gate1.addDeviceListener(deviceListener)
    gate2.addDeviceListener(deviceListener)
    fed1.addDeviceListener(deviceListener)
    fed2.addDeviceListener(deviceListener)

    '''
    1. listener running to see the animals enter the gate
    2. An animal is entered through gate1: a session is created -> link with the FED behind the gate1
    3. the session found information of the animal (phase and score) and order a trial with good parameters until an experimental limit or until the animal exits (listener still working)
    4. 
    '''


