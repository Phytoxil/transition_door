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
    

if __name__ == '__main__':
    
    file = 'gateLogJour3.txt'
        
    
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

    for line in lines:
        
        date = line[0:23]
        dateIn = dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
        print( dateIn )
    
        if "Application started" in line:
            plt.axvline( dateIn, color="black" )
            plt.text( dateIn, 1.5, "start\n" + str ( dateIn ), rotation=90, va='center' )
            startDate = dateIn
    
        if "[032] LOG ANIMAL BACK IN A DONE" in line:  
    
            if "Social Gate" in line: 
                plt.axvline( dateIn, color="red" )
                dateOutSocial = dateIn
                duration = dateOutSocial-dateInSocial
                plt.text( dateInSocial, 2.2, "social:"+str(duration)[:-7]+"s" , rotation=90, va='center' )
                timeInSocial.append( duration.total_seconds() )
            
            if "Sugar Gate" in line: 
                plt.axvline( dateIn, color="green" )
                dateOutSugar = dateIn
                duration = dateOutSugar-dateInSugar
                plt.text( dateInSugar, 0.5, "sugar:"+str(duration)[:-7]+"s" , rotation=90, va='center' )
                timeInSugar.append( duration.total_seconds() )

        if "[012] LOG A IN B DONE" in line:  
    
            if "Social Gate" in line: 
                plt.axvline( dateIn, color="red", linestyle='dashed' )
                dateInSocial = dateIn
                dateInSocialPokes.append( dateInSocialPoke )
                delta = dateInSocial - dateInSocialPoke
                timeBetweenSocialPokeAndEnter.append( delta.total_seconds() )
            
            if "Sugar Gate" in line: 
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
    plt.savefig( str( title )+".pdf")
    #plt.show()
    
    plt.clf()
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot( timeBetweenSugarPokeAndEnter )
    title = "Time between sugar poke and enter"
    plt.title( title )
    plt.ylabel( "seconds" )
    plt.xlabel( "trials" )
    plt.tight_layout()
    plt.savefig( str( title )+".pdf")
    #plt.show()
    
    plt.clf()
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot( timeInSocial )
    title = "Time in social"
    plt.title( title )
    plt.ylabel( "seconds" )
    plt.xlabel( "trials" )
    plt.tight_layout()
    plt.savefig( str( title )+".pdf")
    #plt.show()
    
    plt.clf()
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot( timeInSugar )
    title = "Time in sugar"
    plt.title( title )
    plt.ylabel( "seconds" )
    plt.xlabel( "trials" )
    plt.tight_layout()
    plt.savefig( str( title )+".pdf")
    #plt.show()
    
    
    # text summary:
    
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
    

    
    
    
    quit()
    timeBetweenSugarPokeAndEnter = []
    timeInSocial = []
    timeInSugar = []
    
    
    
    
    
    quit()
    
    
    graph = {}
    graph[("OPENED","date")] = []
    graph[("OPENED","y")] = []
    graph[("CLOSED","date")] = []
    graph[("CLOSED","y")] = []
    graph[("JAMMED_CLOSE","date")] = []
    graph[("JAMMED_CLOSE","y")] = []
    graph[("JAMMED_OPEN","date")] = []
    graph[("JAMMED_OPEN","y")] = []
    
    
    
    #2022-04-06 02:06:43.728: [RFID CHECK][LMT Block AutoGate] Animal allowed to cross: 001039048282
    
    '''
    mylist = ['nowplaying', 'PBS', 'PBS', 'nowplaying', 'job', 'debate', 'thenandnow']
    output = set()    
    for x in mylist:
        output.add(x)
    print(output)
    '''
    
    '''
    2022-04-07 10:23:14.609: [door A] DoorStatus.JAMMED_OPEN
    2022-04-07 10:23:15.522: [door A] JAMMED - Restart order: DoorOrder.OPEN
    2022-04-07 10:23:15.547: [door A] OPEN
    2022-04-07 10:23:16.930: [door A] DoorStatus.JAMMED_OPEN
    2022-04-07 10:23:17.922: [door A] JAMMED - Restart order: DoorOrder.OPEN
    2022-04-07 10:23:17.922: [door A] OPEN
    2022-04-07 10:23:19.329: [door A] DoorStatus.JAMMED_OPEN

    '''
    
    startTime = None
    endTime = None
    
    rfidOrder = []
    
    with open( file ) as f:
        lines = f.readlines()
    
    # RFID 
    
    rfidList = []
    for line in lines:
        if "allowed" in line:
            line = line.strip()
            rfid = line[-12:]
            rfidList.append( rfid )
    
    rfidList = list ( set ( rfidList ) ) 
    print( rfidList )
    
    timeInRoom = {}
    
    for rfid in rfidList:
        graph[( rfid + " in","date")] = []
        graph[( rfid + " in","y")] = []
        graph[( rfid + " out","date")] = []
        graph[( rfid + " out","y")] = []
        timeInRoom[ rfid ] = []
        
        
    for line in lines:
        if "allowed" in line:
            originalLine = line
            line = line.strip()
            rfid = line[-12:]
            date = line[0:23]
            
            nextLine = lines[lines.index(originalLine)+1]
            if "009" in nextLine:
                name = rfid+" in"
                lastIn = rfid
                dateIn = dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
            
            if "027" in nextLine:
                name = rfid+" out"
                
                dateOut = dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
                timeInRoom[rfid].append( (dateOut-dateIn).total_seconds() )
                rfidOrder.append( rfid )
                #print( "Substract: " , str((dateOut-dateIn)) )
                
                if lastIn != rfid:
                    print("ERROR")
                    quit()
                    
            
            graph[( name,"date")].append( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') )
            graph[( name,"y")].append( rfidList.index( rfid ) + 4 )
            
    
    '''
    # TO COMPUTE CHAINS:
    
    print("---")

    #rfidOrder
    chainSize = 5
    possibleOrder = list( itertools.permutations( rfidList, chainSize) )
    for order in possibleOrder:
        print( order )
        
    print( "---")
    
    # create list of breaked data:
    chunks= []
    for i in range ( len( rfidOrder )- chainSize ):
        chunks.append( rfidOrder[i:i+chainSize])
        
    for c in chunks:
        print ( c )
        
    find = {}
    for po in possibleOrder:
        find[po]=0
        for c in chunks:
            if checkListSame( po , c ):
                find[po]+=1
    
    print("---")
    sorted = dict(sorted(find.items(), key=lambda item: item[1], reverse=True ))   
    for f in sorted:
        print ( f ," :", find[f] ) 
    
    '''
    
    '''
    for i in range ( len( rfidOrder )- chainSize ):
        for a in range( chainSize ):
    '''
            
    
    
    
    
    '''
    # number of time in room
    for rfid in rfidList:
        print( rfid, len( timeInRoom[rfid] ) )
    '''
    # number of time in room
    for rfid in rfidList:
        print( rfid, numpy.mean( timeInRoom[rfid] ) )
            
    
    '''
    if True:
        # plot time in room
        data = []
        for rfid in rfidList:
            data.append( timeInRoom[rfid] )   
        
        plt.boxplot( data )
        plt.xticks([1, 2, 3,4,5,6], rfidList)
        plt.ylabel("number of seconds in room")
        plt.xlabel("animals' rfid")
        plt.legend()
        plt.show()
        quit()
    '''
       
    #quit()
    
    # open close        
    nbJam = 0
    nbJamMax = 0
    nbJamClose = 0
    nbJamOpen = 0
    
    for line in lines:
        index = lines.index(line)
        line = line.strip()
        print ( line )
        
        if startTime == None:
            date = line[0:23]
            startTime = dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
        endTime = dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
        
        if "OPENED" in line:
            date = line[0:23]
            graph[("OPENED","date")].append( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') )
            graph[("OPENED","y")].append( 1 )
            nbJam=0
            
        if "CLOSED" in line:
            date = line[0:23]
            graph[("CLOSED","date")].append( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') )
            graph[("CLOSED","y")].append( 2 )
            nbJam=0        
        
        if "DoorStatus.JAMMED_CLOSE" in line:
            try:
                if "DoorStatus.JAMMED_CLOSE" in lines[index+3]:            
                    date = line[0:23]
                    graph[("JAMMED_CLOSE","date")].append( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') )
                    graph[("JAMMED_CLOSE","y")].append( 2.1 )
                    nbJam+=1
                    nbJamClose+=1
            except:
                pass
            
        if "DoorStatus.JAMMED_OPEN": # in line and "door A" in line:
            
            try:
                if "DoorStatus.JAMMED_OPEN" in lines[index+3]:            
                    date = line[0:23]
                    graph[("JAMMED_OPEN","date")].append( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') )
                    graph[("JAMMED_OPEN","y")].append( 1.1 )
                    nbJam+=1
                    nbJamOpen+=1
            except:
                pass
        
        nbJamMax= max ( nbJamMax , nbJam )
        
            
    #plt.scatter( dt.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f') , 1 , color = "green")
    #print( date, ":" , line )
        
    print( "Nb Jam max: " , nbJamMax )
    print( "Nb Jam open: " , nbJamOpen )
    print( "Nb Jam close: " , nbJamClose )
    
    print( "Total duration: " , ( endTime - startTime ))
    
    #dates = ['01/02/1991','01/03/1991','01/04/1991']
    #x = [dt.datetime.strptime(d,'%Y-%m-%d %H:%M:%S.%f').datetime() for d in dates]
    
    
    plt.scatter(graph[("OPENED","date")],graph[("OPENED","y")], color="green" , s=0.5 , label="Opened" )
    plt.scatter(graph[("CLOSED","date")],graph[("CLOSED","y")], color="red" , s = 0.5 , label="Closed")

    plt.scatter(graph[("JAMMED_OPEN","date")],graph[("JAMMED_OPEN","y")], color="darkgreen" , s=0.5 , label="Jammed Open" )
    plt.scatter(graph[("JAMMED_CLOSE","date")],graph[("JAMMED_CLOSE","y")], color="darkred" , s = 0.5 , label="Jammed Close")
    
    
    for rfid in rfidList:
        plt.scatter(graph[( rfid+" in" ,"date")],graph[( rfid+" in" ,"y")], s=5, marker=">", label=rfid +" in")

    for rfid in rfidList:
        plt.scatter(graph[( rfid+" out" ,"date")],graph[( rfid+" out" ,"y")], s=5, marker="<", label=rfid + "out" )
        
    plt.legend()
    
    plt.gcf().autofmt_xdate()
    plt.show()