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
    
    file = 'gateLogNico1.txt'
        
    
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
    
    '''
    plt.rcParams["figure.figsize"] = (20,2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())
    '''

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
    
    rfidDic = {}
    nbRFIDProblem = 0
    
    test1Weight = None
    test2Weight = None
    weightList = []
    
    
    for line in lines:

        date = line[0:23]
        dateIn = dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
        
        #[RFID CHECK][GATE TEST1] Animal allowed to cross:
        #print( dateIn )
    
        if "[RFID CHECK]" in line:
            print ( line )
            rfid= line.split(" ")[-1].strip()
            if rfid not in rfidDic:
                rfidDic[ rfid ] = 0 
                
            rfidDic[ rfid ] +=1
            
            
        if "Checking RFID: remaining attempts: 29" in line:
            nbRFIDProblem+=1
            
        
        if "GATE TEST1 CheckForOneAnimalLogic WEIGHT OK:" in line:
            test1Weight = float ( line.split(" ")[-1].strip() )
        if "[GATE TEST1] Animal allowed to cross:":
            rfid= line.split(" ")[-1].strip()
            weightList.append( ( 1, rfid, test1Weight ) )

        if "GATE TEST2 CheckForOneAnimalLogic WEIGHT OK:" in line:
            test2Weight = float ( line.split(" ")[-1].strip() )
        if "[GATE TEST2] Animal allowed to cross:":
            rfid= line.split(" ")[-1].strip()
            weightList.append( ( 2, rfid, test2Weight ) )
            
        
         
            
    print( rfidDic )
    print("Number of RFID problem: ", nbRFIDProblem)

    

    # display progression
    plt.clf()
    #plt.figure(figsize=(20, 6), dpi=80)
    fig, axes = plt.subplots( nrows = 1 , ncols = 8 , figsize=( 24, 4 ) ,  sharey='all'  )
    
    i = 0
    for rfid in rfidDic:        
        
        for gate in [1,2]:
            values = []
            for w in weightList:
                if w[0] == gate:
                    if w[1] == rfid:
                        values.append( w[2] )
                         
            axes[i].plot( values , label = "gate " + str( gate ) + " " + rfid )
            axes[i].legend( loc=4 )
            i+=1
    
    
    title = "RFID per gate and weight"
    
    plt.title( title )
    plt.ylabel( "grams" )
    plt.xlabel( "trials" )
    #plt.tight_layout()
    plt.savefig( file+" " +str( title )+".pdf")
    plt.show()

    '''    
    plt.clf()
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot( timeBetweenSugarPokeAndEnter )
    title = "Time between sugar poke and enter"
    plt.title( title )
    plt.ylabel( "seconds" )
    plt.xlabel( "trials" )
    plt.tight_layout()
    plt.savefig( file+" "+str( title )+".pdf")
    #plt.show()
    
    plt.clf()
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot( timeInSocial )
    title = "Time in social"
    plt.title( title )
    plt.ylabel( "seconds" )
    plt.xlabel( "trials" )
    plt.tight_layout()
    plt.savefig( file+" "+str( title )+".pdf")
    #plt.show()
    
    plt.clf()
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot( timeInSugar )
    title = "Time in sugar"
    plt.title( title )
    plt.ylabel( "seconds" )
    plt.xlabel( "trials" )
    plt.tight_layout()
    plt.savefig( file+" "+str( title )+".pdf")
    #plt.show()
    '''
    
    # text summary:
    
    '''
    print("---")
    print( "Nature\tpoke date\ttime in experimentation\ttime to enter\ttime in room(s)")

    print("---")
    for i in range( len( dateInSugarPokes ) ):
        dateInPoke = dateInSugarPokes[i]
        timeSinceStart = dateInPoke - startDate
        timeToEnter = timeBetweenSugarPokeAndEnter[i]
        timeInRoom = timeInSugar[i]
        
        print( "Sugar\t" + str( dateInPoke )[:-7] +"\t" + str( timeSinceStart )[:-7] +"\t"+ str( int( timeToEnter ) ) + "\t" + str( int ( timeInRoom ) ) )
    
    print("---")
    for i in range( len( dateInSocialPokes ) ):
        dateInPoke = dateInSocialPokes[i]
        timeSinceStart = dateInPoke - startDate

        timeToEnter = timeBetweenSocialPokeAndEnter[i]
        timeInRoom = timeInSocial[i]
        
        print( "Social\t" + str( dateInPoke )[:-7] +"\t" + str( timeSinceStart )[:-7] +"\t"+ str( int( timeToEnter ) ) + "\t" + str( int ( timeInRoom ) ) )
    
    '''
    
    
    
    quit()
    