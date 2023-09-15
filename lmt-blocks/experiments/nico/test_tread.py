'''
Created by Nicolas Torquet at 17/03/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

import logging
import sys
from datetime import datetime
from blocks.FED3.Fed3Manager3 import Fed3Manager3

# from ExperimentConfig import Experiment, Animal, Session, Phase
import Trial_DNMTP

if __name__ == '__main__':
    fed = Fed3Manager3(name="fed", comPort="COM91")

    logFile = "experimentLog_" + datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"
    print("Logfile: ", logFile)
    logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info('Application started for trial test')

    trial = Trial_DNMTP.TrialModel(fed)



