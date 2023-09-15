import datetime
import re
from abc import abstractmethod
from logging import Logger
from threading import Event, Lock
from typing import Tuple, Callable, List
from unittest.mock import MagicMock

from mqtt_device.common.common_log import create_logger
from mqtt_device.event_handler import EventHandler
from blocks import DeviceEvent as fab_event

# from blocks.DeviceEvent import DeviceEvent
from blocks.DeviceEvent import DeviceEvent
from blocks.autogate.Gate import GateOrder, Gate, GateMode
from blocks.autogate.Parameters import OPENED_DOOR_POSITION_MOUSE, CLOSED_DOOR_POSITION_MOUSE
from transition_doors.events import TransitionEvent, StartedEvent, OrdersDoneEvent
from transition_doors.remote_transition_doors import ITransitionDoors


class TransitionDoorsException(Exception):
    pass


# USEFULL? ... not yet ;p
class IGate:


    @property
    @abstractmethod
    def COM_Servo(self) -> str:
        pass

    @property
    @abstractmethod
    def COM_Arduino(self) -> str:
        pass

    @property
    @abstractmethod
    def COM_RFID(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def weight_factor(self) -> float:
        pass

    @property
    @abstractmethod
    def mouseAverageWeight(self) -> int:
        pass

    @abstractmethod
    def addDeviceListener(self, listener: Callable[[DeviceEvent], None]):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def setOrder(self, order: GateOrder, noOrderAtEnd: bool):
        pass

    @abstractmethod
    def getOrder(self) -> GateOrder:
        pass


class FakeGate(IGate):


    @property
    def COM_Servo(self) -> str:
        pass

    @property
    def COM_Arduino(self) -> str:
        pass

    @property
    def COM_RFID(self) -> str:
        pass

    @property
    def name(self) -> str:
        pass

    @property
    def weight_factor(self) -> float:
        pass

    @property
    def mouseAverageWeight(self) -> int:
        pass

    def addDeviceListener(self, listener: Callable[[DeviceEvent], None]):
        pass

    def stop(self):
        pass

    def setOrder(self, order: GateOrder, noOrderAtEnd: bool):
        pass

    def getOrder(self) -> GateOrder:
        pass

class AbstractTransitionDoors(ITransitionDoors):


    def __init__(self, limited_room: str, other_room: str,
                 max_number: int, device_id: str = "None"):
        self._logger = create_logger(self)
        # self.sas_enter = sas_enter
        # self.sas_exit = sas_exit
        self._limited_room = limited_room
        self._other_side_room: str = other_room
        self._max_number = max_number
        self._device_id = device_id

        self._nb_mice_in_limited = 0

        # self.is_ended: Event = Event()
        self._lock: Lock = Lock()

        self._mouse_moved: EventHandler[TransitionEvent] = EventHandler(self)
        # self.started: EventHandler[StartedEvent] = EventHandler(self)
        # self._enabled = False
        # self._is_initialized = False

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def limited_room(self) -> str:
        return self._limited_room

    @property
    def other_side_room(self) -> str:
        return self._other_side_room

    @property
    def max_number(self) -> int:
        return self._max_number

    @property
    def mouse_moved(self) -> EventHandler[TransitionEvent]:
        return self._mouse_moved

    # @property
    # def enabled(self) -> bool:
    #     return self._enabled
    #
    # @enabled.setter
    # def enabled(self, value: bool):
    #
    #     self.logger.info(f"enable rule set from '{self._enabled}' to {value}")
    #
    #     self._enabled = value
    #     if value:
    #         self.update_rules()

    @property
    def nb_mice_in_limited(self) -> int:
        return self._nb_mice_in_limited

    @nb_mice_in_limited.setter
    def nb_mice_in_limited(self, value: int):
        self._nb_mice_in_limited = value

        self.update_rules()

    @abstractmethod
    def update_rules(self):
        pass

        #
        # if self.nb_mice_in_limited >= self.max_number:
        #     self.logger.info(f"'{self.limited_room}' if FULL ('{self.nb_mice_in_limited}') and need to be closed")
        #     self.sas_enter.unauthorize_access(exit_room=self.other_side_room)
        # else:
        #     self.sas_enter.authorize_access(from_room=self.other_side_room, to_room=self.limited_room)
        #
        # self.sas_exit.authorize_access(from_room=self.limited_room, to_room=self.other_side_room)

    @property
    def logger(self) -> Logger:
        return self._logger

    @abstractmethod
    def add_authorized_rfid(self, rfid_list: str):
        pass

        # for rfid in rfid_list.split(','):
        #     self.sas_enter.add_authorized_rfid(rfid)
        #     self.sas_exit.add_authorized_rfid(rfid)

    # def _get_both_sides(self, sas: 'SasDoor') -> Tuple[str, str]:
    #     limited_side = sas.get_door_side(self.limited_room)
    #
    #     if limited_side is None:
    #         return None, None
    #
    #     other_side = sas.room_a if limited_side == 'b' else sas.room_b
    #
    #     return self.limited_room, other_side
    #
    # def on_orders_done(self, sender: 'SasDoor', event: 'OrdersDoneEvent'):
    #     self.update_rules()

    # def on_transition_done(self, sender: 'SasDoor', event: 'TransitionEvent'):
    #
    #     # if not self.enabled:
    #     #     return
    #
    #     with self._lock:
    #
    #         self.mouse_moved(event=event)
    #
    #         if event.to_room == self.limited_room:
    #             self.nb_mice_in_limited += 1
    #         else:
    #             self.nb_mice_in_limited -= 1
    #
    #         self.logger.critical(f"NB MICE IN '{self.limited_room}'={self.nb_mice_in_limited}")
    #
    #         self.update_rules()
    #         # always open
    #         # self.sas_exit.authorize_access(from_room=self.limited_room, to_room=self.other_side_room)

    # def check_validity(self):
    #
    #     limited_side, other_side = self._get_both_sides(self.sas_enter)
    #
    #     if limited_side is None:
    #         err_msg = f"Gate enter is not linked to limited room :'{self.limited_room}'"
    #         raise TransitionDoorsException(err_msg)
    #
    #     self._other_side_room = other_side
    #
    #     limited_side, other_side = self._get_both_sides(self.sas_exit)
    #
    #     if limited_side is None:
    #         err_msg = f"Gate exit is not linked to limited room :'{self.limited_room}'"
    #         raise TransitionDoorsException(err_msg)
    #
    #     if other_side != self.other_side_room:
    #         err_msg = f"Sas enter other room('{self.other_side_room}') is not the same than sas exit other room('{other_side}')"
    #         raise TransitionDoorsException(err_msg)

    @abstractmethod
    def start(self):
        pass
        # self.sas_enter.start()
        # self.sas_exit.start()
        # self.check_validity()
        #
        # self.sas_enter.mouse_moved.register(self.on_transition_done)
        # self.sas_exit.mouse_moved.register(self.on_transition_done)
        # self.sas_enter.orders_done.register(self.on_orders_done)
        # self.sas_exit.orders_done.register(self.on_orders_done)
        #
        # self.is_ended.clear()
        # self.started(StartedEvent())

    @abstractmethod
    def stop(self):
        pass

        # self.sas_enter.mouse_moved.unregister(self.on_transition_done)
        # self.sas_exit.mouse_moved.unregister(self.on_transition_done)
        # self.sas_enter.orders_done.unregister(self.on_orders_done)
        # self.sas_exit.orders_done.unregister(self.on_orders_done)
        #
        # self.sas_enter.stop()
        # self.sas_exit.stop()
        #
        # self.is_ended.set()

    # def startExperiment(self):
    #
    #     # if not self._is_initialized:
    #     #     self.start()
    #     #     self._is_initialized = True
    #
    #     self.enabled = True
    #     self.update_rules()
    #
    #     # self.gate1.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )
    #     # self.gate2.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )
    #
    # def pauseExperiment(self):
    #     self.sas_enter.set_inactive()
    #     self.sas_exit.set_inactive()
    #     self.enabled = False


class TransitionDoors(ITransitionDoors):

    def __init__(self, sas_enter: 'SasDoor', sas_exit: 'SasDoor', limited_room: str, other_room: str, max_number: int, device_id: str="None"):
        self._logger = create_logger(self)
        self.sas_enter = sas_enter
        self.sas_exit = sas_exit
        self._limited_room = limited_room
        self._other_side_room: str = other_room
        self._max_number = max_number
        self._device_id = device_id

        self._nb_mice_in_limited = 0

        self.is_ended: Event = Event()
        self._lock: Lock = Lock()

        self._mouse_moved: EventHandler[TransitionEvent] = EventHandler(self)
        self.started: EventHandler[StartedEvent] = EventHandler(self)
        self._enabled = False
        self._is_initialized = False

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def limited_room(self) -> str:
        return self._limited_room

    @property
    def other_side_room(self) -> str:
        return self._other_side_room

    @property
    def max_number(self) -> int:
        return self._max_number

    @property
    def mouse_moved(self) -> EventHandler[TransitionEvent]:
        return self._mouse_moved

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):

        self.logger.info(f"enable rule set from '{self._enabled}' to {value}")

        self._enabled = value
        if value:
            self.update_rules()


    @property
    def nb_mice_in_limited(self) -> int:
        return self._nb_mice_in_limited

    @nb_mice_in_limited.setter
    def nb_mice_in_limited(self, value: int):
        self._nb_mice_in_limited = value

        self.update_rules()

    def update_rules(self):

        if self.nb_mice_in_limited >= self.max_number:
            self.logger.info(f"'{self.limited_room}' if FULL ('{self.nb_mice_in_limited}') and need to be closed")
            self.sas_enter.unauthorize_access(exit_room=self.other_side_room)
        else:
            self.sas_enter.authorize_access(from_room=self.other_side_room, to_room=self.limited_room)

        self.sas_exit.authorize_access(from_room=self.limited_room, to_room=self.other_side_room)

    @property
    def logger(self) -> Logger:
        return self._logger

    def add_authorized_rfid(self, rfid_list: str):

        for rfid in rfid_list.split(','):
            self.sas_enter.add_authorized_rfid(rfid)
            self.sas_exit.add_authorized_rfid(rfid)

    def _get_both_sides(self, sas: 'SasDoor') -> Tuple[str, str]:
        limited_side = sas.get_door_side(self.limited_room)

        if limited_side is None:
            return None, None

        other_side = sas.room_a if limited_side == 'b' else sas.room_b

        return self.limited_room, other_side

    def on_orders_done(self,  sender: 'SasDoor', event: 'OrdersDoneEvent'):
        self.update_rules()

    def on_transition_done(self, sender: 'SasDoor', event: 'TransitionEvent'):

        if not self.enabled:
            return

        with self._lock:

            self.mouse_moved(event=event)

            if event.to_room == self.limited_room:
                self.nb_mice_in_limited += 1
            else:
                self.nb_mice_in_limited -= 1

            self.logger.critical(f"NB MICE IN '{self.limited_room}'={self.nb_mice_in_limited}")

            self.update_rules()
            # always open
            # self.sas_exit.authorize_access(from_room=self.limited_room, to_room=self.other_side_room)


    def check_validity(self):

        limited_side, other_side = self._get_both_sides(self.sas_enter)

        if limited_side is None:
            err_msg = f"Gate enter is not linked to limited room :'{self.limited_room}'"
            raise TransitionDoorsException(err_msg)

        self._other_side_room = other_side

        limited_side, other_side = self._get_both_sides(self.sas_exit)

        if limited_side is None:
            err_msg = f"Gate exit is not linked to limited room :'{self.limited_room}'"
            raise TransitionDoorsException(err_msg)

        if other_side != self.other_side_room:
            err_msg = f"Sas enter other room('{self.other_side_room}') is not the same than sas exit other room('{other_side}')"
            raise TransitionDoorsException(err_msg)


    def start(self):

        self.sas_enter.start()
        self.sas_exit.start()
        self.check_validity()

        self.sas_enter.mouse_moved.register(self.on_transition_done)
        self.sas_exit.mouse_moved.register(self.on_transition_done)
        self.sas_enter.orders_done.register(self.on_orders_done)
        self.sas_exit.orders_done.register(self.on_orders_done)

        self.is_ended.clear()
        self.started(StartedEvent())

    def stop(self):
        self.sas_enter.mouse_moved.unregister(self.on_transition_done)
        self.sas_exit.mouse_moved.unregister(self.on_transition_done)
        self.sas_enter.orders_done.unregister(self.on_orders_done)
        self.sas_exit.orders_done.unregister(self.on_orders_done)

        self.sas_enter.stop()
        self.sas_exit.stop()

        self.is_ended.set()

    def startExperiment(self):

        # if not self._is_initialized:
        #     self.start()
        #     self._is_initialized = True

        self.enabled = True
        self.update_rules()

        # self.gate1.setOrder( GateOrder.ALLOW_SINGLE_A_TO_B , noOrderAtEnd=True )
        # self.gate2.setOrder( GateOrder.ALLOW_SINGLE_B_TO_A )

    def pauseExperiment(self):
        self.sas_enter.set_inactive()
        self.sas_exit.set_inactive()
        self.enabled = False

class SasDoor:

    def __init__(self, room_a: str, room_b: str, position: str):
        self._logger = create_logger(self)
        # self._mouse_allowed: EventHandler[MouseAllowedEvent] = EventHandler(self)
        self._mouse_moved: EventHandler[TransitionEvent] = EventHandler(self)
        self._orders_done: EventHandler[OrdersDoneEvent] = EventHandler(self)
        self.room_a = room_a
        self.room_b = room_b
        self.position = position

        self.is_ended: Event = Event()

    @property
    def logger(self) -> Logger:
        return self._logger

    # @property
    # def mouse_allowed(self) -> EventHandler[TransitionEvent]:
    #     return self._mouse_allowed

    @property
    def mouse_moved(self) -> EventHandler[TransitionEvent]:
        return self._mouse_moved

    @property
    def orders_done(self) -> EventHandler[OrdersDoneEvent]:
        return self._orders_done

    @abstractmethod
    def add_authorized_rfid(self, rfid: str):
        pass

    @abstractmethod
    def authorize_access(self, from_room: str, to_room: str):
        pass

    @abstractmethod
    def unauthorize_access(self, exit_room: str):
        pass

    @abstractmethod
    def set_inactive(self):
        pass

    def get_door_side(self, room_name: str) -> str:
        if self.room_a == room_name:
            return 'a'
        elif self.room_b == room_name:
            return 'b'
        else:
            return None


    @property
    @abstractmethod
    def weight(self) -> float:
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def start(self):
        pass

class FakeSasDoor(SasDoor):

    def __init__(self, room_a: str, room_b: str, position: str = None, fake_gate: Gate = MagicMock()):
        super().__init__(room_a, room_b, position)

        self.access_authorized: bool = False
        self.from_room: str = None
        self.to_room: str = None
        self.authorized_rfid: List[str] = list()
        self.gate = fake_gate

    def add_authorized_rfid(self, rfid: str):
        self.authorized_rfid.append(rfid)

    def stop(self):
        pass

    def start(self):
        pass

    def authorize_access(self, from_room: str, to_room: str):
        self.access_authorized = True
        self.from_room = from_room
        self.to_room = to_room

    def unauthorize_access(self):
        self.access_authorized = False

    def set_inactive(self):
        pass

    def fake_mouse_move_from_to(self, rfid: str, from_room: str, to_room: str):

        if not rfid in self.authorized_rfid:
            self.logger.critical(
                f"Mouse '{rfid}' is not allowed")
            return

        if not self.access_authorized:
            self.logger.critical(
                f"Mouse '{rfid}' can't move from '{from_room}' to '{to_room}' because the sas is closed")
            return

        if self.from_room == from_room and self.to_room == to_room:
            self.mouse_moved(TransitionEvent(id_device="device", weight=self.weight, rfid=rfid, timestamp=datetime.datetime.now().timestamp(), from_room=from_room, to_room=to_room))

    @property
    def weight(self) -> float:
        return 1.1


class GateWrapper(SasDoor):

    # TODO => gate instead of all these parameters?
    def __init__(self,
                 room_a: str, room_b: str,
                 COM_Servo: str=None, COM_Arduino: str=None, COM_RFID: str=None,
                 name: str="noName gate",
                 weightFactor: float = 1,
                 mouseAverageWeight: int = 25,
                 enableLIDAR: bool = True,
                 lidarPinOrder: List[int] = None,
                 gateMode: GateMode = GateMode.MOUSE,
                 invertScale: bool = False,
                 position: str = None,
                 delta_doors_limits: int = None,
                 torque_limits: int = None
                 ):

        super().__init__(room_a, room_b, position)

        self.COM_Servo = COM_Servo
        self.COM_Arduino = COM_Arduino
        self.COM_RFID = COM_RFID
        self.name = name
        self.weightFactor = weightFactor
        self.mouseAverageWeight = mouseAverageWeight
        self.enableLIDAR = enableLIDAR
        self.lidarPinOrder = lidarPinOrder
        self.gateMode = gateMode
        self.invertScale = invertScale

        self.delta_doors_limits = delta_doors_limits
        self.torque_limits = torque_limits

        self.position = position
        self._gate: Gate = None
        # self.gate.addDeviceListener(self.on_device_event_received)

        # self.current_event: TransitionEvent = None

    def add_authorized_rfid(self, rfid: str):
        if rfid not in self.gate.rfidAllowedList:
            self.logger.critical(f"authorize rfid {rfid} to gate:'{self._gate.name}'")
            self.gate.rfidAllowedList.append(rfid)

    @property
    def gate(self) -> Gate:
        return self._gate

    @property
    def gate_order(self) -> GateOrder:
        return self.gate.getOrder()

    def start(self):
        if self.gate is None:
            try:
                gate = Gate(
                    COM_Servo=self.COM_Servo, COM_RFID=self.COM_RFID, COM_Arduino=self.COM_Arduino,
                    name=self.name, weightFactor=self.weightFactor,
                    mouseAverageWeight=self.mouseAverageWeight, enableLIDAR=self.enableLIDAR,
                    lidarPinOrder=self.lidarPinOrder, gateMode=self.gateMode, invertScale=self.invertScale
                )

                self._gate = gate

                if self.delta_doors_limits:
                    gate.doorA.setLimits(OPENED_DOOR_POSITION_MOUSE, CLOSED_DOOR_POSITION_MOUSE + self.delta_doors_limits)
                    gate.doorB.setLimits(OPENED_DOOR_POSITION_MOUSE, CLOSED_DOOR_POSITION_MOUSE + self.delta_doors_limits)

                if self.torque_limits:
                    gate.setSpeedAndTorqueLimits(self.torque_limits, self.torque_limits)

                self._gate.addDeviceListener(self.on_device_event_received)
            except Exception as exc:
                raise TransitionDoorsException(f"Unable to start gate") from exc


    def stop(self):
        self.gate.stop()
        self.is_ended.set()

    @staticmethod
    def extract_rfid(message: str) -> str:

        reg_exp = r".*(?P<RFID>[0-9]{12})"
        match = re.match(reg_exp, message)

        if match:
            return match['RFID']
        else:
            return None


    def authorize_access(self, from_room: str, to_room: str):

        from_side = self.get_door_side(from_room)
        to_side = self.get_door_side(to_room)

        if not self.gate.getOrder() == GateOrder.NO_ORDER:
            return

        if from_side and to_side:
            if from_side == 'a' and to_side == 'b':
                self.gate.setOrder(order=GateOrder.ALLOW_SINGLE_A_TO_B, noOrderAtEnd=True)
            else:
                self.gate.setOrder(order=GateOrder.ALLOW_SINGLE_B_TO_A, noOrderAtEnd=True)
        else:
            err_msg = f"Sas is not linked to both rooms => From:'{from_room}' To:'{to_room}'"
            raise TransitionDoorsException(err_msg)

    @property
    def weight(self) -> float:
        return self.gate.currentWeight

    def unauthorize_access(self, exit_room: str = None):
        pass

    def set_inactive(self):
        self.gate.setOrder(GateOrder.NO_ORDER)

    def on_device_event_received(self, device_event: fab_event.DeviceEvent):

        # print(f"DEVICE EVENT RECEIVED {device_event.description}")


        message = device_event.description
            
        if "Animal allowed to cross" in message:
            self.logger.critical(f"Message : {message}")
            rfid = self.extract_rfid(message)

            if self.gate.getOrder() is GateOrder.ALLOW_SINGLE_A_TO_B:
                from_room = self.room_a
                to_room = self.room_b
            elif self.gate.getOrder() is GateOrder.ALLOW_SINGLE_B_TO_A:
                from_room = self.room_b
                to_room = self.room_a
            else:
                raise Exception("Order should be ALLOW_SINGLE_A_TO_B or ALLOW_SINGLE_B_TO_A")

            self.logger.critical(f"animal {rfid} is allowed to go from {from_room} to {to_room}")
            current_event = TransitionEvent(id_device=self.name, weight=self.weight, timestamp=datetime.datetime.now().timestamp(), rfid=rfid, from_room=from_room, to_room=to_room)
            self.mouse_moved(current_event)

        # if message != "setOrder" and "None" not in message:

        # only there to update rules (act as a gate state changed like)
        self.orders_done(OrdersDoneEvent())

            # self.mouse_moved(TransitionEvent(rfid=rfid, from_room=from_room, to_room=to_room))