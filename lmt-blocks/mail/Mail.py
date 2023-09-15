'''
Created on 7 juin 2022

@author: Fab
'''

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from random import randint
from smtplib import SMTPSenderRefused
from threading import Thread
import logging
    

class LMTMail:

    def __init__(self):
        self.port = 465
        self.smtp_server_domain_name = "smtp.gmail.com"
        self.sender_mail = "livemousetracker@gmail.com"
        self.password = "kuvl smzd jxvk gtyd"

    def sendInfo(self , emails, subject, content, files = None):
        subject = "[LMT-AUTO][Info] "+ subject
        self.sendThreaded(emails, subject, content, files)                
    
    def sendAlert(self , emails, subject, content, files = None):
        subject = "[LMT-AUTO][Alert] "+ subject
        self.sendThreaded(emails, subject, content, files)
    
    def sendThreaded( self , emails, subject, content, files = None):
        thr = Thread(target=self.send, args=[emails, subject, content , files])
        thr.start()

    def send(self, emails, subject, content , files = None ):
                
        ssl_context = ssl.create_default_context()
        
        try:
            service = smtplib.SMTP_SSL(self.smtp_server_domain_name, self.port, context=ssl_context)
        except Exception as e:
            logging.info("Mailing error (no internet ?):" + str( e ))
            return False
            
        service.login(self.sender_mail, self.password)
        
        #for email in emails:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender_mail
        msg['To'] = ", ".join( emails )
        
        msg.attach(MIMEText(content))

        
        # attach files
        if files!=None:
            for file_path in files:
                
                mimeBase = MIMEBase("application", "octet-stream")
                with open(file_path, "rb") as file:
                    mimeBase.set_payload(file.read())
                encoders.encode_base64(mimeBase)
                mimeBase.add_header("Content-Disposition", f"attachment; filename={Path(file_path).name}")
                msg.attach(mimeBase)
        
        # send mail
        try:
            result = service.sendmail(self.sender_mail, emails, msg.as_string() )
        except SMTPSenderRefused as e :
            # file too big
            logging.info("Mailing error:"+str(e))
            
        except Exception as e:
            logging.info("Mailing error:" + str( e ))
            


        service.quit()
        return True


if __name__ == '__main__':
    
    
    #"eye@igbmc.fr",
    #"benoit.forget@pasteur.fr"
    mails = ["fabrice.de.chaumont@gmail.com","eye@igbmc.fr"]
    subject = "Test mail"+ str( randint(0,1000) ) 
    

    content = "Animals are ready to leave arena\n"
    content += "\n"
    content += "Test\n"
    content += "\n"
    content += "click here to open all gates : http://action.thisisastest.com?openAllGates"
    content += "\n"
    content += "Animals RFID: 45654564, 56465456, 456465466\n"
    content += "\n"
    content += "This is an automatic message from livemousetracker@gmail.com"
    
    
    mail = LMTMail( )
    files = [ "poney.jpg","fakelog.txt" ]
    
    print("Sending ...")
    # without thread
    #mail.send(mails, subject, content , files )
    
    mail.sendInfo(mails, subject, content , files )
    
    #with thread
    '''
    thr = Thread(target=mail.sendInfo, args=[mails, subject, content , files])
    thr.start()
    '''    

    print("ok")