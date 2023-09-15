'''
Created on 9 mars 2023

@author: Fab
'''
import socket

def LMT_sendRFIDInArea( rfid , enable ):
    # will send an RFID to the arena to tell which RFID has been through
    # enable > will send that the animal is entering the arena
    
    UDP_IP = "127.0.0.1"
    UDP_PORT = 8553
    
    command = f" put the name of the gate here for easy debug : rfid"
    if enable:
        command +=" in"
    if not enable:
        command +=" out"
        
    command+=f" *{rfid}*"
    
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(bytes( command  , "utf-8"), (UDP_IP, UDP_PORT))

if __name__ == '__main__':

    
    LMT_sendRFIDInArea( "001043406195" , enable=True )
    LMT_sendRFIDInArea( "001043406139" , enable=True )
    LMT_sendRFIDInArea( "12345678910A" , enable=True )
    
    #LMT_sendRFIDInArea( "825611" , enable=True )
    
    print("done")
    