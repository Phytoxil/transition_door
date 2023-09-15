import logging
import sys
import traceback
import unittest
from threading import Thread
from time import sleep
from unittest.mock import patch

import PyQt5.QtWidgets as QtWidgets
from PyQt5 import QtCore

# from blocks.autogate.Gate import Gate
from dependency_injector import providers

from blocks import Gate
from container import LocalDeviceContainer
from transition_doors.presentation.LMTVisualExperiment6 import WWVisualExperiment
from transition_doors.presentation.gate_view import GatePresenter, GateViewImpl
from transition_doors.presentation.transition_doors import TransitionDoorsViewImpl, TransitionDoorsPresenter
from transition_doors import GateWrapper, TransitionDoors, FakeSasDoor


def excepthook(type_, value, traceback_):
    traceback.print_exception(type_, value, traceback_)
    QtCore.qFatal('')

class TestPresentation(unittest.TestCase):

    def test_lmt_visual_experiment(self):
        # experiment = LMTVisualExperiment6()


        application_container = LocalDeviceContainer()
        application_container.config.from_ini("./resources/config.ini")

        application_container.gate_enter.sas_door.override(
            providers.Singleton(
                FakeSasDoor,
                room_a="LMT",
                room_b="BLACK_ROOM",
                position="right"
            )
        )

        application_container.gate_exit.sas_door.override(
            providers.Singleton(
                FakeSasDoor,
                room_a="LMT",
                room_b="BLACK_ROOM",
                position="left"
            )
        )

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


        with patch('blocks.autogate.Gate.AntennaRFID') as mockAntenna, \
                patch('blocks.autogate.Gate.Door') as mockDoor, \
                patch('blocks.autogate.Gate.MotorManager') as mockMotor, \
                patch('blocks.autogate.Gate.ArduinoReader') as mockArduino:



            transition_doors = application_container.transition_doors()
            transition_doors.start()

            app = QtWidgets.QApplication([])

            app.aboutToQuit.connect(exitHandler)

            sas_enter: GateWrapper = transition_doors.sas_enter
            sas_exit: GateWrapper = transition_doors.sas_exit

            visualExperiment = WWVisualExperiment(transition_doors=transition_doors)
            visualExperiment.start()
            visualExperiment.show()

            # thread = Thread(target=run)
            # thread.start()

            sys.exit(app.exec_())

            print("ok")

    def test_transition_door_presenter(self):
        app = QtWidgets.QApplication(sys.argv)

        main_window = QtWidgets.QMainWindow()

        view = TransitionDoorsViewImpl()

        with patch('blocks.autogate.Gate.AntennaRFID') as mockAntenna, \
                patch('blocks.autogate.Gate.Door') as mockDoor, \
                patch('blocks.autogate.Gate.MotorManager') as mockMotor, \
                patch('blocks.autogate.Gate.ArduinoReader') as mockArduino:

            sas_enter = FakeSasDoor(room_a="HELL", room_b="PARADISE")
            sas_exit = FakeSasDoor(room_a="HELL", room_b="PARADISE")

            transition_doors = TransitionDoors(sas_enter=sas_enter, sas_exit=sas_exit, limited_room="PARADISE", other_room="HELL", max_number=3)
            presenter = TransitionDoorsPresenter(transition_doors=transition_doors, view=view)

            main_window.setWindowTitle("My Test App")
            main_window.setCentralWidget(view)
            # main_window.resize(500, 600)
            main_window.show()

            def run_test():
                sleep(1)
                sas_enter.fake_mouse_move_from_to(rfid="1", from_room="HELL", to_room="PARADISE")
                sleep(1)
                sas_exit.fake_mouse_move_from_to(rfid="1", from_room="PARADISE", to_room="HELL")
                sleep(1)
                sas_enter.fake_mouse_move_from_to(rfid="3", from_room="HELL", to_room="PARADISE")
                sleep(1)
                sas_enter.fake_mouse_move_from_to(rfid="4", from_room="HELL", to_room="PARADISE")

            thread = Thread(target=run_test)
            thread.start()

            app.exec_()


    def test_gate_presenter(self):
        app = QtWidgets.QApplication(sys.argv)
        # app.setStyleSheet(stylesheet)

        main_window = QtWidgets.QMainWindow()

        view = GateViewImpl()

        with patch('blocks.autogate.Gate.AntennaRFID') as mockAntenna, \
                patch('blocks.autogate.Gate.Door') as mockDoor, \
                patch('blocks.autogate.Gate.MotorManager') as mockMotor, \
                patch('blocks.autogate.Gate.ArduinoReader') as mockArduino:

            gate = Gate(
                COM_Servo="COM5",
                COM_Arduino="COM3",
                COM_RFID="COM4",
                name="First Gate",
                weightFactor=0.74)

            presenter = GatePresenter(sas_door=GateWrapper(gate=gate, room_a="HELL", room_b="PARADISE"), view=view)

            main_window.setWindowTitle("My Test App")
            main_window.setCentralWidget(view)
            # main_window.resize(500, 600)
            main_window.show()
            app.exec_()


if __name__ == '__main__':
    unittest.main()
