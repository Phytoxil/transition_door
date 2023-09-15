import datetime
import json
from abc import abstractmethod
from typing import Any, List

# from event_listener.listener import EventHandler
# from mqtt_device.local.device.device import DeviceProperty
# from mqtt_device.remote.device.device import RemoteDevice
# from events import TransitionEvent


# TODO : first step to create a cleaner way to use remote objects
from mqtt_device.event_handler import EventHandler
from mqtt_device.local.device.device import DeviceProperty
from mqtt_device.remote.device.device import RemoteDevice

from transition_doors.events import TransitionEvent


class ITransitionDoors:

    @property
    @abstractmethod
    def mouse_moved(self) -> EventHandler[TransitionEvent]:
        pass

    @property
    @abstractmethod
    def limited_room(self) -> str:
        pass

    @property
    @abstractmethod
    def other_side_room(self) -> str:
        pass

    @property
    @abstractmethod
    def max_number(self) -> int:
        pass

    @abstractmethod
    def add_authorized_rfid(self, rfid_list: str):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def update_rules(self):
        pass

class RemoteTransitionDoors(RemoteDevice, ITransitionDoors):

    DEVICE_TYPE = "transition_doors"

    def __init__(self, device_id: str, device_type: str = None):
        super().__init__(device_id, device_type)

        self._mouse_moved: EventHandler[TransitionEvent] = EventHandler(self)

        self._max_number: int = None
        self._limited_room: str = None
        self._other_side_room: str = None
        # self.allowed_rfid: List[str] = list()

    @property
    def max_number(self) -> int:
        return self._max_number

    @property
    def mouse_moved(self) -> EventHandler[TransitionEvent]:
        return self._mouse_moved

    @property
    def limited_room(self) -> str:
        return self._limited_room
    
    @limited_room.setter
    def limited_room(self, value: str):
        self._limited_room = value

    @property
    def other_side_room(self) -> str:
        return self._other_side_room

    @other_side_room.setter
    def other_side_room(self, value: str):
        self._other_side_room = value

    def on_property_added(self, sender: RemoteDevice, prop: DeviceProperty):

        # print(f"PROP = {prop.property_name}")
        if prop.property_name == "transition":
            prop.value_changed += self.on_transition
        elif prop.property_name == "limited_room":
           self.limited_room = prop.value  # static prop
        elif prop.property_name == "other_side_room":
            self.other_side_room = prop.value  # static prop
        elif prop.property_name == "max_number":
            self._max_number = prop.value  # static prop

    def on_transition(self, sender: DeviceProperty, old: str, new: str):
        res = json.loads(new)

        # TODO : weight should be always avalaible in the future, remove condition
        if "weight" in res:
            weight = res["weight"]
        else:
            weight = 0

        event = TransitionEvent(id_device=res["id_device"], weight=weight, timestamp=res["date"], rfid=res["rfid"], from_room=res["from_room"], to_room=res["to_room"])
        self.mouse_moved(event)

    def add_authorized_rfid(self, rfid_list: str):
        self.logger.info(f"Add rfid list {rfid_list}")
        prop = self.get_property("allowed_rfid", timeout=3)
        prop.value = rfid_list

