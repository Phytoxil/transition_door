import datetime
import json
import logging
import socket
import sys
import traceback
import unittest
from threading import Thread
from time import sleep
from unittest.mock import MagicMock, Mock

# class VideoMouseTracker(BaseMouseTracker):
#
#     def __init__(self):
#         self._logger = create_logger(self)
#
#     @property
#     def logger(self) -> Logger:
#         return self._logger
from dependency_injector import providers

from container import LocalDeviceContainer
from events import TransitionEvent, DateTimeEncoder
from transition_doors.local_transition_doors import LocalTransitionDoorsDevice
# from device.remote_transition_doors import RemoteTransitionDoors
from mqtt_device.common.mqtt_client import MQTTClient
from mqtt_device.local.client import LocalClient
from mqtt_device.remote.client import ApplicationClient
from mqtt_device.tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer
from remote_application.remote_transition_doors import RemoteTransitionDoors
from transition_doors import FakeSasDoor


local_ip: str = None


def excepthook(type_, value, traceback_):
    traceback.print_exception(type_, value, traceback_)

class TestLocalTransitionDoors(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global local_ip

        logging.root.setLevel(logging.INFO)
        # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)
        # create_logger(self)



    def test_LocalTransitionDoorsDevice(self) -> None:

        application_container = LocalDeviceContainer()
        application_container.config.from_ini("../../tests/resources/config.ini")


        application_container.gate_enter.sas_door.override(
            providers.Singleton(
                FakeSasDoor,
                room_a="LMT",
                room_b="BLACK_BOX")
        )

        application_container.gate_exit.sas_door.override(
            providers.Singleton(
                FakeSasDoor,
                room_a="BLACK_BOX",
                room_b="LMT")
        )

        transition_doors = application_container.transition_doors()
        transition_doors.start()

        transition_doors.add_authorized_rfid("123465")

        sas_enter: FakeSasDoor = transition_doors.sas_enter
        sas_exit: FakeSasDoor = transition_doors.sas_exit

        def run_transition():
            sas_enter.fake_mouse_move_from_to(rfid="123465", from_room="BLACK_BOX", to_room="LMT")
            sleep(0.1)

            expected = '{"rfid": "123465", "from_room": "BLACK_BOX", "to_room": "LMT"}'
            mock_prop_cb.assert_called_with(local.transition, None, expected)


        mock_mqtt = MagicMock()
        client = LocalClient(environment_name="souris city", id_env="01", client_id="application", mqtt_client=mock_mqtt)

        local = LocalTransitionDoorsDevice(transition_doors=transition_doors, device_id="transition_doors")
        # client.add_local_device(local)

        mock_prop_cb = MagicMock()
        local.transition.value_changed += mock_prop_cb

        thread = Thread(target=run_transition)
        thread.start()

        print("OK")
        # sleep(1000)

    def test_RemoteTransitionDoors_on_transition_send_event(self):

        mock_client = MagicMock()

        device = RemoteTransitionDoors(device_id="trans_door_1")
        device._client = mock_client

        mouse_moved_cb = MagicMock()

        device.mouse_moved.register(mouse_moved_cb)

        date = datetime.datetime(2010, 3, 1, 10, 3, 52)

        ts = date.timestamp()

        rev_date = datetime.date.fromtimestamp(ts)

        event_dict = {"id_device": device.device_id, "timestamp": date.timestamp(), "rfid": "123465", "from_room": "HELL", "to_room": "PARADISE"}
        json_str = json.dumps(event_dict)
        device.on_transition(sender=Mock(), old=None, new=json_str)

        expected = TransitionEvent(id_device=device.device_id, timestamp=date.timestamp(), rfid="123465", from_room="HELL", to_room="PARADISE")

        mouse_moved_cb.assert_any_call(sender=device, event=expected)

    def test_json_dump_transition_event(self):
        date = datetime.datetime(2010, 3, 1, 10, 3, 52)

        event = TransitionEvent(id_device="my_id", timestamp=date.timestamp(), rfid="123465", from_room="HELL", to_room="PARADISE")

        res = json.dumps(event.__dict__, cls=DateTimeEncoder)

        print("ok")
    def test_device_container(self):
        sys.excepthook = excepthook

        application_container = LocalDeviceContainer()
        application_container.config.from_ini("../../tests/resources/config.ini")

        # mqtt = application_container.mqtt_client()
        client = application_container.local_client()

        print("OK")


    def run_local_client(self) -> None:
        mqtt_client = MQTTClient(broker_ip=local_ip)
        # client = mqtt_client
        # mqtt_client.connect()

        application_container = LocalDeviceContainer()
        application_container.config.from_ini("../../tests/resources/config.ini")

        application_container.gate_enter.sas_door.override(
            providers.Singleton(
                FakeSasDoor,
                room_a="LMT",
                room_b="BLACK_BOX",
                fake_gate=Mock()
                )
        )

        application_container.gate_exit.sas_door.override(
            providers.Singleton(
                FakeSasDoor,
                room_a="BLACK_BOX",
                room_b="LMT",
                fake_gate=Mock()
            )
        )

        client = LocalClient(environment_name="souris_city", id_env="01", client_id="local_client", mqtt_client=mqtt_client)
        client.connect()

        transition_doors = application_container.transition_doors()
        transition_doors.start()

        local = LocalTransitionDoorsDevice(transition_doors=transition_doors, device_id="transition_doors")
        client.add_local_device(local)


        sas_enter: FakeSasDoor = transition_doors.sas_enter
        sas_exit: FakeSasDoor = transition_doors.sas_exit

        sas_enter.authorize_access(from_room="BLACK_BOX", to_room="LMT")
        sas_exit.authorize_access(from_room="LMT", to_room="BLACK_BOX")

        sleep(5)
        sas_enter.fake_mouse_move_from_to("13245", "BLACK_BOX", "LMT")
        sleep(1)
        sas_enter.fake_mouse_move_from_to(rfid="123465", from_room="BLACK_BOX", to_room="LMT")
        sleep(0.1)
        sas_enter.fake_mouse_move_from_to(rfid="123888", from_room="BLACK_BOX", to_room="LMT")
        sleep(0.1)
        sas_enter.fake_mouse_move_from_to(rfid="0123456", from_room="BLACK_BOX", to_room="LMT")
        sleep(0.1)
        sas_exit.fake_mouse_move_from_to(rfid="123465", from_room="LMT", to_room="BLACK_BOX")
        sleep(0.1)
        sas_enter.fake_mouse_move_from_to(rfid="99999", from_room="BLACK_BOX", to_room="LMT")

        transition_doors.is_ended.wait()

    def test_tmp(self):
        str_array = '[\'13245\']'

        res = list()

    def test_local_remote_functionnal_test(self) -> None:

        mosquitto = FakeMosquittoServer(ip=local_ip, kill_if_exists=True, verbose=False)
        mosquitto.start()

        # sys.excepthook = excepthook


        thread = Thread(target=self.run_local_client, name="local device")
        thread.start()
        # thread.join()


        mqtt_client = MQTTClient(broker_ip=local_ip)
        application_client = ApplicationClient(environment_name="souris_city", id_env="01", client_id="application",
                                               mqtt_client=mqtt_client)

        application_client.connect()
        sleep(0.1)
        print("OK")
        # sleep(0.1)
        remote_client = application_client.get_remote_client(client_id="local_client")

        remote_device: RemoteTransitionDoors = remote_client.get_remote_device(device_id="transition_doors").as_type(RemoteTransitionDoors)
        sleep(1)
        remote_device.set_allowed_rfid('13245')
        remote_device.set_allowed_rfid('123465')
        remote_device.set_allowed_rfid('123888')

        def on_mouse_moved(sender: RemoteTransitionDoors, event: TransitionEvent):
            print(f"################## MOUSE '{event.rfid}' moved from '{event.from_room}' to room '{event.to_room}'")

        remote_device.mouse_moved.register(on_mouse_moved)

        application_client.mqtt_client.wait_until_ended()




if __name__ == '__main__':
    unittest.main()
