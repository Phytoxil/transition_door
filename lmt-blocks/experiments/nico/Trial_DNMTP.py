'''
Created by Nicolas Torquet at 19/04/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

import time
import random
from datetime import datetime

from blocks.DeviceEvent import DeviceEvent
from blocks.FED3.Fed3Manager3 import Fed3Manager3
import logging
from threading import Thread, Event

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

# TODO
# - remove all the sleep and manage fed with the listener


class Trial():
    '''

    '''
    def __init__(self, fed=None, delaySteps=None, trialCompleted=False, step1Completed=False, pelletPicked=False, startTimeStep1: datetime = None, endTimeStep1: datetime = None,
                 startTimeStep2: datetime = None, endTimeStep2: datetime = None, maxTimeBetweenSteps = None, result=None):
        print("initialize new trial")
        self.fed = fed
        self.fed.lightoff()
        # time.sleep(0.1)
        self.delaySteps = delaySteps
        # self.logging = logging
        self.trialCompleted = trialCompleted
        self.startTrial = datetime.now()
        self.endTrial: datetime = None
        self.randomSide = random.choice(['left', 'right'])
        self.step1Completed = step1Completed
        self.pelletPicked = pelletPicked
        self.startTimeStep1 = startTimeStep1
        self.endTimeStep1 = endTimeStep1
        self.startTimeStep2 = startTimeStep2
        self.endTimeStep2 = endTimeStep2
        self.maxTimeBetweenSteps = maxTimeBetweenSteps
        self.result = result
        self.event = Event()
        self.thread: Thread

    def getTrialVariables(self):
        if self.fed.__class__ == Fed3Manager3:
            fed = self.fed.getFedName()
        else:
            fed = self.fed

        if self.endTimeStep1 is None:
            endTimeStep1 = None
        else:
            endTimeStep1 = self.endTimeStep1.strftime("%d/%m/%Y, %H:%M:%S.%f")

        if self.startTimeStep2 is None:
            startTimeStep2 = None
        else:
            startTimeStep2 = self.startTimeStep2.strftime("%d/%m/%Y, %H:%M:%S.%f")

        if self.endTimeStep2 is None:
            endTimeStep2 = None
        else:
            endTimeStep2 = self.endTimeStep2.strftime("%d/%m/%Y, %H:%M:%S.%f")

        return {
            'fed': fed,
            'delaySteps': self.delaySteps ,
            # 'logging': self.logging,
            'trialCompleted': self.trialCompleted,
            'randomSide': self.randomSide,
            'step1Completed': self.step1Completed,
            'pelletPicked': self.pelletPicked,
            'startTimeStep1': self.startTimeStep1.strftime("%d/%m/%Y, %H:%M:%S.%f"),
            'endTimeStep1': endTimeStep1,
            'startTimeStep2': startTimeStep2,
            'endTimeStep2': endTimeStep2,
            'maxTimeBetweenSteps': self.maxTimeBetweenSteps,
            'result': self.result
        }

    def endsTheTrial(self):
        self.endTrial = datetime.now()
        self.fed.lightoff()
        # time.sleep(0.1)
        self.trialCompleted = True
        logging.info("[TRIAL] Trial completed")
        self.event.set()

    def pingEachSecond(self):
        while not self.event.is_set():
            self.deviceListener(DeviceEvent("timer", self, "TIMER Steps", None))
            time.sleep(1)

    def deviceListener(self , event ):
        if "Animal allowed to cross" in event.description:
            # Check if event from same gate and same animal
            gate = event.deviceObject
            rfid = event.data
            if gate == self.gate:
                if rfid == self.animal.getRIFDAnimal():
                    # the same animal is passing the same gate
                    if "SIDE A" in event.description:
                        # animal is going outside the test zone: end of the session
                        logging.info(f"[TRIAL] Animal {rfid} is exiting the test zone: end of the trial")
                        self.endsTheTrial()

        # Chrono between two steps
        if "TIMER Steps" in event.description:
            if self.maxTimeBetweenSteps != None:
                currentTime = datetime.now()
                durationBetweenSteps = (currentTime - self.startTimeStep2).seconds
                # print(f"durationSteps : {durationBetweenSteps} seconds")
                if durationBetweenSteps > self.maxTimeBetweenSteps:
                    # time out: finish the trial
                    self.endTimeStep2 = currentTime
                    logging.info('[TRIAL] Out of time between the two steps')
                    self.result = "Out of time between the two steps"
                    self.endsTheTrial()

    def step1(self):
        self.startTimeStep1 = datetime.now()
        self.fed.controlLight(sides[self.randomSide]['controlLight'])
        # time.sleep(0.5)
        while not self.step1Completed and not self.trialCompleted:
            fedRead = self.fed.read()
            if fedRead != None:
                self.fed.lightoff()
                # time.sleep(0.5)
                if sides[self.randomSide]['sideToChoose'] in fedRead:
                    logging.info('[FED] Step 1 success' + fedRead)
                    self.step1Completed = True

                else:
                    self.fed.controlLight('RGBWdef_R100_G000_B000_W000_Sideb')
                    # time.sleep(0.1)
                    self.fed.lightoff()
                    logging.info('[FED] Step 1 error' + fedRead)
                    self.trialCompleted = True
                    self.step1Completed = True
                    self.startTimeStep2 = None
                    self.endTimeStep2 = None
                self.endTimeStep1 = datetime.now()



    def step2(self):
        self.startTimeStep2 = datetime.now()
        # start a chrono to stop the trial if time > maxTimeBetweenSteps
        self.thread = Thread(target=self.pingEachSecond, name=f"Thread trial: chrono between two steps")
        self.thread.start()
        self.fed.controlLight('RGBWdef_R000_G000_B000_W100_Sideb')
        while not self.trialCompleted:
            fedRead = self.fed.read()
            if fedRead != None:
                self.fed.lightoff()
                # time.sleep(0.1)
                if sides[self.randomSide]['sideToChoose'] not in fedRead:
                    logging.info('[FED] Step 2 success' + fedRead)
                    self.fed.feed()
                    # time.sleep(0.1)
                    while not self.pelletPicked:
                        fedp = self.fed.read()
                        if fedp != None:
                            if 'pellet picked' in fedp:
                                logging.info('[FED] ' + fedp)
                                self.pelletPicked = True
                                self.trialCompleted = True
                    self.result = "success"

                else:
                    logging.info('[FED] Step 2 error' + fedRead)
                    self.step1Completed = True
                    self.trialCompleted = True
                    self.result = "error"
                self.endTimeStep2 = datetime.now()


    def doTrial(self):
        while not self.trialCompleted:
            self.step1()
            timeT = time.process_time() + self.delaySteps
            while time.process_time() <= timeT:
                fedt = self.fed.read()
                if fedt != None:
                    logging.info('[FED]' + fedt)
            if not self.trialCompleted:
                self.step2()
                self.trialCompleted = True
            self.endsTheTrial()
            return self.result



class TrialHabituationLight():
    '''

    '''
    # def __init__(self, fed=None, delaySteps=None, trialCompleted=False, step1Completed=False, pelletPicked=False, startTimeStep1: datetime = None, endTimeStep1: datetime = None,
    #              startTimeStep2: datetime = None, endTimeStep2: datetime = None, maxTimeBetweenSteps = None, result=None):
    def __init__(self, fed=None, trialCompleted=False, pelletPicked=False, result=None):
        print("initialize new trial")
        self.fed = fed
        self.fed.lightoff()
        # time.sleep(0.1)
        # self.delaySteps = delaySteps
        # self.logging = logging
        self.trialCompleted = trialCompleted
        self.startTrial = datetime.now()
        self.endTrial: datetime = None
        self.randomSide = random.choice(['left', 'right'])
        # self.step1Completed = step1Completed
        self.pelletPicked = pelletPicked
        # self.startTimeStep1 = startTimeStep1
        # self.endTimeStep1 = endTimeStep1
        # self.startTimeStep2 = startTimeStep2
        # self.endTimeStep2 = endTimeStep2
        # self.maxTimeBetweenSteps = maxTimeBetweenSteps
        self.result = result
        self.event = Event()
        self.thread: Thread


    def getTrialVariables(self):
        if self.fed.__class__ == Fed3Manager3:
            fed = self.fed.getFedName()
        else:
            fed = self.fed

        # if self.endTimeStep1 is None:
        #     endTimeStep1 = None
        # else:
        #     endTimeStep1 = self.endTimeStep1.strftime("%m/%d/%Y, %H:%M:%S.%f")

        # if self.startTimeStep2 is None:
        #     startTimeStep2 = None
        # else:
        #     startTimeStep2 = self.startTimeStep2.strftime("%m/%d/%Y, %H:%M:%S.%f")
        #
        # if self.endTimeStep2 is None:
        #     endTimeStep2 = None
        # else:
        #     endTimeStep2 = self.endTimeStep2.strftime("%m/%d/%Y, %H:%M:%S.%f")
        endTrial = None
        if self.endTrial:
            endTrial = self.endTrial.strftime("%d/%m/%Y, %H:%M:%S.%f")

        return {
            'fed': fed,
            # 'delaySteps': self.delaySteps ,
            # 'logging': self.logging,
            'trialCompleted': self.trialCompleted,
            'randomSide': self.randomSide,
            # 'step1Completed': self.step1Completed,
            'pelletPicked': self.pelletPicked,
            'startTrial': self.startTrial.strftime("%d/%m/%Y, %H:%M:%S.%f"),
            'endTrial': endTrial,
            # 'startTimeStep1': self.startTimeStep1.strftime("%m/%d/%Y, %H:%M:%S.%f"),
            # 'endTimeStep1': endTimeStep1,
            # 'startTimeStep2': startTimeStep2,
            # 'endTimeStep2': endTimeStep2,
            # 'maxTimeBetweenSteps': self.maxTimeBetweenSteps,
            'result': self.result
        }

    def endsTheTrial(self):
        self.endTrial = datetime.now()
        self.fed.lightoff()
        # time.sleep(0.1)
        self.trialCompleted = True
        logging.info("[TRIAL Habituation] Trial completed")
        self.event.set()

    def pingEachSecond(self):
        while not self.event.is_set():
            self.deviceListener(DeviceEvent("timer", self, "TIMER Steps", None))
            time.sleep(1)

    def deviceListener(self , event ):
        if "Animal allowed to cross" in event.description:
            # Check if event from same gate and same animal
            gate = event.deviceObject
            rfid = event.data
            if gate == self.gate:
                if rfid == self.animal.getRIFDAnimal():
                    # the same animal is passing the same gate
                    if "SIDE A" in event.description:
                        # animal is going outside the test zone: end of the session
                        logging.info(f"[TRIAL Habituation] Animal {rfid} is exiting the test zone: end of the trial")
                        self.endsTheTrial()

        # Chrono between two steps
        if "TIMER Steps" in event.description:
            if self.maxTimeBetweenSteps != None:
                currentTime = datetime.now()
                durationBetweenSteps = (currentTime - self.startTimeStep2).seconds
                # print(f"durationSteps : {durationBetweenSteps} seconds")
                if durationBetweenSteps > self.maxTimeBetweenSteps:
                    # time out: finish the trial
                    self.endTimeStep2 = currentTime
                    logging.info('[TRIAL Habituation] Out of time between the two steps')
                    self.result = "Out of time between the two steps"
                    self.endsTheTrial()

    def step1(self):
        # self.startTimeStep1 = datetime.now()
        self.fed.controlLight(sides[self.randomSide]['controlLight'])
        # time.sleep(0.5)
        while not self.trialCompleted:
            fedRead = self.fed.read()
            if fedRead != None:
                self.fed.lightoff()
                # time.sleep(0.5)
                if sides[self.randomSide]['sideToChoose'] in fedRead:
                    logging.info('[FED] Step 1 success' + fedRead)
                    self.fed.feed()
                    # time.sleep(0.1)
                    while not self.pelletPicked:
                        fedp = self.fed.read()
                        if fedp != None:
                            if 'pellet picked' in fedp:
                                logging.info('[FED] ' + fedp)
                                self.pelletPicked = True
                                self.trialCompleted = True
                    self.result = "success"
                    # self.step1Completed = True

                else:
                    self.fed.controlLight('RGBWdef_R100_G000_B000_W000_Sideb')
                    # time.sleep(0.1)
                    self.fed.lightoff()
                    logging.info('[FED] Habituation error' + fedRead)
                    self.result = "error"
                    self.trialCompleted = True
                    # self.step1Completed = True
                    # self.startTimeStep2 = None
                    # self.endTimeStep2 = None
                # self.endTimeStep1 = datetime.now()


    def doTrial(self):
        while not self.trialCompleted:
            self.step1()
            self.endsTheTrial()
            return self.result




class TrialHabituation():
    '''

    '''
    # def __init__(self, fed=None, delaySteps=None, trialCompleted=False, step1Completed=False, pelletPicked=False, startTimeStep1: datetime = None, endTimeStep1: datetime = None,
    #              startTimeStep2: datetime = None, endTimeStep2: datetime = None, maxTimeBetweenSteps = None, result=None):
    def __init__(self, fed=None, trialCompleted=False, pelletPicked=False, result=None):
        print("initialize new trial")
        self.fed = fed
        self.fed.lightoff()
        # time.sleep(0.1)
        # self.delaySteps = delaySteps
        # self.logging = logging
        self.trialCompleted = trialCompleted
        self.startTrial = datetime.now()
        self.endTrial: datetime = None
        # self.randomSide = random.choice(['left', 'right'])
        # self.step1Completed = step1Completed
        self.pelletPicked = pelletPicked
        # self.startTimeStep1 = startTimeStep1
        # self.endTimeStep1 = endTimeStep1
        # self.startTimeStep2 = startTimeStep2
        # self.endTimeStep2 = endTimeStep2
        # self.maxTimeBetweenSteps = maxTimeBetweenSteps
        self.result = result
        self.event = Event()
        self.thread: Thread


    def getTrialVariables(self):
        if self.fed.__class__ == Fed3Manager3:
            fed = self.fed.getFedName()
        else:
            fed = self.fed

        # if self.endTimeStep1 is None:
        #     endTimeStep1 = None
        # else:
        #     endTimeStep1 = self.endTimeStep1.strftime("%m/%d/%Y, %H:%M:%S.%f")

        # if self.startTimeStep2 is None:
        #     startTimeStep2 = None
        # else:
        #     startTimeStep2 = self.startTimeStep2.strftime("%m/%d/%Y, %H:%M:%S.%f")
        #
        # if self.endTimeStep2 is None:
        #     endTimeStep2 = None
        # else:
        #     endTimeStep2 = self.endTimeStep2.strftime("%m/%d/%Y, %H:%M:%S.%f")
        endTrial = None
        if self.endTrial:
            endTrial = self.endTrial.strftime("%d/%m/%Y, %H:%M:%S.%f")

        return {
            'fed': fed,
            # 'delaySteps': self.delaySteps ,
            # 'logging': self.logging,
            'trialCompleted': self.trialCompleted,
            # 'randomSide': self.randomSide,
            # 'step1Completed': self.step1Completed,
            'pelletPicked': self.pelletPicked,
            'startTrial': self.startTrial.strftime("%d/%m/%Y, %H:%M:%S.%f"),
            'endTrial': endTrial,
            # 'startTimeStep1': self.startTimeStep1.strftime("%m/%d/%Y, %H:%M:%S.%f"),
            # 'endTimeStep1': endTimeStep1,
            # 'startTimeStep2': startTimeStep2,
            # 'endTimeStep2': endTimeStep2,
            # 'maxTimeBetweenSteps': self.maxTimeBetweenSteps,
            'result': self.result
        }

    def endsTheTrial(self):
        self.endTrial = datetime.now()
        self.fed.lightoff()
        # time.sleep(0.1)
        self.trialCompleted = True
        logging.info("[TRIAL Habituation] Trial completed")
        self.event.set()

    def pingEachSecond(self):
        while not self.event.is_set():
            self.deviceListener(DeviceEvent("timer", self, "TIMER Steps", None))
            time.sleep(1)

    def deviceListener(self , event ):
        if "Animal allowed to cross" in event.description:
            # Check if event from same gate and same animal
            gate = event.deviceObject
            rfid = event.data
            if gate == self.gate:
                if rfid == self.animal.getRIFDAnimal():
                    # the same animal is passing the same gate
                    if "SIDE A" in event.description:
                        # animal is going outside the test zone: end of the session
                        logging.info(f"[TRIAL Habituation] Animal {rfid} is exiting the test zone: end of the trial")
                        self.endsTheTrial()

        # Chrono between two steps
        # if "TIMER Steps" in event.description:
        #     if self.maxTimeBetweenSteps != None:
        #         currentTime = datetime.now()
        #         durationBetweenSteps = (currentTime - self.startTimeStep2).seconds
        #         # print(f"durationSteps : {durationBetweenSteps} seconds")
        #         if durationBetweenSteps > self.maxTimeBetweenSteps:
        #             # time out: finish the trial
        #             self.endTimeStep2 = currentTime
        #             logging.info('[TRIAL Habituation] Out of time between the two steps')
        #             self.result = "Out of time between the two steps"
        #             self.endsTheTrial()

    def step1(self):
        # self.startTimeStep1 = datetime.now()
        # self.fed.controlLight(sides[self.randomSide]['controlLight'])
        # time.sleep(0.5)
        while not self.trialCompleted:
            fedRead = self.fed.read()
            if fedRead != None:
                # self.fed.lightoff()
                # time.sleep(0.5)
                # if sides[self.randomSide]['sideToChoose'] in fedRead:
                logging.info('[FED] Step 1 nose poke ' + fedRead)
                self.fed.feed()
                # time.sleep(0.1)
                while not self.pelletPicked:
                    fedp = self.fed.read()
                    if fedp != None:
                        if 'pellet picked' in fedp:
                            logging.info('[FED] ' + fedp)
                            self.pelletPicked = True
                            self.trialCompleted = True
                self.result = "success"
                    # self.step1Completed = True

                # else:
                #     self.fed.controlLight('RGBWdef_R100_G000_B000_W000_Sideb')
                #     time.sleep(0.1)
                #     self.fed.lightoff()
                #     logging.info('[FED] Habituation error' + fedRead)
                #     self.result = "error"
                #     self.trialCompleted = True
                    # self.step1Completed = True
                    # self.startTimeStep2 = None
                    # self.endTimeStep2 = None
                # self.endTimeStep1 = datetime.now()


    def doTrial(self):
        while not self.trialCompleted:
            self.step1()
            self.endsTheTrial()
            return self.result



class TrialTest(TrialHabituation):
    def __init__(self, fed=None, trialCompleted=False, pelletPicked=False, result=None):
        TrialHabituation.__init__(self, fed=fed, trialCompleted=trialCompleted, pelletPicked=pelletPicked, result=result)

    def deviceListener(self, event):
        if "nose poke" in event.description:
            if "right" in event.data:
                print('right')
                self.fed.click()
                logging.info('[FED] nose poke in the right side')
            if "left" in event.data:
                print('left')
                logging.info('[FED] nose poke in the left side')
                self.fed.light()


    def step1(self):
        # self.startTimeStep1 = datetime.now()
        # self.fed.controlLight(sides[self.randomSide]['controlLight'])
        # time.sleep(0.5)
        while not self.trialCompleted:
            fedRead = self.fed.read()
            if fedRead != None:
                # self.fed.lightoff()
                # time.sleep(0.5)
                # if sides[self.randomSide]['sideToChoose'] in fedRead:
                logging.info('[FED] Step 1 nose poke ' + fedRead)
                self.fed.light()
                # time.sleep(0.1)
                while not self.pelletPicked:
                    fedp = self.fed.read()
                    if fedp != None:
                        if 'pellet picked' in fedp:
                            logging.info('[FED] ' + fedp)
                            self.pelletPicked = True
                            self.trialCompleted = True
                self.result = "success"




class StepModel():
    '''
    Superclass to define a generic step of a trial
    '''
    def __init__(self, stepName=None, stepNumber=None, fed=None, startStep=datetime.now(), maxTime=None):
        self.stepName = stepName
        self.stepNumber = stepNumber
        self.fed = fed
        self.startStep = startStep
        self.endStep: datetime = None
        self.stepCompleted = False
        self.result = None
        self.eventList = []
        self.maxTime = maxTime
        self.event = Event()
        self.thread: Thread
        self.fed.addDeviceListener(self.deviceListener)
        logging.info(f"[Step] New step initialized {self.stepName} {self.stepNumber}")


    def getStepVariables(self):
        if self.fed.__class__ == Fed3Manager3:
            fed = self.fed.getFedName()
        else:
            fed = self.fed

        if self.endStep is None:
            endStep = None
        else:
            endStep = self.endStep.strftime("%d/%m/%Y, %H:%M:%S.%f")

        return {
            'stepName': self.stepName,
            'stepNumber': self.stepNumber,
            'fed': fed,
            'stepCompleted': self.stepCompleted,
            'startStep': self.startTrial.strftime("%d/%m/%Y, %H:%M:%S.%f"),
            'endStep': endStep,
            'eventList': self.eventList,
            'result': self.result
        }


    def pingEachSecond(self):
        '''
        Timer
        '''
        while not self.event.is_set():
            self.deviceListener(DeviceEvent("timer", self, "TIMER Steps", None))
            time.sleep(1)

    def actionToDo(self, side):
        '''
        action to do from a listened event
        '''
        self.result = f"{datetime.now()}: nose poke {side}"
        self.fed.click()
        time.sleep(0.05)
        self.endTheStep()


    def deviceListener(self, event):
        if "nose poke" in event.description:
            if "right" in event.data:
                logging.info('[FED] nose poke in the right side')
                self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Nose poke in the right side'))
                self.actionToDo("right")
            if "left" in event.data:
                logging.info('[FED] nose poke in the left side')
                self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Nose poke in the left side'))
                self.actionToDo("left")

        if "feed" in event.description:
            logging.info('[FED] feed')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Feed'))

        if "click" in event.description:
            logging.info('[FED] click')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Click'))

        if "light" in event.description and not "lightoff" in event.description:
            logging.info(f'[FED] {event.data}')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), f'[FED] {event.data}'))

        if "pellet delivered" in event.description:
            logging.info('[FED] Pellet delivered')
            self.pelletPicked = True
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Pellet delivered'))

        if "pellet already delivered" in event.description:
            logging.info('[FED] Pellet already delivered')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Pellet already delivered'))

        if "pellet picked" in event.description:
            logging.info('[FED] Pellet picked')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Pellet picked'))

        if "feed timeout" in event.description:
            logging.info('[FED] Feed timeout')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Feed timeout'))

        # chrono
        if "TIMER session" in event.description:
            if self.maxTime != None and self.startTime != None:
                currentTime = datetime.now()
                duration = (currentTime - self.startTime).seconds
                if duration > self.maxTime:
                    self.result = "timeout"
                    print(f'Step timeout')
                    logging.info(f'[Step] Step timeout')
                    self.endTheStep()


    def endTheStep(self):
        self.endStep = datetime.now()
        self.fed.lightoff()
        time.sleep(0.05)
        logging.info("[Step] Step completed")
        self.event.set()
        self.fed.removeDeviceListener(self.deviceListener)
        self.stepCompleted = True


class Step1DNMTP(StepModel):
    def __init__(self, stepName=None, stepNumber=None, fed=None, startStep=datetime.now()):
        StepModel.__init__(self, stepName, stepNumber, fed, startStep)
        self.randomSide = random.choice(['left', 'right'])
        self.fed.controlLight(sides[self.randomSide]['controlLight'])
        time.sleep(0.05)


    def actionToDo(self, side):
        '''
        action to do from a listened event
        '''
        self.fed.lightoff()
        time.sleep(0.05)
        if side == self.randomSide:
            self.fed.feed()
            time.sleep(0.05)
            self.result = "success"
        if side != self.randomSide:
            self.result = "error"
        self.endTheStep()



class Step2DNMTP(StepModel):
    def __init__(self, stepName=None, stepNumber=None, fed=None, startStep=datetime.now(), sideStep1=None):
        StepModel.__init__(self, stepName, stepNumber, fed, startStep)
        self.sideStep1 = sideStep1
        self.fed.controlLight('RGBWdef_R000_G000_B000_W100_Sideb')
        time.sleep(0.05)


    def actionToDo(self, side):
        '''
        action to do from a listened event
        '''
        self.fed.lightoff()
        time.sleep(0.05)
        if side != self.sideStep1:
            self.fed.feed()
            time.sleep(0.05)
            self.result = "success"
        if side == self.sideStep1:
            self.result = "error"
        self.endTheStep()


class TrialModel():
    '''
    Superclass to define the most used function during a trial
    '''

    def __init__(self, fed=None, trialCompleted=False, result=None):
        self.fed = fed
        self.startTrial = datetime.now()
        self.endTrial: datetime = None
        self.pelletPicked = False
        self.trialCompleted = trialCompleted
        self.result = result
        self.eventList = []
        self.event = Event()
        self.thread: Thread
        self.stepList = []
        self.fed.addDeviceListener(self.deviceListener)
        logging.info("[TRIAL] New trial initialized")


    def pingEachSecond(self):
        '''
        Timer
        '''
        while not self.event.is_set():
            self.deviceListener(DeviceEvent("timer", self, "TIMER Steps", None))
            time.sleep(1)

    def addStep(self, step):
        self.stepList.append(step)

    def endTheTrial(self):
        self.endTrial = datetime.now()
        self.fed.lightoff()
        time.sleep(0.05)
        logging.info("[TRIAL] Trial completed")
        self.event.set()
        self.fed.removeDeviceListener(self.deviceListener)
        self.trialCompleted = True

    def getTrialVariables(self):
        if self.fed.__class__ == Fed3Manager3:
            fed = self.fed.getFedName()
        else:
            fed = self.fed

        if self.endTrial is None:
            endTrial = None
        else:
            endTrial = self.endTrial.strftime("%d/%m/%Y, %H:%M:%S.%f")

        return {
            'fed': fed,
            'trialCompleted': self.trialCompleted,
            'startTrial': self.startTrial.strftime("%d/%m/%Y, %H:%M:%S.%f"),
            'endTrial': endTrial,
            'eventList': self.eventList,
            'pelletPicked': self.pelletPicked,
            'result': self.result
        }

    def actionToDo(self, side):
        '''
        action to do from a listened event
        '''
        self.result = f"{datetime.now()}: nose poke {side}"
        self.fed.click()
        time.sleep(0.05)
        self.endTheTrial()


    def deviceListener(self, event):
        if "nose poke" in event.description:
            if "right" in event.data:
                logging.info('[FED] nose poke in the right side')
                self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Nose poke in the right side'))
                self.actionToDo("right")
            if "left" in event.data:
                logging.info('[FED] nose poke in the left side')
                self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Nose poke in the left side'))
                self.actionToDo("left")

        if "feed" in event.description:
            logging.info('[FED] feed')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Feed'))

        if "click" in event.description:
            logging.info('[FED] click')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Click'))

        if "light" in event.description and not "lightoff" in event.description:
            logging.info(f'[FED] {event.data}')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), f'[FED] {event.data}'))

        if "pellet delivered" in event.description:
            logging.info('[FED] Pellet delivered')
            self.pelletPicked = True
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Pellet delivered'))

        if "pellet already delivered" in event.description:
            logging.info('[FED] Pellet already delivered')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Pellet already delivered'))

        if "pellet picked" in event.description:
            logging.info('[FED] Pellet picked')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Pellet picked'))

        if "feed timeout" in event.description:
            logging.info('[FED] Feed timeout')
            self.eventList.append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f"), '[FED] Feed timeout'))


class TrialHabituation(TrialModel):
    '''
    TrialHabituation derived from TrialModel
    One pellet is delivered for each nosepoke.
    '''
    def __init__(self, fed=None, trialCompleted=False, result=None):
        TrialModel.__init__(self, fed, trialCompleted, result)
        self.fed.lightoff()
        time.sleep(0.05)


    def actionToDo(self, side):
        self.result = f"{datetime.now()}: nose poke {side}"
        self.fed.feed()
        time.sleep(0.05)
        self.endTheTrial()



class TrialHabituationLight(TrialModel):
    '''
    TrialHabituation derived from TrialModel
    One pellet is delivered for each nosepoke done to the light side.
    '''
    def __init__(self, fed=None, trialCompleted=False, result=None):
        TrialModel.__init__(self, fed, trialCompleted, result)
        self.fed.lightoff()
        time.sleep(0.05)
        self.randomSide = random.choice(['left', 'right'])
        self.fed.controlLight(sides[self.randomSide]['controlLight'])
        time.sleep(0.05)


    def actionToDo(self, side):
        # self.result = f"{datetime.now()}: nose poke {side}"
        self.fed.lightoff()
        time.sleep(0.05)
        if side == self.randomSide:
            self.fed.feed()
            time.sleep(0.05)
            self.result = "success"
        if side != self.randomSide:
            self.result = "error"

        self.endTheTrial()



class TrialDNMTP(TrialModel):
    '''
    TrialHabituation derived from TrialModel
    One pellet is delivered for each nosepoke done to the light side.
    '''
    def __init__(self, fed=None, trialCompleted=False, result=None, delaySteps=None, maxTimeBetweenSteps = None):
        TrialModel.__init__(self, fed, trialCompleted, result)
        self.fed.lightoff()
        time.sleep(0.05)
        self.delaySteps = delaySteps
        self.maxTimeBetweenSteps = maxTimeBetweenSteps
        self.addStep(Step1DNMTP())
        self.addStep(Step2DNMTP())


