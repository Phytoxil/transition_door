import logging
import socket
import sys
import traceback
import unittest
from pathlib import Path

from PyQt5 import QtCore, QtWidgets
from mqtt_device.common.mqtt_client import MQTTClient
from mqtt_device.local.client import LocalClient

# from container import LocalDeviceContainer, LocalSingleDoorContainer
# from events import TransitionEvent
import start_single_gate_device
from transition_doors.container import LocalSingleDoorContainer
from transition_doors.local_transition_doors import LocalTransitionDoorsDevice
from transition_doors.presentation.LMTVisualExperimentSingle import WWVisualExperiment
from transition_doors.single_mouse_sas import SingleMouseSas
# from transition_doors import FakeSasDoor, GateWrapper
from transition_doors.transition_doors import FakeSasDoor, GateWrapper

local_ip: str = None

def excepthook(type_, value, traceback_):
    traceback.print_exception(type_, value, traceback_)
    QtCore.qFatal('')

class TestSingleMouseSas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        global local_ip

        logging.root.setLevel(logging.INFO)
        # # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)
        # create_logger(self)

    def test_single_mouse_with_fake_sas(self):

        sas_door = FakeSasDoor(room_a="WATER", room_b="BLACK_BOX")

        mouse_sas = SingleMouseSas(sas_door=sas_door, limited_room="WATER", other_side_room="BLACK_BOX")
        mouse_sas.add_authorized_rfid("12345")

        mouse_sas.start()

        sas_door.authorize_access(from_room="WATER", to_room="BLACK_BOX")

        sas_door.fake_mouse_move_from_to(rfid="12345", from_room="WATER", to_room="BLACK_BOX")

        # sas_door.mouse_moved(event=TransitionEvent(id_device="device", timestamp=datetime.datetime.now().timestamp(), weight=1.123, rf))
        # sas_door.mouse_moved(TransitionEvent(id_device="toto", timestamp=datetime.datetime.now().timestamp(), weight=1.456, rfid="13456", from_room="WATER", to_room="BLACK_BOX"))


    def test_single_mouse_with_real_sas(self):
        # com_servo = COM8
        # com_arduino = COM7
        # com_rfid = COM6
        com_servo = "COM23"
        com_arduino = "COM22"
        com_rfid = "COM21"

        # com_servo = "COM5"
        # com_arduino = "COM4"
        # com_rfid = "COM3"


        sas_door = GateWrapper(room_a="WATER", room_b="BLACK_BOX", COM_Servo=com_servo, COM_RFID=com_rfid, COM_Arduino=com_arduino,
                               name="LMT Block AutoGate",
                               weightFactor=0.74,  # 0.74
                               mouseAverageWeight=20,
                               enableLIDAR=True
                               )

        mouse_sas = SingleMouseSas(sas_door=sas_door, limited_room="WATER", other_side_room="BLACK_BOX")
        # mouse_sas.add_authorized_rfid("12345")

        mouse_sas.start()

        mouse_sas.enabled = True

        # mouse_sas.sas_door.authorize_access(from_room="WATER", to_room="BLACK_BOX")
        # mouse_sas.sas_door.authorize_access(from_room="BLACK_BOX", to_room="WATER")
        # sas_door.authorize_access(from_room="WATER", to_room="BLACK_BOX")

        # sas_door.fake_mouse_move_from_to(rfid="12345", from_room="WATER", to_room="BLACK_BOX")

        # sas_door.mouse_moved(event=TransitionEvent(id_device="device", timestamp=datetime.datetime.now().timestamp(), weight=1.123, rf))
        # sas_door.mouse_moved(TransitionEvent(id_device="toto", timestamp=datetime.datetime.now().timestamp(), weight=1.456, rfid="13456", from_room="WATER", to_room="BLACK_BOX"))

        sas_door.is_ended.wait()

    def test_container_single(self):
        application_container = LocalSingleDoorContainer()
        application_container.config.from_ini("./resources/config.ini")

    def test_start_single_mouse(self):
        path = Path(r"C:\Users\Nicolas\Desktop\transition_door\single_config.ini")
        start_single_gate_device.init(path)


    def test_single_lmt_visual_experiment(self):
        # experiment = LMTVisualExperiment6()


        application_container = LocalSingleDoorContainer()
        application_container.config.from_ini("./resources/single_config.ini")

        # application_container.gate.sas_door.override(
        #     providers.Singleton(
        #         FakeSasDoor,
        #         room_a="LMT",
        #         room_b="BLACK_ROOM"
        #     )
        # )

        # application_container.gate_enter.sas_door.override(
        #     providers.Singleton(
        #         FakeSasDoor,
        #         room_a="LMT",
        #         room_b="BLACK_ROOM",
        #         position="right"
        #     )
        # )

        # application_container.gate_exit.sas_door.override(
        #     providers.Singleton(
        #         FakeSasDoor,
        #         room_a="LMT",
        #         room_b="BLACK_ROOM",
        #         position="left"
        #     )
        # )

        mqtt_client = MQTTClient(broker_ip=local_ip)
        local_client = LocalClient(client_id="some_client", environment_name="souris_city", id_env="01", mqtt_client=mqtt_client)
        local_client.connect()

        transition_doors = application_container.transition_doors()
        transition_doors.start()

        local_door = LocalTransitionDoorsDevice(transition_doors=transition_doors, device_id="SINGLE")
        local_door.start()

        local_client.add_local_device(local_door)

        # client = LocalClient(environment_name="souris city", id_env="01", client_id="local_client", mqtt_client=mqtt_client)
        # client.connect()



        sys.excepthook = excepthook

        # setup logfiles
        # logFile = "testLog - " + datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + ".log.txt"
        # print("Logfile: ", logFile)
        # logging.basicConfig(level=logging.INFO, filename=logFile, format='%(asctime)s.%(msecs)03d: %(message)s',
        #                     datefmt='%Y-%m-%d %H:%M:%S')
        # logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logging.info('Application started')

        def exitHandler():
            visualExperiment.stop()


        # def run():
        #
        #     sas_enter.gate.currentWeight = 30


        # with patch('blocks.autogate.Gate.AntennaRFID') as mockAntenna, \
        #         patch('blocks.autogate.Gate.Door') as mockDoor, \
        #         patch('blocks.autogate.Gate.MotorManager') as mockMotor, \
        #         patch('blocks.autogate.Gate.ArduinoReader') as mockArduino:



        # transition_doors = application_container.transition_doors()
        # transition_doors.start()

        app = QtWidgets.QApplication([])

        app.aboutToQuit.connect(exitHandler)

        # sas_enter: GateWrapper = transition_doors.sas_enter
        # sas_exit: GateWrapper = transition_doors.sas_exit

        visualExperiment = WWVisualExperiment(transition_doors=transition_doors)
        visualExperiment.start()
        visualExperiment.show()

        # thread = Thread(target=run)
        # thread.start()

        sys.exit(app.exec_())

        print("ok")


    def test_mqtt_single_door(self):

        com_servo = "COM23"
        com_arduino = "COM22"
        com_rfid = "COM21"

        sas_door = GateWrapper(room_a="WATER", room_b="BLACK_BOX", COM_Servo=com_servo, COM_RFID=com_rfid, COM_Arduino=com_arduino,
                               name="LMT Block AutoGate",
                               weightFactor=0.74,  # 0.74
                               mouseAverageWeight=20
                               )

        mouse_sas = SingleMouseSas(sas_door=sas_door, limited_room="WATER", other_side_room="BLACK_BOX")
        mouse_sas.start()
        mouse_sas.enabled = True


        mqtt_client = MQTTClient(broker_ip=local_ip)
        local_client = LocalClient(client_id="some_client", environment_name="souris_city", id_env="01", mqtt_client=mqtt_client)

        local_client.connect()

        local_door = LocalTransitionDoorsDevice(transition_doors=mouse_sas, device_id="SINGLE")
        local_door.start()

        local_client.add_local_device(local_door)


        mqtt_client.wait_until_ended()
        # mouse_sas.is_ended.wait()


if __name__ == '__main__':
    unittest.main()
