'''
Created on 18 mars 2023

@author: LMT_11
'''
from blocks.autogate.Gate import Gate
import socket

'''

     
     
     def LMT_sendRFIDInfoForArea( self, ip, rfid , enable ):
        # will send an RFID to the arena to tell which RFID has been through
        # enable > will send that the animal is entering the arena
        
        UDP_IP = ip
        UDP_PORT = 8553
        
        command = f" gate name: {self.name} : rfid"
        if enable:
            command +=" in"
        if not enable:
            command +=" out"
            
        command+=f" *{rfid}*"
        
        print(f"Sending command to LMT at {ip} for RFID identity presence: {command}" )
                
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.sendto(bytes( command  , "utf-8"), (UDP_IP, UDP_PORT))
        
'''
if __name__ == '__main__':
    command = "rfid out *001043406171*" 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(bytes( command  , "utf-8"), ("127.0.0.1", 8553))
        
    #Gate.LMT_sendRFIDInfoForArea( None, "127.0.0.1", "001043406171", False )
