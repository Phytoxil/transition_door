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


worksheet = None
wy= 0


def jitter( value , l ):
    ll =[]
    for i in range( len(l) ):
        ll.append( value+ (random.random()-0.5)*0.4 )
    return ll
    
def noData(ax ,text="no data"):
    ax.text(0.5,0.5,text,horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)


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

def trimRatioPhase6( analyser , nbValue ):
    # WARNING: dirty copy of getRatioProgress
    phase = "PHASE6"
    analyser.setAnalysisPhase(phase)
    times, ratios, nbValues, realTimes = analyser.getRatioProgress( phase, nbValue )
    threshold = 2.*(nbValue/3.)
    for i in range( len( ratios )):
        ratio = ratios[i]
        time = times[i]
        realTime = realTimes[i]
        nbVal = nbValues[i] # to check if enough values have been checked ( 20 or 40 ? )
        if ratio > threshold and nbVal > nbValue :
            # threshold reached
            analyser.trimAll( realTime )
            
            return
        
def getRatioProgress(  ax , phase , analyser , nbValue ):
    
    
    times, ratios, nbValues , notused = analyser.getRatioProgress( phase, nbValue )
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
            writeToXls(phase, "RatioProgress: threshold reached at time (s)", int(time), "ratio is", ratio )
            break
    
    ax.set_ylabel(f"number of correct last {nbValue} pokes")
    ax.set_title( f"{phase} : Number of correct last {nbValue} pokes" )
    ax.axhline( 1+int( 2.*(nbValue/3.) ) , c="black" , ls="--")
                
                
def locationOfMouseVersusTime( ax , phase, analyser ):
    
    
    times, values,totalSocial, totalSugar = analyser.getMouseLocationVersusTime( phase )
    
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
    
    ax.set_title( f"{phase} : Location of mice. Total time in social (s): {int(totalSocial)} / sugar: {int(totalSugar)}" )
    
    writeToXls("Location of mice (total time in seconds):",phase,"social",int(totalSocial),"sugar",int(totalSugar))

def writeToXls( *data ):
    global worksheet
    global wy
    x =0
    for i in range(len(data)):
        worksheet.write( wy, x , data[i] )
        x+=1        
    wy+=1
    


def processFile( file , workbook ):
    
    print("Processing file...")
    analyser = LogAnalyser( file )
    
    #xlsSheet = xls.sheet_by_name(file)
    fileNameOnly = file.split("/")[1][0:31]
    print( fileNameOnly )
    #worksheet = workbook.get_worksheet_by_name( fileNameOnly )
    #if worksheet == None:
 
    print("Creating worksheet")
    global worksheet
    global wy
    worksheet = workbook.add_worksheet( analyser.experimentName )    
    worksheet.set_column(0, 1, 50)
    worksheet.set_column(1, 5, 30)
    wy = 0
    
    #    worksheet.write(6, 6, 'test2')
    
    
    
    phases = [ "PHASE1" , "PHASE2" , "PHASE3" , "PHASE4","PHASE5","PHASE6"]
        
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
    
    
    
    
    fig, axes = plt.subplot_mosaic([["A","B","C","D","E","F"],["G","H","I","J","K","L"],["M","N","O","P","Q","R"],["S","S","S","S","S","S"],["T","T","T","T","T","T"],["U","U","U","U","U","U"],["V","V","V","V","V","V"],["W","W","W","W","W","W"],["X","X","X","X","X","X"],["Y","Y","Y","Y","Y","Y"],["Z","Z","Z","Z","Z","Z"],["0","0","0","0","0","0"],["1","1","1","1","1","1"],["2","2","2","2","2","2"],["3","3","3","3","3","3"],["4","4","4","4","4","4"],["5","5","5","5","5","5"],["6","6","6","6","6","6"]] , figsize=( 16,40 ) )
    print( axes )
    #fig, axes = plt.subplots(nrows=nbRows, ncols=nbCols, figsize=(4*nbCols, 3*nbRows) ) # sharey=True
    
    plt.suptitle( f"Experiment {analyser.experimentName} - started on {str(analyser.startTime)[:-10]} - initial nose poke: {analyser.initialNosepokedirection}")
    
    
    
    
    axList = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","0","1","2","3","4","5","6"]
    
    axes["B"].sharey( axes["A"] )
    axes["C"].sharey( axes["A"] )
    axes["D"].sharey( axes["A"] )
    axes["E"].sharey( axes["A"] )
    axes["F"].sharey( axes["A"] )
    
    # trim phase 6 until threshold is reached:
    
    trimRatioPhase6( analyser , 40 )
    
    
    writeToXls( "nose poke summary" )
    writeToXls( "phase", "social", "nbWrong","nbCorrect","nbCancelTimeOut", "nbCancelOther" )
    for phase in phases:
        analyser.setAnalysisPhase( phase )

        nbWrong,nbCorrect,nbCancelTimeOut, nbCancelOther = analyser.getNosePokeWrongCorrect("social")        
        writeToXls( phase, "social", nbWrong,nbCorrect,nbCancelTimeOut, nbCancelOther  )
        
        nbWrong,nbCorrect,nbCancelTimeOut, nbCancelOther = analyser.getNosePokeWrongCorrect("sugar")        
        writeToXls( phase, "sugar", nbWrong,nbCorrect,nbCancelTimeOut, nbCancelOther  )
        
    
    graphIndex = 0
    for phase in phases:
        print("Phase")
        worksheet.write( wy, 0 , phase )
        wy+=1
        
        analyser.setAnalysisPhase( phase )
        nbEnterSocial = analyser.getNbEnter("social")
        print( f"Number of enter in social: {nbEnterSocial}"  )
        
        worksheet.write( wy, 0 , "Number of enter in social:" )
        worksheet.write( wy, 1 , nbEnterSocial )
        wy+=1
        
        nbEnterSugar = analyser.getNbEnter("sugar")
        print( f"Number of enter in sugar: {nbEnterSugar}"  )
        worksheet.write( wy, 0 , "Number of enter in sugar:" )
        worksheet.write( wy, 1 , nbEnterSugar )
        wy+=1

    
        ax = axes[axList[graphIndex]]
        #ax.sharey( axes[0][0])
        pps = ax.bar( [0,1] , [ nbEnterSocial , nbEnterSugar ] )
        ax.set_ylabel("Number of entrance in area")
        
        # add number on top:
        for p in pps:
            height = p.get_height()
            ax.annotate('{}'.format(height),
                xy=(p.get_x() + p.get_width() / 2, height),
                xytext=(0, 3), # 3 points vertical offset
                textcoords="offset points", ha='center', va='bottom')
        
        
        #print( 2 + ( analyser.startTime - analyser.startPhase ).days )
        
        #quit()
        
        
        try:
            seconds = analyser.getPhaseDurationS()
            title = f"{phase} ({int( seconds/60)} min)"
            title += f"\n{analyser.startPhase.strftime('%A')[:2]}:{analyser.startPhase.hour}h{analyser.startPhase.minute}"
            title += f" - {analyser.endPhase.strftime('%A')[:2]}:{analyser.endPhase.hour}h{analyser.endPhase.minute} "
            #analyser.endPhase
            ax.set_title( title ) # {analyser.endPhase}
            
            
            ax.set_xticklabels( ["Social","Sugar"] )
            ax.set_xticks( [0,1] )
            
            if graphIndex == 0:
                ax.axhline( 10 , c="black" , ls="--")
        except:
            noData(ax)            
            print(f"No data for phase {phase}")
        
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
        
        if len( socialList ) == 0 and len( sugarList ) == 0:
            noData( ax )
        
        ax.set_xticklabels( ["","Social","Sugar",""] )
        ax.set_xticks( [0,1,2,3] )
                
        graphIndex +=1
    
    
    # time to get in area
    
    
    for phase in phases:
        if "PHASE1" in phase:
            ax = axes[axList[graphIndex]]
            noData(ax,text="no data for\nphase 1")
            graphIndex +=1
            continue
        
        print(phase )
        
        analyser.setAnalysisPhase( phase )
        socialTimes, socialList = analyser.getTimeToEnterArea("social")
        print( f"Time to get in social: {socialList}"  )
        sugarTimes, sugarList = analyser.getTimeToEnterArea("sugar")
        print( f"Time to get in sugar: {sugarList}"  )
        #print (socialTimes)
        
        writeToXls( "time between nose poke and enter for ", phase  )
        writeToXls( "location from start in phase (s)","duration(s)"  )
        writeToXls( "social"  )
        print( socialTimes )
        
        for i in range( len( socialTimes ) ):
            writeToXls(  int(socialTimes[i]) , socialList[i]  )
        writeToXls( "sugar" )
        for i in range( len( sugarTimes ) ):
            writeToXls(  int(sugarTimes[i]) , sugarList[i]  )
            
        
        
        '''
        if "PHASE1" in phase:
            noData( ax )
            graphIndex +=1
            continue
        '''
        
        ax = axes[axList[graphIndex]]
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(MultipleLocator(base=3600*3))
        ax.xaxis.set_minor_locator(MultipleLocator(base=3600))
        #ax.xaxis.set_major_locator(MultipleLocator(base=3600*4))
        #ax.sharey( axes[2][0])
        
        ax.plot( socialTimes, socialList , label="social")
        ax.plot( sugarTimes, sugarList , label="sugar" )
        ax.legend()
        
        if len( socialTimes ) == 0 and len( sugarTimes ) == 0:
            noData( ax )
        
        ax.set_ylabel("time between np and enter (s)")
        ax.set_title( f"{phase}" )
                
        graphIndex +=1
    
    
    # number of unvalidated per phase (excel output)
    writeToXls("Number of timeout entry")
    writeToXls("Phase","nbSocial","nbSugar")
    for phase in phases:
        analyser.setAnalysisPhase( phase )
        nbSocial = analyser.getNbTimeOut("social")
        nbSugar = analyser.getNbTimeOut("sugar")
        writeToXls(phase,nbSocial,nbSugar)
        
    # brut number of nose poke per phase
    writeToXls("raw number of nose poke", "initial nose poke direction: ", analyser.initialNosepokedirection  )
    writeToXls("Phase","nbSocial left","nbSocial right","nbSugar left","nbSugar right")
    for phase in phases:
        analyser.setAnalysisPhase( phase )
        nbSocialLeft, nbSocialRight = analyser.getNbRawPoke("social")
        nbSugarLeft, nbSugarRight = analyser.getNbRawPoke("sugar")
        writeToXls(phase,nbSocialLeft, nbSocialRight,nbSugarLeft, nbSugarRight)
    
    # phase 1 : location of the mouse
        
    ax = axes[axList[graphIndex]]
    locationOfMouseVersusTime( ax , "PHASE1" , analyser )    
    graphIndex +=1
    
    
    # phase 2 : location of the mouse
        
    ax = axes[axList[graphIndex]]
    locationOfMouseVersusTime( ax , "PHASE2" , analyser )    
    graphIndex +=1
    
    # phase 2 : number of right and left nose poke for each fed
        
    ax = axes[axList[graphIndex]]
    numberOfNosePokeVersusTime( ax , "PHASE2" , analyser )    
    graphIndex +=1
    
    
    # phase 3 : location of the mouse
        
    ax = axes[axList[graphIndex]]
    locationOfMouseVersusTime( ax , "PHASE3" , analyser  )    
    graphIndex +=1
    
    # phase 3 : number of right and left nose poke for each fed
        
    ax = axes[axList[graphIndex]]
    numberOfNosePokeVersusTime( ax , "PHASE3" , analyser )    
    graphIndex +=1


    # phase 3 ratio 40 shared between sugar and social

    ax = axes[axList[graphIndex]]
    getRatioProgress( ax , "PHASE3" , analyser, 40 )
    graphIndex +=1

    
    

    '''
    # phase 3 ratio (old way with 20 pokes per feeder)
    
    ax = axes[axList[graphIndex]]
    
    analyser.setAnalysisPhase( "PHASE3" )
    times, socialList, sugarList = analyser.getRatioProgressPhase3()
    ax.xaxis.set_major_formatter(formatter)

    print( socialList )
    print( sugarList )
    
    ax.plot( times, socialList , label="social")
    ax.plot( times, sugarList , label="sugar" )
    ax.legend()
    
    if len( times ) == 0:
        noData( ax )
    
    ax.set_ylabel("number of correct last 20 pokes")
    ax.set_title( "Number of correct last 20 pokes in phase 3" )
    ax.axhline( 13.5 , c="black" , ls="--")
                
    graphIndex +=1
    '''
        
    
    '''
    # phase 4 : number of right and left nose poke for each fed
        
    ax = axes[axList[graphIndex]]
    numberOfNosePokeVersusTime( ax , "PHASE4" , analyser )    
    graphIndex +=1
    '''
    
    # phase 4 : location of the mouse
        
    ax = axes[axList[graphIndex]]
    locationOfMouseVersusTime( ax , "PHASE4" , analyser  )    
    graphIndex +=1
    
    # phase 4 ratio
    
    
    ax = axes[axList[graphIndex]]
    
    analyser.setAnalysisPhase( "PHASE4" )
    
    times, socials, sugars, step_socials, step_sugars = analyser.getProgressPhase4()

    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(MultipleLocator(base=3600))
    
    #print( socialList )
    #print( sugarList )
    
    ax.plot( times, socials , label="social")
    ax.plot( times, sugars , label="sugar" )
    
    ax.plot( times, step_socials , label="social_step" , c="blue" , ls=":" )
    ax.plot( times, step_sugars , label="sugar_step" , c="orange" , ls=":" )
    
    if len( times ) == 0:
        noData( ax )
        
    ax.set_title( "Progressive ratio phase 4" )
    ax.set_ylabel("cumulated correct pokes")
    
    ax.legend()
                
    graphIndex +=1
    
    
    # phase 4 cumulated
    
    ax = axes[axList[graphIndex]]
    
    analyser.setAnalysisPhase( "PHASE4" )
    
    times, socialRs, socialLs, sugarRs, sugarLs = analyser.getCumulatedPhase4()
    ax.xaxis.set_major_formatter(formatter)
    #ax.xaxis.set_major_locator(MultipleLocator(base=3600))
    #print( socialList )
    #print( sugarList )
    
    styleLeft = "--"
    styleRight = "-"
    if "left" in analyser.initialNosepokedirection:
        styleLeft, styleRight = invert( styleLeft, styleRight )
    
        
    ax.plot( times, socialRs , label="social right" , c="blue" , ls=styleRight )
    ax.plot( times, socialLs , label="social left" , c="blue" , ls=styleLeft )
    
    ax.plot( times, sugarRs , label="sugar right" , c="orange" , ls=styleRight )
    ax.plot( times, sugarLs , label="sugar left" , c="orange" , ls=styleLeft )
    
    if len( times ) == 0:
        noData( ax )
        
    ax.set_title( "Cumulated nose poke phase 4 " + analyser.progressiveRatioAtEnd )
    ax.set_ylabel("cumulated poke")
    
    ax.legend()
                
    graphIndex +=1
    
    
    # phase 5 : location of the mouse
        
    ax = axes[axList[graphIndex]]
    locationOfMouseVersusTime( ax , "PHASE5" , analyser  )    
    graphIndex +=1
    
    # phase 5 : number of right and left nose poke for each fed
        
    ax = axes[axList[graphIndex]]
    numberOfNosePokeVersusTime( ax , "PHASE5" , analyser )    
    graphIndex +=1
    
    # phase 5 ratio 20 shared between sugar and social

    ax = axes[axList[graphIndex]]
    getRatioProgress( ax , "PHASE5" , analyser, 20 )
    graphIndex +=1


    # phase 6 : location of the mouse
        
    ax = axes[axList[graphIndex]]
    locationOfMouseVersusTime( ax , "PHASE6" , analyser  )    
    graphIndex +=1
    
    # phase 6 : number of right and left nose poke for each fed
        
    ax = axes[axList[graphIndex]]
    numberOfNosePokeVersusTime( ax , "PHASE6" , analyser )    
    graphIndex +=1
    
    # phase 6 ratio 40 shared between sugar and social

    ax = axes[axList[graphIndex]]
    getRatioProgress( ax , "PHASE6" , analyser , 40 )
    graphIndex +=1


    
    
    
    
    
    
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.98])
    plt.savefig( file+".pdf" )


if __name__ == '__main__':
    
    import xlsxwriter
    formatter = FuncFormatter(format_func)
    workbook = xlsxwriter.Workbook("batch social sucrose/excel_output social vs sucrose.xlsx")
    
    
    
    
    #file = 'exp728.log.txt'
    
    '''
    '''
    # batch mode
    from os import listdir
    from os.path import isfile, join
    mypath = "batch social sucrose" 
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print( onlyfiles )
    
    for file in onlyfiles:
        if "jamReport" in file:
            continue
        if ".pdf" in file:
            continue
        if ".xls" in file:
            continue
        if ".zip" in file:
            continue
        processFile( mypath+"/"+file , workbook )
     
    
    
    '''
    #file = 'batch social sucrose/gateLog - 2022-10-19 malekoda113(3777)8mois.log.txt'
    
    file = "batch social sucrose/2022-08-31 femWTda91(5662).log.txt" # problem file ?    
    processFile( file , workbook )
    '''
    
    
    
    workbook.close()
    
    
    
    

    print("Done.")
    #plt.show()
    

    