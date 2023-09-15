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
    
'''
Current phase: Phase.PHASE2
SUGAR ok/wrong: (3, 7)
SOCIAL ok/wrong: (2, 11)

NB pass in sugar: 7
NB pass in social: 4

Current duration of this phase: 2:00:02.002261
Current duration of the experiment: 2:24:25.981867
'''

if __name__ == '__main__':
    
    file = 'gateLogProblem.txt'
        
    
    with open( file ) as f:
        lines = f.readlines()
    
    '''
    for line in lines:
        line = line.strip()
        print ( line )
    '''
    
    graph = {}
    graph[("SOCIAL","date")] = []
    graph[("SOCIAL","y")] = []
    graph[("SUGAR","date")] = []
    graph[("SUGAR","y")] = []
    
    graph[("NOSE POKE SOCIAL","date")] = []
    graph[("NOSE POKE SOCIAL","y")] = []
    graph[("NOSE POKE SUGAR","date")] = []
    graph[("NOSE POKE SUGAR","y")] = []
    
    plt.rcParams["figure.figsize"] = (20,2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())

    dateInSugar = None
    dateOutSugar = None

    dateInSocial = None
    dateOutSocial = None

    dateInSocialPoke = None # effective nose poke, no bounce poke
    dateInSugarPoke = None 
    
    startDate = None
    
    dateInSocialPokes = []
    dateInSugarPokes = []
    timeBetweenSocialPokeAndEnter = []
    timeBetweenSugarPokeAndEnter = []
    timeInSocial = []
    timeInSugar = []

    dropLines = True
    
    sugarOk = 0
    socialOk = 0
    sugarWrong = 0
    socialWrong = 0
    
    sugarR = 0
    sugarL = 0
    socialR = 0
    socialL = 0
    
    for line in lines:

        date = line[0:23]
        dateIn = dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
        
        if "Starting phase: Phase.PHASE2" in line:
            dropLines = False
            startDate = dateIn
        
        if dropLines:
            continue
        
        if "Starting phase: Phase.PHASE3" in line:
            break
        
        
        if "*sugarFed*nose poke*right" in line:
            sugarR +=1
            
        if "*sugarFed*nose poke*left" in line:
            sugarL +=1
        
        if "*socialFed*nose poke*right" in line:
            socialR +=1
        
        if "*socialFed*nose poke*left" in line:
            socialL +=1
        
    
    print( sugarR )
    print( sugarL )
    print( socialR )
    print( socialL )