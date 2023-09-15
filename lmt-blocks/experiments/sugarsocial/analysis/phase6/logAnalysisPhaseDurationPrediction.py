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
import json
import numpy as np
import matplotlib
from matplotlib import ticker

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

def convert_to_d_h_m_s( frames ):
    """Return the tuple of days, hours, minutes and seconds."""
    #seconds = frames / 30
    seconds, f = divmod( frames, 30)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    return days, hours, minutes, seconds, f


def frameToTimeTicker(x, pos):
   
    #    vals= convert_to_d_h_m_s( x*30 )
    #return "D{0} - {1:02d}:{2:02d}".format( int(vals[0])+1, int(vals[1]), int(vals[2]) )
    return str ( int( x/(60*60) ) ).zfill(2)



def compute():
    
    
    # batch mode
    from os import listdir
    from os.path import isfile, join
    mypath = "batch social sucrose" 
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print( onlyfiles )
    
    numberOfAnimals = {}
    
    data = {}
    
    for file in onlyfiles:
        if "jamReport" in file:
            continue
        if ".pdf" in file:
            continue
        if ".xls" in file:
            continue
        if ".zip" in file:
            continue
        #processFile( mypath+"/"+file )
        
        analyser = LogAnalyser( mypath+"/"+file )
        phases = [ "PHASE1" , "PHASE2" , "PHASE3" , "PHASE4","PHASE5","PHASE6"]
        
        
        
        print("---")
        print( "file" , analyser.logFile )
        print( "name", analyser.experimentName )
        print( "geno", analyser.getGenotype() )
        print( "sex", analyser.getSex() )
        print( "age", analyser.getAge() )
        phaseDurationList = []
        for phase in phases:
            analyser.setAnalysisPhase( phase )
            try:
                phaseDurationList.append( analyser.getPhaseDurationS() )
            except:
                phaseDurationList.append( None ) # this phase has not been reached
                            
        
        data[ analyser.logFile ] = {}
        d = data[ analyser.logFile ]
        d[ "name" ] = analyser.experimentName
        d[ "genotype" ] = analyser.getGenotype()        
        d[ "sex" ] = analyser.getSex()
        d[ "age" ] = analyser.getAge()
        d[ "phaseDurations"] = phaseDurationList
        d[ "endTimePhase6S"] = getEndTimePhase6( analyser )
        
        json.dump(data, open("SugarSocialData.json", 'w'))
        
        k = f"{analyser.getGenotype()} {analyser.getSex()} {analyser.getAge()}w"
        if k not in numberOfAnimals:            
            numberOfAnimals[k] = 0
        numberOfAnimals[k]+=1
        
    print("Animal list:")
    for k,v in numberOfAnimals.items():
        print(k,"\t",v)
     

def plot( data, genotype , phase , y2 ):
    
    x = []
    y = []
    for d in data.values():
        print( d )
        if d["genotype"] == genotype:
            x.append( d["phaseDurations"][phase] )
            y.append( y2 )    
    plt.scatter( x , y )

def toHM( seconds ):
    
    mm, ss = divmod(seconds, 60)
    hh, mm= divmod(mm, 60)
    return f"{int(hh)}:{str(int(mm)).zfill(2)}"

def getEndTimePhase6( analyser ):
    
    nbValue = 40
    times, ratios, nbValues , notused = analyser.getRatioProgress( "PHASE6", nbValue )    
    threshold = 2.*(nbValue/3.)
    for i in range( len( ratios )):
        ratio = ratios[i]
        time = times[i]
        nbVal = nbValues[i] # to check if enough values have been checked ( 20 or 40 ? )
        if ratio > threshold and nbVal > nbValue :
            return time            
            break
    
def analyse():
    
    
    data = json.load(open("SugarSocialData.json"))
    
    '''
    plot( data, "WT" , 0 , 1 )
    plot( data, "KO" , 0 , 2 )
    '''
    
    animals = []
    
    plt.figure(figsize=(20,8))
    colors = plt.get_cmap('RdYlGn')( np.linspace(0.15, 0.95, 6 ))
    ax = plt.gca()

    '''
    # filter data
    for k in data.copy():
        d = data[k]
        if not "KO" in d["genotype"]:
            data.pop(k)
    for k in data.copy():
        d = data[k]
        if not "female" in d["sex"]:
            data.pop(k)
    
    for k in data.copy():
        d = data[k]
        if d["age"] != 12:
            data.pop(k)
        
    for k in data.copy():
        d = data[k]
        if d["age"] !=12 :
            data.pop(k)
    
    
    for d in data:
        #print( d )
        dd = data[d]
        for maxPhase in range( 6 ):
            if dd["phaseDurations"][maxPhase] == None:                
                break
        endTime = ""
        if dd["endTimePhase6S"] != None:
            endTime =dd["endTimePhase6S"]
            
        
        print( f"{d}{dd['genotype']}\t{dd['sex']}\t{dd['age']}\t{dd['genotype']}\t{maxPhase+1}\t{endTime}" )
    quit()
    '''
    '''
            
    '''
    files = [ 
    "batch social sucrose/gateLog - 2022-10-17 malewtda114(3818)8mois.log.txt",

    "batch social sucrose/gateLog - 2022-08-31 femWTda91(5662)8months.log.txt",
    "batch social sucrose/gateLog - 2022-09-19 femWTda92(5605)8months.log.txt",
    "batch social sucrose/gateLog - 2022-10-26 femwtda115(3799)8mois.log.txt",
    
    "batch social sucrose/gateLog - 2022-10-19 malekoda113(3777)8mois.log.txt",
    "batch social sucrose/gateLog - 2022-11-02 malekoda117(3809)8mois.log.txt",

    "batch social sucrose/gateLog - 2022-09-05 femKOda103(5580)8months.log.txt",
    "batch social sucrose/gateLog - 2022-09-07 femKOda104(5652 blessee)8months.log.txt",
    "batch social sucrose/gateLog - 2022-11-07 femkoda130(5679)8mois phase1.log.txt",
    
    "batch social sucrose/gateLog - 2022-11-14 femhetda131(5701)8mois.log.txt",
    "batch social sucrose/gateLog - 2022-11-16 femhetda132(5716)8mois.log.txt",
    "batch social sucrose/gateLog - 2022-11-21 femhet146(5720)phase2 8mois.log.txt",
    "batch social sucrose/gateLog - 2022-11-23 femhet147(5691)8mois.log.txt",
    "batch social sucrose/gateLog - 2022-11-28 femhet138(5728)8moisphase2.log.txt",
    "batch social sucrose/gateLog - 2022-11-30 femhet139(5735)8mois phase3.log.txt",
    ]
    '''
    
    
    files = [
    "batch social sucrose/gateLog - 2022-09-21 maleWTda226(5669)12w.log.txt",    
    "batch social sucrose/gateLog - 2022-12-09 malewtda334(3795)12w.log.txt",
    "batch social sucrose/gateLog - 2023-02-13 malewtda375(2og)12w.log.txt",
    "batch social sucrose/gateLog - 2023-01-09 malewtda323(3806)12wok.log.txt",
    "batch social sucrose/gateLog - 2023-01-11 malewtda324(3780)12wok.log.txt",
    
    "batch social sucrose/gateLog - 2022-12-14 femwtda313(3802)12w.log.txt",    
    "batch social sucrose/gateLog - 2023-01-18 femwtda355(3876)12w.log.txt",
    
    "batch social sucrose/gateLog - 2022-12-05 femkoda315(3821)12w.log.txt",
    "batch social sucrose/gateLog - 2022-12-16 femkoda337(3820)12wphase3.log.txt",
    "batch social sucrose/gateLog - 2022-12-19 femkoda338(3786)12wphase2.log.txt",    
    "batch social sucrose/gateLog - 2023-01-04 femkoda339(3807)12wphase3.log.txt",
    "batch social sucrose/gateLog - 2023-01-06 femkoda340(3801)12wcompleted.log.txt",
    
    "batch social sucrose/gateLog - 2023-02-10 malekoda367(2od)12w.log.txt",
    "batch social sucrose/gateLog - 2022-09-26 maleKOda227(5584)12w.log.txt",    
    "batch social sucrose/gateLog - 2023-02-07 malekoda365(od)12w.log.txt",
    "batch social sucrose/gateLog - 2023-01-16 maleko318(od)12w.log.txt",
    "batch social sucrose/gateLog - 2023-01-16 maleko319(og)12ws2.log.txt",
    
    "batch social sucrose/gateLog - 2023-01-30 femhetda379(2od)12w.log.txt",
    "batch social sucrose/gateLog - 2023-02-01 femhetda369(og)12w.log.txt",
    "batch social sucrose/gateLog - 2023-02-03 femhetda371(2og)12w.log.txt",
    "batch social sucrose/gateLog - 2023-01-25 femhetda378(og)12w.log.txt",
    ]
    '''
    
    files=[ "batch social sucrose/gateLog - 2023-02-20 malewtda372(od)12w-setup1.log.txt",
           "batch social sucrose/gateLog - 2023-03-01 malewtda372(od)12w-setup2.log.txt"
    ]
    
    for d in data:
        print ( d )
    
    files.reverse()
    
    i = 0
    #for d in data.values():
    for f in files:
        
        d = data[f]
        animals.append( f"{i}: {d['genotype']} {d['sex']} {d['age']}w\n{f.split(' ')[-1].split('.')[0]}" )
        x = 0
        endedTooSoon = False
        for p in range( 6 ):
            val = d["phaseDurations"][p]
            if val == None:
                val = 0
                if not endedTooSoon:
                    #ax.barh( y=i, width = 60*10, left=x, height=0.8, color='black' )
                    endedTooSoon = True
            
            #ax.barh(labels, widths, left=starts, height=0.5, label=colname, color=color)
            color = colors[p]
            rects = ax.barh( y=i, width = val, left=x, height=0.8, color=color, label="test")
            
            r, g, b, _ = color
            text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
            if p!=5:
                if val!=0:
                    ax.text( x+val/2,i , toHM( val ) ,  ha="center", va="center" , color=text_color )
            
            #if p == 3: # phase 4
            if p ==5 :
                
                endPhase6 = d[ "endTimePhase6S"]
                if endPhase6 != None:
                    ax.barh( y=i, width = 600, left=x+endPhase6, height=0.9, color="red", label="end")
                    print( "duration : " , x, endPhase6, endPhase6-x )
                    ax.text( x+endPhase6/2, i , "goal reached in " + toHM( endPhase6 ) ,  ha="center", va="center" , color=text_color )
                
            x+=val
        
        i+=1
            
    animalLabels = []
    for animal in animals:
        animalLabels.append( animal.split(":")[-1] )
    plt.yticks( range( len( animals ) ), animalLabels )
    plt.xlim( 0 , 60*60*48 )
    
    ''' set x axis '''
    formatter = matplotlib.ticker.FuncFormatter( frameToTimeTicker )
    ax.xaxis.set_major_formatter(formatter)
    ax.tick_params(labelsize=8 )
    ax.xaxis.set_major_locator(ticker.MultipleLocator( 60 * 60 ))
    #ax.xaxis.set_minor_locator(ticker.MultipleLocator( 30 * 60 * 60 ))
    
    #colors = plt.get_cmap('hsv')( np.linspace(0.15, 0.85, 6 ))
    #print( colors )
    
    #ax.barh(labels, widths, left=starts, height=0.5, label=colname, color=color)
    
    
    '''
    b1 = plt.barh(animals, phases[0], color = colors[0] , stacked=True )
    b2 = plt.barh(animals, phases[1], color = colors[1] , stacked=True  )
    '''
    '''
    b3 = plt.barh(animals, phases[2], color = colors[2] )
    b4 = plt.barh(animals, phases[3], color = colors[3] )
    b5 = plt.barh(animals, phases[4], color = colors[4] )
    b6 = plt.barh(animals, phases[5], color = colors[5] )
    '''
    
    #plt.gca().axvline( 60 *60 * 47 )
    #plt.text( 1000 + 60 *60 * 48, 0, "47h experiment", rotation=90 )
    
    #b2 = plt.barh(year, issues_pending, left=issues_addressed, color="yellow")
    #plt.legend([b1, b2,b3,b4,b5,b6], ["Phase 1", "Phase 2","Phase 3","Phase 4", "Phase 5", "Phase 6"], title="Time in phases", loc="upper right")
    
    
    plt.tight_layout()
    plt.show()
    
     

if __name__ == '__main__':
    
    #compute()
    
    analyse()
        
    
    

    print("Done.")
    #plt.show()
    

    