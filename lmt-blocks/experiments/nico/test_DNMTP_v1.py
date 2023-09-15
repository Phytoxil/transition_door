'''
Created by Nicolas Torquet at 25/11/2022
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

'''
Results stored in JSON file. This file will be reloaded if necessary.
'''

import random
import time
from datetime import datetime
import logging
import sys
from blocks.FED3.Fed3Manager import Fed3Manager
from protocol_DNMTP_v1 import *
import json

def listener(deviceEvent):
    print('Message received:', deviceEvent)


if __name__ == '__main__':
    '''
    Experimental design
    '''
    # fed1 = Fed3Manager(name="fed1", comPort="COM84")
    fed1 = Fed3Manager(name="fed1", comPort="COM94")
    experimentName = 'Elsa'
    results = Results(experimentName)

    animal_01 = Animal("mouse_01")
    animal_02 = Animal("mouse_02")
    group = {'animal_01': animal_01, 'animal_02': animal_02}
    for animal in group.values():
        experiment = Experiment(experimentName)
        # experiment.addSession(Session(nameSession="habituation", numberSession=1, percentToSucceed=80, numberOfLastTrialToSucceed=30, delayPhases=0, delayTrials=5))
        experiment.addSession(Session(nameSession="dnmtp_1s", numberSession=1, percentToSucceed=80, numberOfLastTrialToSucceed=3, delayPhases=1, delayTrials=10))
        experiment.addSession(Session(nameSession="dnmtp_3s", numberSession=2, percentToSucceed=80, numberOfLastTrialToSucceed=3, delayPhases=3, delayTrials=10))
        experiment.addSession(Session(nameSession="dnmtp_5s", numberSession=3, percentToSucceed=80, numberOfLastTrialToSucceed=30, delayPhases=5, delayTrials=30))
        experiment.addSession(Session(nameSession="dnmtp_7s", numberSession=4, percentToSucceed=80, numberOfLastTrialToSucceed=30, delayPhases=7, delayTrials=30))
        experiment.addSession(Session(nameSession="dnmtp_9s", numberSession=5, percentToSucceed=80, numberOfLastTrialToSucceed=30, delayPhases=9, delayTrials=30))
        animal.setExperiment(experiment)
        results.addAnimal(animal)

    '''
    Load previous results if needed
    '''
    # results.loadResults(r"C:\Users\torquetn\Documents\GitHub\lmt-blocks\experiments\nico\Experiment_01.json")


    logFile = "gateLog - " + datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".txt"


    print("Logfile: ", logFile)
    # logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s:%(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S : ' )
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info('Application started.')

    print('Testing.')

    print('running...')


    '''
    One animal passes the gate and is identify
    '''
    animal_01.runExperiment(fed1, logging, results)






