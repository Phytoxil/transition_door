'''
Created on 6 juil. 2022

@author: Fab
'''

import datetime as dt
import re

class LogAnalyser(object):
    


    
    def __init__(self, logFile ):
        
        self.plines = [] # current phase log lines
        
        self.log(f"Reading log file {logFile}...")
        self.logFile = logFile
        with open( logFile ) as f:
            rawlines = f.readlines()
        
        self.lines = []
        for line in rawlines:
            # remove non-timestamped line:
            try:
                self.getDateTime( line )
                self.lines.append( line.strip().lower() )
            except:
                #print("No timestamp on line: " , line )
                pass
            
        for line in self.lines:
            if "experiment created:" in line:
                self.experimentName = line.split(":")[-1].strip()
                break
        
        self.initialNosepokedirection = None
        for line in self.lines:
            if "Initial Nose poke direction".lower() in line:
                print( line )
                self.initialNosepokedirection = line.split(":")[-1].strip()
                break

        

        
        self.setAnalysisPhase( None )
        
        
        self.log( f"Start time: {self.startTime}" )
        self.log( f"End time: {self.endTime}" )
        self.log("read ok.")
    
    
    def getGenotype(self):
        name = self.experimentName.lower()
        if "wt" in name:
            return "WT"
        if "het" in name:
            return "HET"
        if "ko" in name:
            return "KO"
        return None
    
    def getSex(self):
        name = self.experimentName.lower()
        if "mal" in name:
            return "male"
        
        if "fem" in name:
            return "female"
        return None
    
    def getAge(self):
        name = self.experimentName.lower()
        if "8m" in name:
            return 4*8
        if "12w" in name:
            return 12
        return None
        
        
    def getPhaseDurationS(self ):
                
        startTime = self.getDateTime( self.plines[0] )
        endTime = self.getDateTime( self.plines[-1] )
        return (endTime - startTime).total_seconds()
        
    def getNbEnter(self, name ):
        
        nbEnter = 0
        for line in self.plines:
            #if "LOG ANIMAL IS IN SIDE B"
            '''
            if "nose poke" in line and "correct" in line and name in line:
                nbEnter+=1
            '''
            
            
            if "[logic]" in line and "animal back in side a" in line and name in line:
                nbEnter+=1
            
        return nbEnter
    
    
    def getNosePokeWrongCorrect( self, name ):
        
        nbWrong = 0
        nbCorrect = 0
        nbCancelTimeOut = 0
        nbCancelOther = 0
        
        for line in self.plines:
            if "nose poke "+name+ " correct" in line:                
                print( line )
                nbCorrect+=1
                     
            if "nose poke "+name+ " wrong" in line:
                print( line )            
                nbWrong+=1

            if "nose poke "+name+ " cancel timeout" in line:
                print( line )            
                nbCancelTimeOut+=1
                
            if "nose poke "+name+ " cancel other nose poke" in line:
                print( line )
                nbCancelOther+=1
        
                    
        
        
        return nbWrong,nbCorrect,nbCancelTimeOut, nbCancelOther
        
        #nose poke sugar cancel timeout
        #nose poke sugar cancel other nose poke
        
    
    
    def getJamReport(self , file=None ):
        
        errors = {}
        for line in self.plines:
            line = line[24:]            
            if "DoorStatus.JAMMED".lower() in line:
                if line not in errors:
                    errors[line] = 0
                errors[line] +=1
                #print(line)
        for k,v in errors.items():
            print(k,"\t",v)
            
        if file != None:
            with open( file, 'w+') as f:
                for k,v in errors.items():
                    f.write( f"{k} \t {v}\n" )
            
    
    def getTimeInArea(self, name ):
        
        name = name.lower()
        durationList = []
        
        time = None
        for line in self.plines:
            
            if "[tracelogic][" in line and "log animal is in side b" in line and name in line:
                print( line )
                time = self.getDateTime( line )
                
            if "[logic]" in line and "animal back in side a" in line and name in line:
                print( line )
                if time!=None:
                    durationList.append( ( self.getDateTime( line ) - time ).total_seconds() )
        
        return durationList
    
    def getNbTimeOut(self,name):
        
        name = name.lower()
        nb = 0        
        for line in self.plines:
            if "deviceevent" in line:
                continue
            if "timeout" in line and name in line:
                
                nb+=1
        return nb
    
    def getNbRawPoke(self,name):
        
        name = name.lower()
        nbLeft = 0
        nbRight = 0
                
        for line in self.plines:
            if name in line:
                if "*nose poke*left" in line:
                    nbLeft+=1
                    print( line )
                if "*nose poke*right" in line:
                    nbRight+=1
                    print( line )
        
        
        #if "PHASE6" in self.currentPhase:
        #    quit()
            
            
        return nbLeft, nbRight
        
    
    def getTimeToEnterArea(self, name ):
        
        print("---")
        name = name.lower()
        durationList = []
        times = []
                
        time = None
        for line in self.plines:
            
            if "number" in line or "deviceevent" in line or "validated" in line:
                continue
            # [TraceLogic][social gate][000] START: CLOSE DOOR_B
            
            if "nose poke" in line and name in line:
                print( line )
                time = self.getDateTime( line )
                
            if "[tracelogic][" in line and "log animal is in side b" in line and name in line:
                print( line )
                if time!=None:
                    duration = ( self.getDateTime( line ) - time ).total_seconds()                    
                    durationList.append( duration )
                    times.append( (time-self.startPhase).total_seconds() )
                    print(f"Duration:{duration}")
        print( durationList )
        
        '''
        if "PHASE4" in self.currentPhase:
            quit()
        '''
        
        
        return times, durationList

    def getPhaseNosePoke(self ):

        times = []
        nbLeftSocial = 0
        nbRightSocial = 0
        nbLeftSugar = 0
        nbRightSugar = 0
        
        left_sugars = []
        right_sugars = []
        left_socials = []
        right_socials = []
        
        for line in self.plines:
            
            used = False
            if "*socialFed*nose poke*left".lower() in line:
                nbLeftSocial+=1
                used = True
            
            if "*socialFed*nose poke*right".lower() in line:
                nbRightSocial+=1
                used = True
                
            if "*sugarFed*nose poke*left".lower() in line:
                nbLeftSugar+=1
                used = True
            
            if "*sugarFed*nose poke*right".lower() in line:
                nbRightSugar+=1
                used = True
                
            if used:
                time = self.getDateTime( line )
                s = re.split("[, ()]+", line )
                                                
                times.append( (time-self.startPhase).total_seconds() )
                left_sugars.append( nbLeftSugar )
                right_sugars.append( nbRightSugar )
                left_socials.append( nbLeftSocial )
                right_socials.append( nbRightSocial )
                
        return times, left_sugars, right_sugars, left_socials, right_socials
        
    def trimAll(self, realTime ):
        
        lineNumber = 0
        for line in self.lines:
            rt = self.getDateTime( line )
            lineNumber+=1
            if rt > realTime:
                break
        
        # keep only first lines
        self.lines = self.lines[0:lineNumber]
                

    def getRatioProgress(self, phase, nbValues ):
        
        self.setAnalysisPhase( phase )
        #Phase.PHASE3 : sugar: (1, 1) social: (1, 0)
        
        times = []
        realTimes=[]
        ratios = []
        nbValuesList = []
        read = []        
        
        for line in self.plines:
            
            update = False
            if "social nose poke validated in".lower() in line:
                read.append("social TRUE")
                update = True

            if "social wrong".lower() in line:
                read.append("social FALSE")
                update = True

            if "sugar nose poke validated in".lower() in line:
                read.append("sugar TRUE")
                update = True

            if "sugar wrong".lower() in line:
                read.append("sugar FALSE")
                update = True

            if update:
                
                nbOk = 0
                for v in read[-nbValues:]:
                    if "TRUE" in v:
                        nbOk+=1
                        
                ratios.append( nbOk )
                time = self.getDateTime( line )
                realTimes.append( time )
                times.append( (time-self.startPhase).total_seconds() )
                nbValuesList.append( len ( read ) )
                #print( time, line )
                print( len( read) , nbOk , time, read[-nbValues:] )
        
        
        '''
        if "PHASE5" in phase:
            quit()
        '''
        
        
                
        return times, ratios, nbValuesList,realTimes

    def getMouseLocationVersusTime( self, phase ):
        
        # 1: social location
        # 0: central location
        # -1: sucrose location
        
        print( "----------------------- getMouseLocationVersusTime")
        
        times = []
        values = []
        previous = None
        self.setAnalysisPhase(phase)
        
        
        totalSocial = 0
        totalSugar = 0
        
        for line in self.plines:
            
            
            if "*[tracelogic][" in line and "log animal is in side b" in line and "social" in line:
                print( line )
                times.append( (self.getDateTime( line )-self.startPhase).total_seconds() )
                values.append( 0 )
                times.append( (self.getDateTime( line )-self.startPhase).total_seconds() )
                values.append( 1 )                
                previous = 1

            if "*[tracelogic][" in line and "log animal is in side b" in line and "sugar" in line:
                print( line )
                times.append( (self.getDateTime( line )-self.startPhase).total_seconds() )
                values.append( 0 )
                times.append( (self.getDateTime( line )-self.startPhase).total_seconds() )
                values.append( -1 )
                previous = -1
                
            if "[logic]" in line and "animal back in side a" in line:
                print( line )
                # sum of time
                if previous == 1:
                    previousTime = times[-1]
                    currentTime = (self.getDateTime( line )-self.startPhase).total_seconds()
                    duration=currentTime-previousTime
                    totalSocial+= duration
                    print(f"social duration: {duration}")
                
                if previous == -1:
                    previousTime = times[-1]
                    currentTime = (self.getDateTime( line )-self.startPhase).total_seconds()
                    duration=currentTime-previousTime
                    totalSugar+= duration
                    print(f"sugar duration: {duration}")
                
                # graph
                if previous != None:
                    times.append( (self.getDateTime( line )-self.startPhase).total_seconds() )
                    values.append( previous )
                times.append( (self.getDateTime( line )-self.startPhase).total_seconds() )
                values.append( 0 )
                
            
        return times, values, totalSocial, totalSugar
        
        
    def getRatioProgressPhase3(self ):
        
        #Phase.PHASE3 : sugar: (1, 1) social: (1, 0)
        
        times = []
        sugars = []
        socials = []
        
        for line in self.plines:
            if "phase.phase3 : sugar:" in line:
                #print( line )
                time = self.getDateTime( line )
                s = re.split("[, ()]+", line )
                sugarOk = int(s[-6])
                sugarWrong = int(s[-5])
                socialOk = int(s[-3])
                socialWrong = int(s[-2])
                
                times.append( (time-self.startPhase).total_seconds() )
                sugars.append( sugarOk )
                socials.append( socialOk )
                
        return times, socials, sugars
                
                
    def getProgressPhase4(self ):
        
        # Nose poke progressive SUGAR : 3 / 5
        
        times = []
        sugars = []
        socials = []
        step_sugars = []
        step_socials = []
        
        step_sugar = 0
        step_social = 0
        sugar = 0
        social = 0
        time = 0
        
        for line in self.plines:
            addToData = False
            
            if "nose poke progressive sugar" in line:
                print( line )
                time = self.getDateTime( line )
                
                s = line.split(" ")
                sugar = int( s[-3] )
                step_sugar = int ( s[-1] )
                
                addToData = True
                
            if "nose poke progressive social" in line:
                print( line )
                time = self.getDateTime( line )
                
                s = line.split(" ")
                social = int( s[-3] )
                step_social = int ( s[-1] )
                
                addToData = True
        
            if addToData:        
                times.append( (time-self.startPhase).total_seconds() )
                sugars.append( sugar )
                socials.append( social )
                step_sugars.append( step_sugar )
                step_socials.append( step_social )
        
        self.progressiveRatioAtEnd = f"(current/step): sugar: {sugar}/{step_sugar} social: {social}/{step_social}"        
                
        return times, socials, sugars, step_socials, step_sugars
        
    
    def getCumulatedPhase4(self ):
        
        times = []
        
        socialRs = []
        socialLs = []
        sugarRs = []
        sugarLs = []
        
        socialR = 0
        socialL = 0
        sugarR = 0
        sugarL = 0
               
        time = 0
        
        print("----------------------------------------")
        for line in self.plines:
            addToData = False
            
            print( line )
            if "deviceevent *fed3*<class 'blocks.fed3.fed3manager.fed3manager'>*sugarfed" in line:
                if "right" in line:
                    sugarR +=1
                if "left" in line:
                    sugarL +=1
                addToData = True

            if "deviceevent *fed3*<class 'blocks.fed3.fed3manager.fed3manager'>*socialfed*nose poke" in line:
                if "right" in line:
                    socialR +=1
                if "left" in line:
                    socialL +=1
                addToData = True        
                                
            if addToData:     
                time = self.getDateTime( line )   
                times.append( (time-self.startPhase).total_seconds() )
                socialRs.append( socialR )
                socialLs.append( socialL )
                sugarRs.append( sugarR )
                sugarLs.append( sugarL )
                        
        return times, socialRs, socialLs, sugarRs, sugarLs
        
    
    
    def setAnalysisPhase(self, phase ):
        
        self.currentPhase = phase
        self.plines =[]
        
        if phase == None:
            self.log("Set current phase: all")
            self.plines = []
            for line in self.lines:
                self.plines.append( line )
                self.startTime = self.getDateTime( self.lines[0] )
                self.endTime = self.getDateTime( self.lines[-1] )
                self.startPhase = None
                self.endPhase = None
            return
            
        phase = phase.lower()
        phaseStarted = False
        for line in self.lines:
            
            if "starting phase" in line and phase in line:                
                phaseStarted = True
                self.startPhase = self.getDateTime( line )
                 
            if phaseStarted == True:
                if "starting phase" in line and not phase in line:
                    return
                
            if phaseStarted:
                self.plines.append( line )                
                self.endPhase = self.getDateTime( line )
                
            
    def printCurrentPhase(self):
        for line in self.plines:
            print ( line )
    
    def getDateTime(self , line ):        
        datetime = line[0:23]
        datetime = dt.datetime.strptime(datetime,'%Y-%m-%d %H:%M:%S.%f')
        return datetime
    
    def log(self, txt):
        print(f"[Analysis]{txt}")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    