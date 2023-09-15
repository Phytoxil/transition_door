'''
Created on 16 mars 2022

@author: Fab
'''

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import itertools
import numpy
from gevent.libev.corecext import NONE
from experiments.sugarsocial.analysis.LogAnalyser import LogAnalyser
import random
from matplotlib.ticker import FuncFormatter, MultipleLocator
import datetime
    
def jitter( value , l ):
    ll =[]
    for i in range( len(l) ):
        ll.append( value+ (random.random()-0.5)*0.4 )
    return ll
    
def noData(ax):
    ax.text(0.5,0.5,'no data',horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)


def format_func(x, pos):
    hours = int(x//3600)
    minutes = int((x%3600)//60)
    #seconds = int(x%60)

    return "{:d}h{:02d}".format(hours, minutes)
    #return "{:d}h".format(hours)
    
def invert( a,b ):
        return b,a

def numberOfNosePokeVersusTime( ax , phase , analyser ):
        
    analyser.setAnalysisPhase( phase )
    times, left_sugars, right_sugars, left_socials, right_socials = analyser.getPhaseNosePoke()
    
    ax.xaxis.set_major_formatter(formatter)
    
    styleLeft = "--"
    styleRight = "-"
    
    if "left" in analyser.initialNosepokedirection:
        styleLeft, styleRight = invert( styleLeft, styleRight )
    
    if "PHASE6" in phase:
        styleLeft, styleRight = invert( styleLeft, styleRight )
        
        
    print( styleLeft, styleRight )
    
    
    ax.plot( times, left_sugars , label="left sugar" , c="orange" , ls=styleLeft  )
    ax.plot( times, right_sugars , label="right sugar" , c="orange" , ls=styleRight )
    ax.plot( times, left_socials , label="left social" , c="blue" , ls=styleLeft )
    ax.plot( times, right_socials , label="right social" , c ="blue" , ls=styleRight )
    ax.legend()
    
    
    if len( times ) == 0:
        noData( ax )
        
    ax.set_ylabel("Cumulated nose pokes")
    ax.set_title( f"{phase} : Nose pokes versus time" )
        
def getRatioProgress(  ax , phase , analyser , nbValue ):
    
    
    times, ratios, nbValues = analyser.getRatioProgress( phase, nbValue )
    ax.xaxis.set_major_formatter(formatter)
    
    ax.plot( times, ratios , label="sugar+social score")    
    ax.legend()
    
    if len( times ) == 0:
        noData( ax )
    
    threshold = 2.*(nbValue/3.)
    for i in range( len( ratios )):
        ratio = ratios[i]
        time = times[i]
        nbVal = nbValues[i] # to check if enough values have been checked ( 20 or 40 ? )
        if ratio > threshold and nbVal > nbValue :
            ax.axvline( time , c="red" , ls=":")
            ax.text( time , 2 , "Threshold reached", rotation=90,ha="left", c="red" )
            break
    
    ax.set_ylabel("number of correct last {nbValue} pokes")
    ax.set_title( f"{phase} : Number of correct last {nbValue} pokes" )
    ax.axhline( 1+int( 2.*(nbValue/3.) ) , c="black" , ls="--")
                
                
def locationOfMouseVersusTime( ax , phase, analyser ):
    
    
    times, values = analyser.getMouseLocationVersusTime( phase )
    
    ax.xaxis.set_major_formatter(formatter)
    
    ax.plot( times, values )    
    
    # 1: social location
    # 0: central location
    # -1: sucrose location
    labels = ["sucrose location","central location","social location"]
    y = [ -1, 0 , 1 ]
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    
    
    if len( times ) == 0:
        noData( ax )
    
    ax.set_title( f"{phase} : Location of mice" )
    
def processFile( file ):
    
    print("---------------------------------")
    print("Processing file..." , file )
    analyser = LogAnalyser( file )
    

    # number of nose poke in each phase and what progressive ratio is reached
            
    phases = [ "PHASE1" , "PHASE2" ]
        
    '''
    analyser.setAnalysisPhase( "PHASE1" )
    
    analyser.printCurrentPhase()
    
    nbEnterSocial = analyser.getNbEnter("social")
    print( f"Number of enter in social: {nbEnterSocial}"  )
    nbEnterSugar = analyser.getNbEnter("sugar")
    print( f"Number of enter in sugar: {nbEnterSugar}"  )
    '''
    
    analyser.setAnalysisPhase( None )
    analyser.getJamReport( file+".jamReport.txt" )
    
    
    print("Initial nose poke direction: " , analyser.initialNosepokedirection )
    
    
    analyser.setAnalysisPhase( "PHASE1" )
    times, left_sugars, right_sugars, left_socials, right_socials = analyser.getPhaseNosePoke()
    print( "Phase 1")
    print( f"Left: {left_sugars[-1]}" )
    print( f"Right: {right_sugars[-1]}" )

    analyser.setAnalysisPhase( "PHASE2" )
    times, left_sugars, right_sugars, left_socials, right_socials = analyser.getPhaseNosePoke()
    print( "Phase 2")
    print( f"Left: {left_sugars[-1]}" )
    print( f"Right: {right_sugars[-1]}" )
    
    lastLine = ""
    analyser.setAnalysisPhase( "PHASE2" )
    for line in analyser.plines:
        if "current ratio: sugar" in line:
            lastLine = line 
    print("Phase 2:")
    print (lastLine )
    


if __name__ == '__main__':
    
    formatter = FuncFormatter(format_func)
    
    #file = 'exp728.log.txt'
    from math import exp
    progressiveRatio = []
    for i in range( 0 , 20 ):
        progressiveRatio.append( int( 5* exp( 0.2 * i ) -4 ) ) #5 × e0.2n -5
        #self.progressiveRatio.append( int( 5* exp( 0.2 * i )  ) ) #5 × e0.2n -5
    
    print("Progress ratios:")
    print ( progressiveRatio )
    
    # batch mode
    from os import listdir
    from os.path import isfile, join
    mypath = "batch control sucrose motivation" 
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print( onlyfiles )
    
    for file in onlyfiles:
        if "jamReport" in file:
            continue
        if ".pdf" in file:
            continue
        processFile( mypath+"/"+file )
     
    
    
    
    '''
    file = 'batch control sucrose motivation/control_sucrose_motivation - 2022-10-24 maleWTda114(3818)8moisright.log.txt'
    processFile( file )
    '''
    
    

    print("Done.")
    #plt.show()
    

    