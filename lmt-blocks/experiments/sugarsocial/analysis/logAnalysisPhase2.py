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
        
        
        #print( dateIn )
    
        if "TIMEOUT: CLOSING SOCIAL GATE" in line:
            plt.axvline( dateIn, 2,3, color="red" )
            plt.text( dateIn, 3/2, "social TIMEOUT" , rotation=90, ha='right' , va='center' , size=4 )
            
        if "TIMEOUT: CLOSING SUGAR GATE" in line:
            plt.axvline( dateIn, 0,0.5, color="green" )
            plt.text( dateIn, 3/2, "sugar TIMEOUT" , rotation=90, ha='right' , va='center' , size=4 )

        if "nose poke social wrong" in line:
            plt.axvline( dateIn, color="red" )
            plt.text( dateIn, 3/2, "sugar TIMEOUT" , rotation=90, ha='right' , va='center' , size=4 )

        
        if "experiment" in line:
            if "social" in line:
                if "nose poke social wrong" in line:
                    plt.axvline( dateIn, 2,2.5, color="black" )
                    plt.text( dateIn, 3/2, "nose poke social wrong" , rotation=90, ha='right' , va='center' , size=4 )
                    socialWrong+=1
            
                if "nose poke social correct" in line:
                    plt.axvline( dateIn, 2,2.5, color="red" )
                    plt.text( dateIn, 3/2, "validated" , rotation=90, ha='right' , va='center' , size=4 )
                    socialOk+=1

            if "sugar" in line:
                if "nose poke sugar wrong" in line:
                    plt.axvline( dateIn, 0,0.5 ,color="black" )
                    plt.text( dateIn, 3/2, "nose poke sugar wrong" , rotation=90, ha='right' , va='center' , size=4 )
                    sugarWrong+=1
        
                if "validated" in line:
                    plt.axvline( dateIn, 0,0.5,color="green" )
                    plt.text( dateIn, 3/2, "nose poke sugar correct" , rotation=90, ha='right' , va='center' , size=4 )
                    sugarOk+=1
             
        
        if not "DeviceEvent" in line:
            if "[032] LOG ANIMAL BACK IN SIDE A" in line:  
        
                if "social gate" in line: 
                    plt.axvline( dateIn, color="red" )
                    dateOutSocial = dateIn
                    duration = dateOutSocial-dateInSocial
                    #plt.text( dateInSocial, 2.2, "social:"+str(duration)[:-7]+"s" , rotation=90, va='center' )
                    print( line )
                    print("Time in social:" , duration )
                    timeInSocial.append( duration.total_seconds() )
                
                if "sugar gate" in line: 
                    plt.axvline( dateIn, color="green" )
                    dateOutSugar = dateIn
                    duration = dateOutSugar-dateInSugar
                    #plt.text( dateInSugar, 0.5, "sugar:"+str(duration)[:-7]+"s" , rotation=90, va='center' )
                    timeInSugar.append( duration.total_seconds() )
    
            if "[012] LOG ANIMAL IS IN SIDE B" in line:  
        
                if "social gate" in line: 
                    plt.axvline( dateIn, color="red", linestyle='dashed' )
                    dateInSocial = dateIn
                    dateInSocialPokes.append( dateInSocialPoke )
                    delta = dateInSocial - dateInSocialPoke
                    timeBetweenSocialPokeAndEnter.append( delta.total_seconds() )
                
                if "sugar gate" in line: 
                    plt.axvline( dateIn, color="green" , linestyle='dashed' )
                    dateInSugar = dateIn
                    dateInSugarPokes.append( dateInSugarPoke )
                    delta = dateInSugar - dateInSugarPoke
                    timeBetweenSugarPokeAndEnter.append( delta.total_seconds() )
        
            
        if "Nose poke SUGAR" in line:            
    
            graph[( "NOSE POKE SUGAR","date")].append( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') )
            graph[( "NOSE POKE SUGAR","y")].append( 0.75 )
        
        if "Nose poke SOCIAL" in line:            
    
            graph[( "NOSE POKE SOCIAL","date")].append( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') )
            graph[( "NOSE POKE SOCIAL","y")].append( 1.75 )
        
        
        if "SUGAR GATE OPEN" in line:            
    
            graph[( "SUGAR","date")].append( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') )
            graph[( "SUGAR","y")].append( 1 )
            dateInSugarPoke = dateIn
            
            print( "sugar gate open")

        if "SOCIAL GATE OPEN" in line:            

            graph[( "SOCIAL","date")].append( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') )
            graph[( "SOCIAL","y")].append( 2 )
            dateInSocialPoke = dateIn
            

            print( "social gate open")
        
    print( ( sugarOk , sugarWrong ) )
    print( ( socialOk , socialWrong ) )
    
    
    plt.scatter( graph[("SUGAR","date")],graph[("SUGAR","y")], color="green" , s=5 , label="Sugar" )
    plt.scatter( graph[("SOCIAL","date")],graph[("SOCIAL","y")], color="red" , s=5 , label="Social" )    

    plt.scatter( graph[("NOSE POKE SUGAR","date")],graph[("NOSE POKE SUGAR","y")], color="green" , s=5, marker='^', label="Nose Poke Sugar" )
    plt.scatter( graph[("NOSE POKE SOCIAL","date")],graph[("NOSE POKE SOCIAL","y")], color="red" , s=5, marker='^', label="Nose Poke Social" )    

    #plt.legend()
    plt.ylim( 0 , 3 )
    plt.gcf().autofmt_xdate()
    title = "Sugar vs social chronogram"
    plt.title( title )
    plt.tight_layout()    
    plt.savefig( str( title )+".pdf")
    #plt.show()
    
    
    # display progression
    plt.clf()
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot( timeBetweenSocialPokeAndEnter )
    title = "Time between social poke and enter"
    plt.title( title )
    plt.ylabel( "seconds" )
    plt.xlabel( "trials" )
    plt.tight_layout()
    plt.savefig( file+" " +str( title )+".pdf")
    #plt.show()
    
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
    