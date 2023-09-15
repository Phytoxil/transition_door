'''
Created by Nicolas Torquet at 03/03/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''
import sys
import time
import random
from datetime import datetime

from blocks.DeviceEvent import DeviceEvent
from blocks.FED3.Fed3Manager import Fed3Manager
from blocks.autogate.Gate import Gate, GateOrder
import json
from Trial_DNMTP_old import Trial, TrialHabituation
import logging
from threading import Thread, Event, Lock



class PhaseModel():
    '''
    Definition of the phase, with its rules
    '''
    def __init__(self, namePhase, numberPhase, percentToSucceed, numberOfLastTrialToSucceed,
                 delayTrials = None, delaySteps = None, numberOfTrialsPerSession = None, maxSessionTime = None, maxTimeBetweenSteps = None):
        self.namePhase = namePhase
        self.numberPhase = numberPhase
        self.percentToSucceed = percentToSucceed
        self.numberOfLastTrialToSucceed = numberOfLastTrialToSucceed
        self.delayTrials = delayTrials
        self.delaySteps = delaySteps
        self.numberOfTrialsPerSession = numberOfTrialsPerSession
        self.maxSessionTime = maxSessionTime
        self.maxTimeBetweenSteps = maxTimeBetweenSteps
        print(f"phaseModel max session time: {self.maxSessionTime}")

    def getPhaseModel(self):
        return self

    def getPhaseModelName(self):
        return self.namePhase

    def getNumberPhase(self):
        return self.numberPhase

    def getPercentToSucceed(self):
        return self.percentToSucceed

    def getNumberOfLastTrialToSucceed(self):
        return self.numberOfLastTrialToSucceed

    def getDelaySteps(self):
        return self.delaySteps

    def getDelayPhases(self):
        return self.delayPhases

    def getDelayTrials(self):
        return self.delayTrials

    def getDelaySteps(self):
        return self.delaySteps

    def getNumberOfTrialsPerSession(self):
        return self.numberOfTrialsPerSession

    def getMaxSessionTime(self):
        return self.maxSessionTime

    def getMaxTimeBetweenSteps(self):
        return self.maxTimeBetweenSteps

    def getConfig(self):
        # if "habituation" in self.namePhase:
        #     return (self.namePhase, self.numberPhase, self.percentToSucceed, self.numberOfLastTrialToSucceed,
        #             self.delayTrials, self.numberOfTrialsPerSession, self.maxSessionTime)
        # else:
        return (self.namePhase, self.numberPhase, self.percentToSucceed, self.numberOfLastTrialToSucceed,
                 self.delayTrials, self.delaySteps, self.numberOfTrialsPerSession, self.maxSessionTime, self.maxTimeBetweenSteps)

    def getDicoConfig(self):
        # if "habituation" in self.namePhase:
        #     return {
        #         'namePhase': self.namePhase,
        #         'numberPhase': self.numberPhase,
        #         'percentToSucceed': self.percentToSucceed,
        #         'numberOfLastTrialToSucceed': self.numberOfLastTrialToSucceed,
        #         'delayTrials': self.delayTrials,
        #         'numberOfTrialsPerSession': self.numberOfTrialsPerSession,
        #         'maxSessionTime': self.maxSessionTime,
        #     }
        # else:
        return {
            'namePhase': self.namePhase,
            'numberPhase': self.numberPhase,
            'percentToSucceed': self.percentToSucceed,
            'numberOfLastTrialToSucceed': self.numberOfLastTrialToSucceed,
            'delayTrials': self.delayTrials,
            'delaySteps': self.delaySteps,
            'numberOfTrialsPerSession': self.numberOfTrialsPerSession,
            'maxSessionTime': self.maxSessionTime,
            'maxTimeBetweenSteps': self.maxTimeBetweenSteps
        }


class Phase(PhaseModel):
    '''
    A phase is related to an animal and derived from a phaseModel
    '''

    def __init__(self, phaseModel: PhaseModel, namePhase, numberPhase, percentToSucceed, numberOfLastTrialToSucceed,
                 delayTrials=None, delaySteps=None, numberOfTrialsPerSession = None, maxSessionTime = None, maxTimeBetweenSteps = None):
        PhaseModel.__init__(self, namePhase, numberPhase, percentToSucceed, numberOfLastTrialToSucceed,
                 delayTrials, delaySteps, numberOfTrialsPerSession, maxSessionTime, maxTimeBetweenSteps)

        self.phaseModel = phaseModel
        self.startTime = datetime.now()
        self.endTime: datetime = None
        self.trials = []
        self.sessions = []
        self.success = 0
        self.score = 0
        self.completed = False

        print(f"phase max session time: {self.maxSessionTime}")

    def getCompleted(self):
        return self.completed

    def addSession(self, session):
        self.sessions.append(session)

    def getNbSession(self):
        return len(self.sessions)

    def getSessionFromIndex(self, index: int):
        return self.sessions[index]

    def addTrial(self, trial):
        self.trials.append(trial)

    def getNbTrial(self):
        return len(self.trials)

    def getTrialFromIndex(self, index: int):
        return self.trials[index]

    def getNbSuccess(self):
        return self.success

    def getScore(self):
        return self.score

    def computeScore(self):
        nbOfSuccess = 0
        if len(self.trials) >= self.numberOfLastTrialToSucceed:
            for trial in self.trials[-self.numberOfLastTrialToSucceed:]:
                if trial.result == 'success':
                    nbOfSuccess += 1
            self.score = (nbOfSuccess*100)/self.numberOfLastTrialToSucceed
            if (len(self.trials[-self.numberOfLastTrialToSucceed:]) >= self.numberOfLastTrialToSucceed and self.score >= self.percentToSucceed):
                self.completed = True
        else:
            print("Number of trials less than minimum to compute the score")

    def getDicoConfig(self):
        config = self.phaseModel.getDicoConfig()
        phaseConfig = {
            'startTime': self.startTime,
            'endTime': self.endTime,
            'trials': self.trials,
            'sessions': self.sessions,
            'success': self.success,
            'score': self.score,
            'completed': self.completed
        }
        config.update(phaseConfig)
        return config

    def getDicoConfigForResults(self):
        config = self.phaseModel.getDicoConfig()
        phaseConfig = {
            'startTime': self.startTime.strftime("%d/%m/%Y %H:%M:%S.%f"),
            'endTime': "",
            'success': self.success,
            'score': self.score,
            'completed': self.completed
        }
        if self.endTime:
            phaseConfig['endTime'] = self.endTime.strftime("%d/%m/%Y %H:%M:%S.%f")
        trials = []
        # for trial in self.trials:
        #     trials.append(trial.getTrialVariables())
        # phaseConfig['trials'] = trials
        sessions = []
        for session in self.sessions:
            sessions.append(session.getSessionInfoForResults())
        phaseConfig['sessions'] = sessions
        config.update(phaseConfig)
        return config

    def endsThePhase(self):
        self.endTime = datetime.now()
        self.completed = True
        logging.info(f'[PHASE] Phase {self.namePhase} completed')


    # def doPhase(self, animal, fed, logging, results):
    #     while not self.completed:
    #         fed.lightoff()
    #         time.sleep(0.5)
    #         trial = Trial(fed, logging, self.delayPhases)
    #         print("Trial number %s" %str(len(self.trials)+1))
    #         trialResult = trial.doTrial()
    #         if trialResult == "success":
    #             self.success += 1
    #         self.addTrial(trial)
    #         if len(self.trials) >= self.numberOfLastTrialToSucceed:
    #             self.computeScore()
    #         animal.setSession(self)
    #         animal.setSessionNameFromSession()
    #         animal.setScore(self.score)
    #         print("Animal: %s - Session: %s - Success: %i - Score: %i%% (calculate on %i last trials, 0 if fewer trials)" % (animal.getIdAnimal(), animal.getSessionName(), self.success, animal.getScore(), self.numberOfLastTrialToSucceed))
    #         logging.info('[RES] "Animal: %s - Session: %s - Success: %i - Score: %i%% (calculate on %i last trials, 0 if fewer trials)'  % (animal.getIdAnimal(), animal.getSessionName(), self.success, animal.getScore(), self.numberOfLastTrialToSucceed))
    #         results.saveDataAndExport(animal.getIdAnimal(), self, self.score)
    #         timeT = time.process_time() + self.delayTrials
    #         while time.process_time() <= timeT:
    #             fedt = fed.read()
    #             if fedt != None:
    #                 logging.info('[FED]' + fedt)



class Animal():
    '''
    Information about the animal
    - RFID number
    - current phase
    - score in this current phase
    '''
    def __init__(self, idAnimal: str, rfid=None):
        self.idAnimal = idAnimal
        self.rfid = rfid
        self.currentPhase: Phase = None
        self.currentPhaseName: str = None
        self.currentScore: float = 0
        self.currentSession = None
        self.phaseList = []
        # self.results = {}

    def getIdAnimal(self):
        return self.idAnimal

    def getRIFDAnimal(self):
        return self.rfid

    def setCurrentPhase(self, phase: Phase):
        self.currentPhase = phase

    def setCurrentScore(self, score):
        self.currentScore = score

    def setCurrentPhaseName(self, currentPhaseName: str):
        self.currentPhaseName = currentPhaseName

    def getCurrentPhase(self):
        return self.currentPhase

    def getCurrentPhaseName(self):
        return self.currentPhaseName

    def getCurrentScore(self):
        return self.currentScore

    def setCurrentSession(self, session):
        self.currentSession = session

    def getCurrentSession(self):
        return self.currentSession

    def getPhaseList(self):
        return self.phaseList()

    def addPhaseToPhaseList(self, phase: Phase):
        self.phaseList.append(phase)
        self.setCurrentPhase(phase)
        self.setCurrentPhaseName(phase.getPhaseModelName())

    def loadResults(self, results):
        self.results = results[self.idAnimal]

    def getAnimalInfo(self):
        phaseListDico = {}
        print(str(self.phaseList))
        for phase in self.phaseList:
            print(phase.getPhaseModelName())
            phaseListDico[phase.getPhaseModelName] = phase.getDicoConfig()
        return {
            'idAnimal': self.idAnimal,
            'rfid': self.rfid,
            'currentPhase': self.currentPhase,
            'currentPhaseName': self.currentPhaseName,
            'currentScore': self.currentScore,
            'currentSession': self.currentSession,
            'phaseList': phaseListDico
        }

    def getAnimalInfoForResults(self):
        phaseListDico = {}
        # print(str(self.phaseList))
        for phase in self.phaseList:
            # print(phase.getPhaseModelName())
            phaseListDico[phase.getPhaseModelName] = phase.getDicoConfig()
        currentSession = 0
        if self.currentSession:
            currentSession = self.currentSession.getSessionNumber()
        return {
            'idAnimal': self.idAnimal,
            'rfid': self.rfid,
            'currentPhaseName': self.currentPhaseName,
            'currentScore': self.currentScore,
            'currentSession': currentSession,
            # 'phaseList': phaseListDico
        }

class Results():
    '''
    Results stores the results of each animal during the whole experiment
    results = {
        'experiment': {
            'nameExperiment' = nameExperiment,
            'startTime' = startTime,
            'endTime': endTime,
            'phaseModelList' = [
                {
                    'phaseName': namePhase,
                    'numberPhase': numberPhase,
                    'percentToSucceed': percentToSucceed,
                    'numberOfLastTrialToSucceed': numberOfLastTrialToSucceed,
                    'delayTrials': delayTrials,
                    'delaySteps': delaySteps,
                    'numberOfTrialsPerSession': numberOfTrialsPerSession,
                    'maxSessionTime': maxSessionTime,
                    'maxTimeBetweenSteps': maxTimeBetweenSteps,
                },
                {
                    ...
                }
            ],
            'gateList' = [],
            'animalDico' = {
                animal1RFID: {
                    'idAnimal': idAnimal,
                    'rfid': rfid,
                    'currentPhaseName': currentPhaseName,
                    'currentScore': currentScore,
                    'currentSession': currentSession,
                    'phaseList': [
                        {
                            'phaseName': namePhase,
                            'numberPhase': numberPhase,
                            'percentToSucceed': percentToSucceed,
                            'numberOfLastTrialToSucceed': numberOfLastTrialToSucceed,
                            'delayTrials': delayTrials,
                            'delaySteps': delaySteps,
                            'numberOfTrialsPerSession': numberOfTrialsPerSession,
                            'maxSessionTime': maxSessionTime,
                            'maxTimeBetweenSteps': maxTimeBetweenSteps,
                            'startTime': startTime,
                            'endTime': endTime,
                            'trials': trials,
                            'sessions': [
                                {
                                    'animal': animal,
                                    'gate': gate,
                                    'currentPhase': currentPhase,
                                    'sessionNumber': sessionNumber,
                                    'startTime': startTime,
                                    'endTime': endTime,
                                    'trialList': [
                                        {
                                            'fed': fedName,
                                            'delaySteps': delaySteps ,
                                            'trialCompleted': trialCompleted,
                                            'randomSide': randomSide,
                                            'step1Completed': step1Completed,
                                            'pelletPicked': pelletPicked,
                                            'startTimeStep1': startTimeStep1,
                                            'endTimeStep1': endTimeStep1,
                                            'startTimeStep2': startTimeStep2,
                                            'endTimeStep2': endTimeStep2,
                                            'result': self.result
                                        },
                                        {
                                            ...
                                        }
                                    ],
                                    'thread': thread,
                                    'isProcessing': isProcessing
                                },
                                {
                                    ...
                                }
                            ],
                            'success': success,
                            'score': score,
                            'completed': completed
                        },
                        {
                            ...
                        }
                    ]
                },
                animal2RFID: {
                    ...
                }
            }
        }
    }
    '''
    def __init__(self, experiment):
        self.results = {}
        self.results['experiment'] = {
            'nameExperiment': experiment.getExperiment(),
            'startTime': experiment.getStartTime().strftime("%d-%m-%Y %H-%M-%S-%f"),
            'endTime':  '',
            'phaseModelList': {},
            'gateList': [],
            'animalDico': {}
        }
        self.lock = Lock()

    def getResults(self):
        return self.results

    def addExperimentPhaseModel(self, phaseModel: PhaseModel):
        self.results['experiment']['phaseModelList'][phaseModel.getPhaseModelName()] = phaseModel.getDicoConfig()

    def addExperimentGate(self, gateName: str):
        self.results['experiment']['gateList'].append(gateName)

    def addAnimal(self, animal: Animal):
        animalInfo = animal.getAnimalInfoForResults()
        self.results['experiment']['animalDico'][animal.getRIFDAnimal()] = animalInfo
        self.results['experiment']['animalDico'][animal.getRIFDAnimal()]['phaseList'] = []

    def getAnimalResults(self, animalRFID):
        return self.results['experiment']['animalDico'][animalRFID]

    def addAnimalPhase(self, animalRFID, phase: Phase):
        # check if animal in results
        if animalRFID in self.results.keys():
            phaseInfo = phase.getDicoConfig()
            # check if phase in results[animal][phaseList]
            phaseAlreadyEntered = False
            for phase in self.results[animalRFID]['phaseList']:
                if phaseInfo['namePhase'] in phase:
                    phaseAlreadyEntered = True
                    break
            if not phaseAlreadyEntered:
                self.results[animalRFID]['phaseList'].append(phaseInfo)
            else:
                print(f'{phaseInfo["namePhase"]} already in results for {animalRFID}')
        else:
            print(f'{animalRFID} not in results: please first add this animal')

    def addAnimalPhaseSession(self, animalRFID, phaseName, session):
        sessionInfo = session.getSessionInfo
        # check if animal in results
        if animalRFID in self.results.keys():
            # check if phase in results[animal][phaseList]
            phaseAlreadyEntered = False
            for index, phase in enumerate(self.results[animalRFID]['phaseList']):
                if phaseName in phase['phaseName']:
                    phaseAlreadyEntered = True
                    phase['sessions'].append(sessionInfo)
                    break

            if not phaseAlreadyEntered:
                print(f'{phaseName} not in results for {animalRFID}: please add this phase first')
        else:
            print(f'{animalRFID} not in results: please first add this animal')

    def addAnimalPhaseSessionTrial(self, animalRFID, phaseName, sessionNumber, trial):
        trialInfo = trial.getTrialVariables()
        # check if animal in results
        if animalRFID in self.results.keys():
            # check if phase in results[animal][phaseList]
            phaseAlreadyEntered = False
            for index, phase in enumerate(self.results[animalRFID]['phaseList']):
                if phaseName in phase['phaseName']:
                    phaseAlreadyEnter = True
                    # check if session in results[animal][phaseList][sessions]
                    sessionAlreadyEntered = False
                    for indexSession, session in enumerate(phase['sessions']):
                        if sessionNumber in session['sessionNumber']:
                            sessionAlreadyEntered = True
                            phase['sessions'][indexSession]['trialList'].append(trialInfo)
                            break
                    if not sessionAlreadyEntered:
                        print(f'Session number {sessionNumber} not in results for {animalRFID} and phase {phaseName}: please add this session first')
            if not phaseAlreadyEntered:
                print(f'{phaseName} not in results for {animalRFID}: please add this phase first')
        else:
            print(f'{animalRFID} not in results: please first add this animal')

    def exportToJson(self):
        self.lock.acquire()
        with open(f"{self.results['experiment']['nameExperiment']}_{self.results['experiment']['startTime']}.json", "w") as file:
            json.dump(self.results, file, indent=4)
        self.lock.release()



class Experiment():
    '''
    Compile all information about the experiment:
    - a list of the animals
    - a list of the phaseModel
    '''
    def __init__(self, nameExperiment):
        self.nameExperiment = nameExperiment
        self.startTime = datetime.now()
        self.endTime: datetime
        self.animalDico = {}
        self.phaseModelList = []
        self.gateDico = {}
        self.results = Results(self)


        self.logFile = "experimentLog_"+ datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"
        print("Logfile: ", self.logFile )
        logging.basicConfig(level = logging.INFO, filename = self.logFile, format = '%(asctime)s.%(msecs)03d: %(message)s', datefmt = '%Y-%m-%d %H:%M:%S' )
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logging.info('Application started for ' + self.nameExperiment)


    def initGateMode(self):
        for gate in self.gateDico:
            self.gateDico[gate]['gate'].setOrder(GateOrder.ONLY_ONE_ANIMAL_IN_B)

    def getExperiment(self):
        return self.nameExperiment

    def getStartTime(self):
        return self.startTime

    def getEndTime(self):
        return self.endTime

    def setEndTime(self, endTime: datetime):
        self.endTime = endTime

    def addPhaseModel(self, phaseModel: PhaseModel):
        self.phaseModelList.append(phaseModel)
        self.results.addExperimentPhaseModel(phaseModel)

    def getPhaseModelList(self):
        return self.phaseModelList

    def getPhaseNameList(self):
        phaseNameList = []
        for phase in self.phaseModelList:
            phaseNameList.append(phase.getPhaseModelName())
        return phaseNameList

    def getPhaseModelFromIndex(self, index):
        return self.phaseModelList[index]

    def getPhaseNumberFromPhaseName(self, phaseName: str):
        phaseNumber = 0
        phaseFound = False
        for index, phase in enumerate(self.phaseModelList):
            print(f"loop: {index}")
            if phaseName == phase.getPhaseModelName():
                phaseNumber = index
                phaseFound = True
                break
        if phaseFound:
            return phaseNumber
        else:
            print(f"The phase whose name {phaseName} has not been found")
            return -1

    def getGateDico(self):
        return self.gateList

    def getGateNameList(self):
        gateNameList = []
        for gate in self.gateDico:
            gateNameList.append(gate.name)
        return gateNameList

    def addGate(self, gate: Gate):
        self.gateDico[gate.name] = {'gate': gate}
        self.results.addExperimentGate(gate.name)

    def addFedToGate(self, gateName: str, fed):
        '''
        To link a fed with a gate
        '''
        if 'feds' in self.gateDico[gateName]:
            if fed not in self.gateDico[gateName]['feds']:
                self.gateDico[gateName]['feds'].append(fed)
            else:
                print(f"{fed.name} already linked with {gateName}")
        else:
            self.gateDico[gateName]['feds'] = [fed]

    def getFedsFromGate(self, gateName: str):
        '''
        Return the devices behind the gate
        '''
        return self.gateDico[gateName]['feds']

    def addAnimal(self, animal: Animal):
        self.animalDico[animal.getRIFDAnimal()] = animal
        self.results.addAnimal(animal)

    def getAnimalList(self):
        return self.animalDico.keys()

    def getAnimal(self, rfid):
        return self.animalDico[rfid]

    def createAndAddPhaseModel(self, namePhase, numberPhase, percentToSucceed, numberOfLastTrialToSucceed,
                 delayTrials=None, delaySteps=None, numberOfTrialsPerSession = None, maxSessionTime = None, maxTimeBetweenSteps = None):
        phaseModel = PhaseModel(namePhase, numberPhase, percentToSucceed, numberOfLastTrialToSucceed,
                 delayTrials, delaySteps, numberOfTrialsPerSession, maxSessionTime, maxTimeBetweenSteps)
        self.addPhaseModel(phaseModel)

    def getPhaseModelConfigFromIndex(self, index: int):
        return self.phaseModelList[index].getConfig()


    # def doExperiment(self):
    #     '''
    #     If there is a gate, a listener is waiting for an animal
    #     '''
    #     if self.gateList:
    #         for gate in self.gateList:
    #             gate.close()
    #     else:
    #         pass


class Session():
    '''
    A session is the period where an animal is in the test zone.
    The session could be a gateSession, which is the period between the entry and the exit of an animal though the gate
    '''
    def __init__(self, experiment: Experiment, animal: Animal, gate=None):
        self.experiment = experiment
        self.animal = animal
        self.gate = gate
        self.results = self.experiment.results.results['experiment']['animalDico'][animal.getRIFDAnimal()]
        if animal.getCurrentPhase():
            self.currentPhase = self.animal.getCurrentPhase()
        else:
            self.currentPhase = Phase(experiment.phaseModelList[0].getPhaseModel(), *experiment.getPhaseModelFromIndex(0).getConfig())
            animal.setCurrentPhase(self.currentPhase)
            animal.setCurrentPhaseName(self.currentPhase.getPhaseModelName())
            animal.addPhaseToPhaseList(self.currentPhase)
            self.results['currentPhaseName'] = self.currentPhase.getPhaseModelName()
            self.results['phaseList'].append(self.currentPhase.getDicoConfigForResults())
            self.results['phaseList'][len(self.results['phaseList'])-1]['sessions'].append(self.getSessionInfoForResults())
        self.sessionNumber = animal.getCurrentPhase().getNbSession()+1
        self.results['currentSession'] = self.sessionNumber
        self.startTime = datetime.now()
        self.endTime: datetime = None
        self.trialList = []
        self.isProcessing = True
        # chrono session
        self.event = Event()
        self.thread = Thread(target=self.pingEachSecond, name=f"Thread session", args=("session",))
        self.thread.start()

        # chrono between two trials
        # self.eventBetweenTrials = Event()
        # self.threadBetweenTrials = Thread(target=self.pingEachSecond, name=f"Thread between trials", args=("between trials",))
        self.pauseBetweenTrials = False
        # self.results['phaseList']['sessions'] = self.getSessionInfo()

    def getAnimalSession(self):
        return self.animal

    def getGateSession(self):
        return self.gate

    def getSessionNumber(self):
        return self.sessionNumber

    def setSessionNumber(self, sessionNumber):
        self.sessionNumber = sessionNumber

    def getStartTime(self):
        return self.startTime

    def getEndTime(self):
        return self.endTime

    def setEndTime(self, endTime: datetime):
        self.endTime = endTime

    def getThread(self):
        return self.thread

    def setThread(self, thread):
        self.thread = thread

    def getIsProcessing(self):
        return self.isProcessing

    def phaseManager(self):
        self.currentPhase = self.animal.getCurrentPhase()


    def addOrUpdateSessionInResultsAndSave(self):
        if len(self.results['phaseList'][len(self.results['phaseList'])-1]['sessions']) == self.sessionNumber:
            # update
            self.results['phaseList'][len(self.results['phaseList']) - 1]['sessions'][self.sessionNumber-1] = self.getSessionInfoForResults()
        if len(self.results['phaseList'][len(self.results['phaseList'])-1]['sessions']) < self.sessionNumber:
            # add the session to the results
            self.results['phaseList'][len(self.results['phaseList']) - 1]['sessions'].append(
                self.getSessionInfoForResults())
        self.experiment.results.exportToJson()

    def endsTheSession(self):
        # end the trial
        currentTrial = self.trialList[-1]
        currentTrial.endsTheTrial()
        # end of the session
        self.endTime = datetime.now()
        self.event.set()
        self.isProcessing = False
        self.addOrUpdateSessionInResultsAndSave()
        logging.info('[SESSION] session completed')


    def pingEachSecond(self, name):
        print(f"Name thread: {name}")
        while not self.event.is_set():
            self.deviceListener(DeviceEvent("timer", self, f"TIMER {name}", None))
            time.sleep(1)

    def getSessionInfo(self):
        return {
            'animal': self.animal,
            'gate': self.gate,
            'currentPhase': self.currentPhase,
            'sessionNumber': self.sessionNumber,
            'startTime': self.startTime,
            'endTime': self.endTime,
            'trialList': self.trialList,
            'thread': self.thread,
            'isProcessing': self.isProcessing
        }

    def getSessionInfoForResults(self):
        dicoInfoSession = {
            # 'animal': self.animal.getAnimalInfoForResults(),
            'gate': self.gate.name,
            'currentPhaseName': self.currentPhase.getPhaseModelName(),
            'sessionNumber': self.sessionNumber,
            'startTime': self.startTime.strftime("%d/%m/%Y %H:%M:%S.%f"),
            'endTime': "",
            'isProcessing': self.isProcessing
        }
        if self.endTime:
            dicoInfoSession['endTime'] = self.endTime.strftime("%d/%m/%Y %H:%M:%S.%f")
        trials = []
        for trial in self.trialList:
            trials.append(trial.getTrialVariables())
        dicoInfoSession['trialList'] = trials
        return dicoInfoSession

    def deviceListener(self, event ):
        if "Animal allowed to cross" in event.description:
            # Check if event from same gate and same animal
            gate = event.deviceObject
            rfid = event.data
            if gate == self.gate:
                if rfid == self.animal.getRIFDAnimal():
                    # the same animal is passing the same gate
                    if "SIDE A" in event.description:
                        # animal is going outside the test zone:
                        # end the trial
                        currentTrial = self.trialList[-1]
                        currentTrial.endsTheTrial()
                        # end of the session
                        self.endTime = datetime.now()
                        self.isProcessing = False

        # Chrono
        if "TIMER session" in event.description:
            if self.startTime != None:
                currentTime = datetime.now()
                durationSession = (currentTime - self.startTime).seconds
                # print( f"durationSession : {durationSession} seconds" )
                # print( f"Max session time : {self.currentPhase.getMaxSessionTime()} seconds" )
                if durationSession > self.currentPhase.getMaxSessionTime():
                    # time out: the animal can finish its trial if it is begun. Then it must go outside

                    # self.gate.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True )
                    print(f'Session timeout')
                    logging.info(f'[Session] Session timeout')
                    # self.isProcessing = False
                    self.endsTheSession()

        # if "TIMER between trials" in event.description:
        #     if self.currentPhase.delayTrials:
        #         currentTime = datetime.now()
        #         durationFromLastTrial = (currentTime - self.trialList[-1].endTrial).seconds
        #         if durationFromLastTrial > self.currentPhase.getDelayTrials():
        #             self.pauseBetweenTrials = False
        #             self.eventBetweenTrials.set()


    def doSession(self):
        '''
        Launch trials until the end of the phase or the end of the session (the animal leaves the test zone)
        A listener check if the animal leaves the test zone through the gate
        '''
        if self.gate:
            '''
            This session is a gate session
            The session find the Fed behing the gate
            Listener to check if the animal is leaving the test zone
            '''
            fed = self.experiment.getFedsFromGate(self.gate.name)[0]  # getFedsFromGate returns a list, we take the first item
            while self.isProcessing:
                if (self.currentPhase.getNumberOfTrialsPerSession() and len(self.trialList) < self.currentPhase.getNumberOfTrialsPerSession()) or self.currentPhase.getNumberOfTrialsPerSession()==None:
                    if "habituation" in self.currentPhase.getPhaseModelName():
                        trial = TrialHabituation(fed=fed)
                    else:
                        trial = Trial(fed=fed, delaySteps=self.currentPhase.getDelaySteps(), startTimeStep1=datetime.now(),
                                  maxTimeBetweenSteps=self.currentPhase.getMaxTimeBetweenSteps())
                    self.trialList.append(trial)
                    self.currentPhase.addTrial(trial)
                    trialResult = trial.doTrial()
                    # print(f"len(self.results['phaseList'])-1 = {len(self.results['phaseList'])-1}")
                    # print(f"self.sessionNumber-1 = {self.sessionNumber-1}")
                    self.addOrUpdateSessionInResultsAndSave()
                    # self.results['phaseList'][len(self.results['phaseList'])-1]['sessions'][self.sessionNumber-1]['trialList'].append(trial.getTrialVariables())
                    if trialResult == "success":
                        self.currentPhase.success += 1
                        self.currentPhase.computeScore()
                        self.results['currentScore'] = self.animal.getCurrentScore()

                    self.animal.setCurrentScore(self.currentPhase.getScore())
                    if self.currentPhase.getCompleted():
                        self.endsTheSession()
                else:
                    # numberOfTrialsPerSession reached
                    self.endsTheSession()
                    break
                self.addOrUpdateSessionInResultsAndSave()
                print(self.trialList[-1].endTrial)
                self.pauseBetweenTrials = True
                currentTime = datetime.now()
                durationFromLastTrial = (currentTime - self.trialList[-1].endTrial).seconds
                while durationFromLastTrial < self.currentPhase.getDelayTrials():
                    fedt = fed.read()
                    if fedt != None:
                        logging.info('[FED] Between two trials: ' + fedt)
                    currentTime = datetime.now()
                    durationFromLastTrial = (currentTime - self.trialList[-1].endTrial).seconds

            fed.clickflash()
            time.sleep(0.1)
        else:
            '''
            This session is not a gate session: it will end with the experiment
            '''
            self.trialList.append(Trial(fed=None, logging=None, delaySteps=None, startTimeStep1=datetime.now()))

