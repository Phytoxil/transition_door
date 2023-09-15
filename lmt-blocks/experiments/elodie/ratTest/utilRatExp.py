'''
Created on 17 mars 2023

@author: eye
'''

maxDurationSSessionDic = {"phase1": 60000000, "phase2": 60*2, "phase3": 60*2, "phase4": 60*2,"phase5":600000000 }

#maxNbTrialPerSession = {"phase1": 20, "phase2": 20, "phase3": 20, "phase4": 20}
maxNbTrialPerSession = {"phase1": 4, "phase2": 4, "phase3": 4, "phase4": 4}

inactivityBetweenTrialsDic = {"phase1": 1, "phase2": 1, "phase3": 1, "phase4": 1}

errorHoldTestDurationDic = {"phase1": 1, "phase2": 1, "phase3": 2, "phase4": 2}

dropSizeDic = {"phase1": 30, "phase2": 20, "phase3": 20, "phase4": 20}

targetSideList = ["right", "left"]

#MAX_NB_SESSION_PHASE1 = 4
MAX_NB_PRESS_PHASE1 = 6 #10

#MAX_NB_SESSION_PHASE2 = 4

MAX_NB_PRESS_SESSION2 = 6 #10

NB_PRESS_CORRECT_PHASE2 = 20

#MAX_NB_POKE_SESSION2 = 20
#NB_NOSE_POKE_CORRECT_PHASE2= 10

#NUMBER_OF_MIN_POKE_PHASE3 = 20
NUMBER_OF_MIN_PRESS_PHASE3 = 6 #30
RATIO_PHASE3 = 0.8

NUMBER_OF_MIN_PRESS_PHASE4 = 30
RATIO_PHASE4 = 0.8