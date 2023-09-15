'''
Created by Nicolas Torquet at 19/04/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''


from dynamixel_sdk.port_handler import PortHandler
from dynamixel_sdk.packet_handler import PacketHandler
import serial
from blocks.DeviceEvent import DeviceEvent
import threading
from time import sleep


class Fed3Manager3(object):

    def __init__(self, comPort="COM79", name="Fed3"):

        self.name = name
        self.comPort = comPort
        self.serialPort = serial.Serial(port=comPort, baudrate=115200, bytesize=8, timeout=.1)

        self.nbRight = 0
        self.nbLeft = 0

        self.deviceListenerList = []
        self.enabled = True

        self.readThread = threading.Thread(target=self.read, name=f"FED Thread - {self.comPort}")
        self.readThread.start()

    def getFedName(self):
        return self.name

    def stop(self):
        self.enabled = False

    def read(self):

        while (self.enabled):

            if self.serialPort.in_waiting > 0:
                serialString = self.serialPort.readline().decode("Ascii")
                serialString = serialString.strip()

                # print( serialString )
                if serialString == "rightIn":
                    self.nbRight += 1
                    self.fireEvent(DeviceEvent("fed3", self, "nose poke", data="right"))

                if serialString == "leftIn":
                    self.nbLeft += 1
                    self.fireEvent(DeviceEvent("fed3", self, "nose poke", data="left"))

                # print( self )
                # return serialString
                # sleep( 0.05 )

    def feed(self):
        self.send("feed")
        self.fireEvent(DeviceEvent("fed3", self, "feed"))

    def click(self):
        self.send("click")
        self.fireEvent(DeviceEvent("fed3", self, "click"))

    def light(self , direction = "" ):
        txt = "light"
        if "right" in direction:
            txt="lightright"
        if "left" in direction:
            txt="lightleft"
        self.send( txt )
        self.fireEvent( DeviceEvent( "fed3", self, txt ) )


    def controlLight(self, instruction):
        '''
        instruction must be like: RGBWdef_R000_G100_B100_W100_SideL
        RGBWdef_ : mandatory at the beginning of the instruction
        Rxxx : Red color with its intensity from 0 until 100
        Gxxx : Green color with its intensity from 0 until 100
        Bxxx : Blue color with its intensity from 0 until 100
        Wxxx : White color with its intensity from 0 until 100
        SideX: L for left, R for right, b for both
        '''
        self.send(instruction)
        self.fireEvent(DeviceEvent("fed3", self, instruction))


    def lightoff(self):
        self.send("lightoff")
        self.fireEvent(DeviceEvent("fed3", self, "lightoff"))

    def clickflash(self):
        self.send("clickflash")
        self.fireEvent(DeviceEvent("fed3", self, "clickflash"))

    def send(self, message):
        self.serialPort.write(message.encode("utf-8"))

    def fireEvent(self, deviceEvent):
        for listener in self.deviceListenerList:
            listener(deviceEvent)

    def addDeviceListener(self, listener):
        self.deviceListenerList.append(listener)

    def removeDeviceListener(self, listener):
        self.deviceListenerList.remove(listener)

    def __str__(self, *args, **kwargs):
        return self.name + ": nbLeft: " + str(self.nbLeft) + " nbRight: " + str(self.nbRight)





