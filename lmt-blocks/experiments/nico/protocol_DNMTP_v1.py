'''
Created by Nicolas Torquet at 07/10/2022
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

import time
import random
from datetime import datetime
from blocks.FED3.Fed3Manager import Fed3Manager
import json

sides = {
    'left': {
        'controlLight': 'RGBWdef_R000_G000_B000_W100_SideL',
        'sideToChoose': 'leftIn'
    },
    'right': {
        'controlLight': 'RGBWdef_R000_G000_B000_W100_SideR',
        'sideToChoose': 'rightIn'
    }
}







class Trial():
    def __init__(self, fed=None, logging=None, delayPhases=None, trialCompleted=False, phase1Completed=False, pelletPicked=False, startTimePhase1: datetime = None, endTimePhase1: datetime = None, startTimePhase2: datetime = None, endTimePhase2: datetime = None, result=None):
        self.fed = fed
        self.delayPhases = delayPhases
        self.logging = logging
        self.trialCompleted = trialCompleted
        self.randomSide = random.choice(['left', 'right'])
        self.phase1Completed = phase1Completed
        self.pelletPicked = pelletPicked
        self.startTimePhase1 = startTimePhase1
        self.endTimePhase1 = endTimePhase1
        self.startTimePhase2 = startTimePhase2
        self.endTimePhase2 = endTimePhase2
        self.result = result

    def getTrialVariables(self):
        if self.fed.__class__ == Fed3Manager:
            fed = self.fed.getFedName()
        else:
            fed = self.fed

        if self.startTimePhase2 is None:
            startTimePhase2 = None
        else:
            startTimePhase2 = self.startTimePhase2.strftime("%m/%d/%Y, %H:%M:%S.%f")

        if self.endTimePhase2 is None:
            endTimePhase2 = None
        else:
            endTimePhase2 = self.endTimePhase2.strftime("%m/%d/%Y, %H:%M:%S.%f")

        return {
            'fed': fed,
            'delayPhases': self.delayPhases ,
            # 'logging': self.logging,
            'trialCompleted': self.trialCompleted,
            'randomSide': self.randomSide,
            'phase1Completed': self.phase1Completed,
            'pelletPicked': self.pelletPicked,
            'startTimePhase1': self.startTimePhase1.strftime("%m/%d/%Y, %H:%M:%S.%f"),
            'endTimePhase1': self.endTimePhase1.strftime("%m/%d/%Y, %H:%M:%S.%f"),
            'startTimePhase2': startTimePhase2,
            'endTimePhase2': endTimePhase2,
            'result': self.result
        }


    def phase1(self):
        self.startTimePhase1 = datetime.now()
        while not self.phase1Completed:
            fedRead = self.fed.read()
            if fedRead != None:
                self.fed.lightoff()
                time.sleep(0.5)
                if sides[self.randomSide]['sideToChoose'] in fedRead:
                    self.logging.info('[FED] phase 1 success' + fedRead)
                    self.phase1Completed = True

                else:
                    self.fed.controlLight('RGBWdef_R100_G000_B000_W000_Sideb')
                    time.sleep(0.5)
                    self.fed.lightoff()
                    self.logging.info('[FED] phase 1 error' + fedRead)
                    self.trialCompleted = True
                    self.phase1Completed = True
                    self.startTimePhase2 = None
                    self.endTimePhase2 = None
                self.endTimePhase1 = datetime.now()


    def phase2(self):
        self.startTimePhase2 = datetime.now()
        self.fed.controlLight('RGBWdef_R000_G000_B000_W100_Sideb')
        while not self.trialCompleted:
            fedRead = self.fed.read()
            if fedRead != None:
                self.fed.lightoff()
                time.sleep(0.5)
                if sides[self.randomSide]['sideToChoose'] not in fedRead:
                    self.logging.info('[FED] phase 2 success' + fedRead)
                    self.fed.feed()
                    time.sleep(0.5)
                    while not self.pelletPicked:
                        fedp = self.fed.read()
                        if fedp != None:
                            if 'pellet picked' in fedp:
                                self.logging.info('[FED] ' + fedp)
                                self.pelletPicked = True
                                self.trialCompleted = True
                    self.result = "success"

                else:
                    self.logging.info('[FED] phase 2 error' + fedRead)
                    self.phase1Completed = True
                    self.trialCompleted = True
                    self.result = "error"
                self.endTimePhase2 = datetime.now()


    def doTrial(self):
        self.fed.controlLight(sides[self.randomSide]['controlLight'])
        while not self.trialCompleted:
            self.phase1()
            timeT = time.process_time() + self.delayPhases
            while time.process_time() <= timeT:
                fedt = self.fed.read()
                if fedt != None:
                    self.logging.info('[FED]' + fedt)
            if not self.trialCompleted:
                self.phase2()
                self.trialCompleted = True
            return self.result





class Session():
    def __init__(self, nameSession, numberSession, percentToSucceed, numberOfLastTrialToSucceed, delayPhases, delayTrials):
        # self.animal = animal
        self.nameSession = nameSession
        self.numberSession = numberSession
        self.percentToSucceed = percentToSucceed
        self.numberOfLastTrialToSucceed = numberOfLastTrialToSucceed
        self.delayPhases = delayPhases
        self.delayTrials = delayTrials
        self.trials = []
        self.success = 0
        self.score = 0
        self.completed = False

    def getSession(self):
        return self.nameSession

    def getScore(self):
        return self.score

    def getNumberSession(self):
        return self.numberSession

    def getPercentToSucceed(self):
        return self.percentToSucceed

    def getNumberOfLastTrialToSucceed(self):
        return self.numberOfLastTrialToSucceed

    def getDelayPhases(self):
        return self.delayPhases

    def getDelayTrials(self):
        return self.delayTrials

    def getCompleted(self):
        return self.completed

    def addTrial(self, trial):
        self.trials.append(trial)

    def getNbTrial(self):
        return len(self.trials)

    def getTrialFromNumber(self, number: int):
        return self.trials[number]

    def getNbSuccess(self):
        return self.success

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
            print("Error: number of trials less than minimum")

    def doSession(self, animal, fed, logging, results):
        while not self.completed:
            fed.lightoff()
            time.sleep(0.5)
            trial = Trial(fed, logging, self.delayPhases)
            print("Trial number %s" %str(len(self.trials)+1))
            trialResult = trial.doTrial()
            if trialResult == "success":
                self.success += 1
            self.addTrial(trial)
            if len(self.trials) >= self.numberOfLastTrialToSucceed:
                self.computeScore()
            animal.setSession(self)
            animal.setSessionNameFromSession()
            animal.setScore(self.score)
            print("Animal: %s - Session: %s - Success: %i - Score: %i%% (calculate on %i last trials, 0 if fewer trials)" % (animal.getIdAnimal(), animal.getSessionName(), self.success, animal.getScore(), self.numberOfLastTrialToSucceed))
            logging.info('[RES] "Animal: %s - Session: %s - Success: %i - Score: %i%% (calculate on %i last trials, 0 if fewer trials)'  % (animal.getIdAnimal(), animal.getSessionName(), self.success, animal.getScore(), self.numberOfLastTrialToSucceed))
            results.saveDataAndExport(animal.getIdAnimal(), self, self.score)
            timeT = time.process_time() + self.delayTrials
            while time.process_time() <= timeT:
                fedt = fed.read()
                if fedt != None:
                    logging.info('[FED]' + fedt)






class Experiment():
    def __init__(self, nameExperiment):
        self.nameExperiment = nameExperiment
        # self.animal = animal
        self.sessionList = []
        self.currentSession: Session = None
        self.currentScore: float
        self.results = {}

    def getExperiment(self):
        return self.nameExperiment

    def getCurrentSession(self):
        if self.currentSession:
            return self.currentSession
        else:
            return None

    def setCurrentSession(self, session: Session):
        self.currentSession = session

    def getCurrentScore(self):
        return self.currentScore

    def setCurrentScore(self, score):
        self.currentScore = score

    def addSession(self, session: Session):
        self.sessionList.append(session)

    def getSessionList(self):
        return self.sessionList

    def getSessionFromName(self, sessionName: str):
        for session in self.sessionList:
            if sessionName == session.getSession():
                return session
                break

    def getSessionIndexFromName(self, sessionName: str):
        if sessionName is not None:
            for i in range(0, len(self.sessionList)):
                if sessionName == self.sessionList[i].getSession():
                    return i
                    break
        else:
            return 0

    def doExperiment(self, animal, fed, logging, results):
        print("Experiment %s started" %self.nameExperiment)
        if self.getCurrentSession() != None:
            indexSessionToStart = self.getSessionIndexFromName(self.getCurrentSession().getSession())
        else:
            indexSessionToStart = 0
        for i in range(indexSessionToStart, len(self.sessionList)):
            session = self.sessionList[i]
            print("******* Session %s *******" %session.nameSession)
            session.doSession(animal, fed, logging, results)




class Animal():
    def __init__(self, idAnimal: str, rfid=None):
        self.idAnimal = idAnimal
        self.rfid = rfid
        self.experiment: Experiment = None
        self.session: Session = None
        self.sessionName: str = None
        self.score: float = None
        self.results = {}

    def getIdAnimal(self):
        return self.idAnimal

    def getExperiment(self):
        return self.experiment

    def getExperimentName(self):
        return self.experiment.getExperiment()

    def setExperiment(self, experiment):
        self.experiment = experiment

    def setSession(self, session: Session):
        self.session = session

    def setScore(self, score):
        self.score = score

    def setSessionName(self, sessionName: str):
        self.sessionName = sessionName

    def getSession(self):
        return self.session

    def getSessionName(self):
        return self.sessionName

    def setSessionNameFromSession(self):
        self.sessionName = self.session.getSession()

    def getSessionNameFromSession(self):
        return self.session.getSession()

    def getScore(self):
        return self.score

    def runExperiment(self, fed, logging, results):
        if self.experiment is not None:
            self.experiment.doExperiment(self, fed, logging, results)


    def loadResults(self, results):
        self.results = results[self.idAnimal]





class Results():
    '''
    All the result of an experiment
    '''
    def __init__(self, name: str):
        self.name = name
        self.animals = {}
        self.results = {}

    def addAnimal(self, animal: Animal):
        if animal.getIdAnimal() not in self.animals.keys():
            self.animals[animal.getIdAnimal()] = animal
            self.results[animal.getIdAnimal()] = {
                'currentSession': Session,
                'score': 0,
            }

    def getAnimal(self, idAnimal):
        return self.animals[idAnimal]

    def addSession(self, idAnimal, session: Session):
        self.results[idAnimal][session.getSession()] = session

    def setAnimalCurrentSession(self, idAnimal, session: Session):
        if idAnimal in self.results.keys():
            self.results[idAnimal]['currentSession'] = session
        else:
            print("%s: this animal is not entered into the results" % (idAnimal))

    def getAnimalCurrentSession(self, idAnimal):
        if idAnimal in self.results.keys():
            return self.results[idAnimal]['currentSession']
        else:
            print("%s: this animal is not entered into the results" % (idAnimal))

    def setAnimalScore(self, idAnimal, score: int):
        self.results[idAnimal]['score'] = score

    def getAnimalScore(self, idAnimal: str):
        if idAnimal in self.results.keys():
            return self.results[idAnimal]['score']
        else:
            print("%s: this animal is not entered into the results" % (idAnimal))

    def exportToJson(self):
        resultDico = {}
        for animal in self.results.keys():
            resultDico[animal] = {}
            resultDico[animal][self.getAnimal(animal).getExperimentName()] = {}
            if self.getAnimal(animal).getSession() is not None:
                # print('getSession: '+str(self.getAnimal(animal).getSession()))
                resultDico[animal][self.getAnimal(animal).getExperimentName()]['currentSession'] = self.getAnimal(animal).getSession().getSession()
                resultDico[animal][self.getAnimal(animal).getExperimentName()]['score'] = self.getAnimalScore(animal)
            else:
                resultDico[animal][self.getAnimal(animal).getExperimentName()]['currentSession'] = 'No session started'
                resultDico[animal][self.getAnimal(animal).getExperimentName()]['score'] = 0

            resultDico[animal][self.getAnimal(animal).getExperimentName()]['sessionList'] = []
            indexSessionInList = 0
            for session in self.getAnimal(animal).getExperiment().getSessionList():
                # print('session:'+ session)
                # sessionObject = self.getAnimal(animal).getExperiment().getSessionFromName(session)
                resultDico[animal][self.getAnimal(animal).getExperimentName()]['sessionList'].append({
                    'nameSession': session.getSession(),
                    'numberSession': session.getNumberSession(),
                    'percentToSucceed': session.getPercentToSucceed(),
                    'numberOfLastTrialToSucceed': session.getNumberOfLastTrialToSucceed(),
                    'delayPhases': session.getDelayPhases(),
                    'delayTrials': session.getDelayTrials(),
                    'success': session.getNbSuccess(),
                    'score': session.getScore(),
                    'completed': session.getCompleted(),
                    'trials': []
                })

                for i in range(session.getNbTrial()):
                    resultDico[animal][self.getAnimal(animal).getExperimentName()]['sessionList'][indexSessionInList]['trials'].append(session.getTrialFromNumber(i).getTrialVariables())
                indexSessionInList += 1

        # print(resultDico)
        with open("%s.json" % (self.name), "w") as file:
            json.dump(resultDico, file, indent=4)


    def saveDataAndExport(self, idAnimal, session: Session, score):
        self.addSession(idAnimal, session)
        self.setAnimalCurrentSession(idAnimal, session)
        self.setAnimalScore(idAnimal, score)
        self.exportToJson()

    def loadResults(self, resultFile):
        '''
        Experiment and sessions in resultFile must correspond to those described in the main
        '''
        with open(resultFile) as json_file:
            self.results = json.load(json_file)
        for animal in self.results.keys():
            animalToLoad = self.getAnimal(animal)
            experimentName = animalToLoad.getExperimentName()
            experiment = animalToLoad.getExperiment()
            experiment.setCurrentScore(self.results[animal][experimentName]["score"])
            if self.results[animal][experimentName]["currentSession"] != "No session started":
                experiment.setCurrentSession(experiment.getSessionFromName(self.results[animal][experimentName]["currentSession"]))
            else:
                experiment.setCurrentSession(None)
            animalToLoad.setScore(experiment.getCurrentScore())
            animalToLoad.setSession(experiment.getCurrentSession())
            # Check experiment
            if animalToLoad.getExperimentName() in self.results[animal].keys():
                sessions = self.results[animal][experimentName]['sessionList']
                # print('sessions: '+str(sessions))
                # for session in self.results[animal][self.getAnimal(animal).getExperimentName()].keys():
                for session in sessions:
                    # print(str(session))
                    if animalToLoad.getExperiment().getSessionFromName(session['nameSession']) is not None:
                        sessionToLoad = animalToLoad.getExperiment().getSessionFromName(session['nameSession'])
                        # if session == self.results[animal]['currentSession']:
                        #     self.setAnimalCurrentSession(animal, self.results[animal][self.getAnimal(animal).getExperimentName()][session])
                        # Rebuild trials
                        for previousTrial in session['trials']:
                            # thisSession = self.results[animal][experimentName][session][previousTrial]
                            # print('delayPhases: %s' % (str(thisSession)))
                            trial = Trial(fed=previousTrial['fed'], delayPhases=previousTrial['delayPhases'],
                                          trialCompleted=previousTrial['trialCompleted'], randomSide=previousTrial['randomSide'],
                                          phase1Completed=previousTrial['phase1Completed'], pelletPicked=previousTrial['pelletPicked'],
                                          startTimePhase1=datetime.strptime(previousTrial['startTimePhase1'], "%m/%d/%Y, %H:%M:%S.%f"),
                                          endTimePhase1=datetime.strptime(previousTrial['endTimePhase1'], "%m/%d/%Y, %H:%M:%S.%f"),
                                          startTimePhase2=datetime.strptime(previousTrial['startTimePhase2'], "%m/%d/%Y, %H:%M:%S.%f"),
                                          endTimePhase2=datetime.strptime(previousTrial['endTimePhase2'], "%m/%d/%Y, %H:%M:%S.%f"),
                                          result=previousTrial['result'])
                            sessionToLoad.addTrial(trial)

            else:
                print("The experiment name is not the same in the result file")

            # animalToLoad.setSessionName -> to do