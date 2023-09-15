'''
Created on 16 mars 2022

@author: Fab
'''

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import itertools
import numpy

from experiments.sugarsocial.analysis.LogAnalyser import LogAnalyser
import random
    

def jitter( value , l ):
    ll =[]
    for i in range( len(l) ):
        ll.append( value+ (random.random()-0.5)*0.4 )
    return ll
    
    
if __name__ == '__main__':
    
    file = 'expOk01.log.txt'
    
    analyser = LogAnalyser( file )
        
    phases = [ "PHASE1" , "PHASE2" , "PHASE3" , "PHASE4"]
        
    '''
    analyser.setAnalysisPhase( "PHASE1" )
    
    analyser.printCurrentPhase()
    
    nbEnterSocial = analyser.getNbEnter("social")
    print( f"Number of enter in social: {nbEnterSocial}"  )
    nbEnterSugar = analyser.getNbEnter("sugar")
    print( f"Number of enter in sugar: {nbEnterSugar}"  )
    '''
    
    nbRows = 4
    nbCols = 4
    fig, axes = plt.subplot_mosaic([["A","B","C","D"],["E","F","G","H"],["I","J","K","L"],["M","M","M","M"],["N","N","N","N"],["O","O","O","O"]] , figsize=( 12,12 ) )
    print( axes )
    #fig, axes = plt.subplots(nrows=nbRows, ncols=nbCols, figsize=(4*nbCols, 3*nbRows) ) # sharey=True
    
    plt.suptitle( f"Experiment {analyser.experimentName}")
    
    # number of entrance in areas
    
    axList = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O"]
    
    axes["B"].sharey( axes["A"] )
    axes["C"].sharey( axes["A"] )
    axes["D"].sharey( axes["A"] )
    
    graphIndex = 0
    for phase in phases:
        print("Phase")
        analyser.setAnalysisPhase( phase )
        nbEnterSocial = analyser.getNbEnter("social")
        print( f"Number of enter in social: {nbEnterSocial}"  )
        nbEnterSugar = analyser.getNbEnter("sugar")
        print( f"Number of enter in sugar: {nbEnterSugar}"  )
    
        ax = axes[axList[graphIndex]]
        #ax.sharey( axes[0][0])
        ax.bar( [0,1] , [ nbEnterSocial , nbEnterSugar ] )
        ax.set_ylabel("Number of entrance in area")
        
        seconds = analyser.getPhaseDurationS()
        ax.set_title( f"{phase} ({int( seconds/60)} min)" )
        
        
        ax.set_xticklabels( ["Social","Sugar"] )
        ax.set_xticks( [0,1] )
        
        if graphIndex == 0:
            ax.axhline( 10 , c="black" , ls="--")
        
        graphIndex +=1
    
    # time spent in each area
    
    
    for phase in phases:
        print(phase )
        analyser.setAnalysisPhase( phase )
        socialList = analyser.getTimeInArea("social")
        print( f"Time in social: {socialList}"  )
        sugarList = analyser.getTimeInArea("sugar")
        print( f"Time in sugar: {sugarList}"  )
        ax = axes[axList[graphIndex]]
        #ax.sharey( axes[1][0])
        
        ax.scatter( jitter(1 , socialList), socialList , alpha=0.5 )
        ax.scatter( jitter(2 , sugarList), sugarList  , alpha=0.5 )
        ax.set_ylabel("time spent in area (s)")
        ax.set_title( f"{phase}" )
        
        ax.set_xticklabels( ["","Social","Sugar",""] )
        ax.set_xticks( [0,1,2,3] )
                
        graphIndex +=1
    
    
    # time to get in area
    
    
    for phase in phases:
        print(phase )
        analyser.setAnalysisPhase( phase )
        socialTimes, socialList = analyser.getTimeToEnterArea("social")
        print( f"Time to get in social: {socialList}"  )
        sugarTimes, sugarList = analyser.getTimeToEnterArea("sugar")
        print( f"Time to get in sugar: {sugarList}"  )
        ax = axes[axList[graphIndex]]
        #ax.sharey( axes[2][0])
        
        ax.plot( socialTimes, socialList , label="social")
        ax.plot( sugarTimes, sugarList , label="sugar" )
        ax.legend()
        
        ax.set_ylabel("time between np and enter (s)")
        ax.set_title( f"{phase}" )
                
        graphIndex +=1
    
    
    
    # phase 3 ratio
    
    
    ax = axes[axList[graphIndex]]
    
    analyser.setAnalysisPhase( "PHASE3" )
    times, socialList, sugarList = analyser.getRatioProgressPhase3()

    print( socialList )
    print( sugarList )
    
    ax.plot( times, socialList , label="social")
    ax.plot( times, sugarList , label="sugar" )
    ax.legend()
    
    ax.set_ylabel("number of correct last 20 pokes")
    ax.set_title( "Number of correct last 20 pokes in phase 3" )
    ax.axhline( 13.5 , c="black" , ls="--")
                
    graphIndex +=1
        
    # phase 4 ratio
    
    
    ax = axes[axList[graphIndex]]
    
    analyser.setAnalysisPhase( "PHASE4" )
    
    times, socials, sugars, step_socials, step_sugars = analyser.getProgressPhase4()

    #print( socialList )
    #print( sugarList )
    
    ax.plot( times, socials , label="social")
    ax.plot( times, sugars , label="sugar" )
    
    ax.plot( times, step_socials , label="social_step" , c="blue" , ls="--" )
    ax.plot( times, step_sugars , label="sugar_step" , c="orange" , ls="--" )
    
    ax.set_title( "Progressive ratio phase 4" )
    
    ax.legend()
                
    graphIndex +=1
    
    
    # phase 4 cumulated
    
    ax = axes[axList[graphIndex]]
    
    analyser.setAnalysisPhase( "PHASE4" )
    
    times, socialRs, socialLs, sugarRs, sugarLs = analyser.getCumulatedPhase4()

    #print( socialList )
    #print( sugarList )
    
    ax.plot( times, socialRs , label="social right" , c="blue" , ls="--" )
    ax.plot( times, socialLs , label="social left" , c="blue" , ls="-" )
    
    ax.plot( times, sugarRs , label="sugar right" , c="orange" , ls="--" )
    ax.plot( times, sugarLs , label="sugar left" , c="orange" , ls="-" )
    
    ax.set_title( "Cumulated nose poke phase 4" )
    ax.set_ylabel("cumulated poke")
    
    ax.legend()
                
    graphIndex +=1
    
    
    
    plt.tight_layout()
    plt.show()
    

    