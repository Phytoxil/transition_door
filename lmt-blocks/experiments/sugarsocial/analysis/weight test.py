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
    
    file = 'gateLog3.txt'
        
    
    with open( file ) as f:
        lines = f.readlines()
    
    
    sugarW = []
    socialW = []
    
    for line in lines:

        date = line[0:23]
        dateIn = dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
        
    
        
        
        if "CheckForOneAnimalLogic" in line and "WEIGHT OK" in line:  
    
            currentList= sugarW
            if "social" in line:
                currentList = socialW 
            
            w = float ( line.split(" ")[-1] ) #social gate CheckForOneAnimalLogic WEIGHT OK: 28.5
            currentList.append( w )
           

    
    # display progression
    plt.clf()
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot( sugarW , label="sugar gate" )
    plt.plot( socialW , label="social gate" )
    title = "Weight in gate"
    plt.title( title )
    plt.ylabel( "grams" )
    plt.xlabel( "measure in gate" )
    plt.legend()
    plt.tight_layout()
    plt.savefig( str( title )+".pdf")
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
    