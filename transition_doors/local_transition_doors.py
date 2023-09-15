import json

# from event_listener.listener import EventHandler
# from mqtt_device.local.device.device import LocalDevice, DeviceProperty, StaticProperty
# from remote_application.remote_transition_doors import ITransitionDoors
# from events import TransitionEvent, DateTimeEncoder
from mqtt_device.event_handler import EventHandler
from mqtt_device.local.device.device import LocalDevice, DeviceProperty, StaticProperty

from transition_doors.events import TransitionEvent, DateTimeEncoder
from transition_doors.remote_transition_doors import ITransitionDoors


class LocalTransitionDoorsDevice(LocalDevice, ITransitionDoors):

    DEVICE_TYPE = "transition_doors"

    def __init__(self, transition_doors: ITransitionDoors, device_id: str, location: str = None):
        self._transition_doors = transition_doors

        self._transition_doors.mouse_moved.register(self.on_mouse_moved)

        super().__init__(device_id=device_id, location=location)

    def declare_properties(self):
        prop = DeviceProperty(property_name="allowed_rfid", datatype="str", settable=True, retention=True)
        self.add_property(prop)

        prop.value_changed += self.on_allowed_rfid_changed

        prop = DeviceProperty(property_name="transition", datatype="str", settable=False)
        self.add_property(prop)

        prop = StaticProperty(property_name="max_number", datatype="integer", static_value=self._transition_doors.max_number)
        self.add_property(prop)

        prop = StaticProperty(property_name="limited_room", datatype="str", static_value=self._transition_doors.limited_room)
        self.add_property(prop)

        prop = StaticProperty(property_name="other_side_room", datatype="str", static_value=self._transition_doors.other_side_room)
        self.add_property(prop)

    @property
    def mouse_moved(self) -> EventHandler[TransitionEvent]:
        return self._transition_doors.mouse_moved

    @property
    def limited_room(self) -> str:
        return self._transition_doors.limited_room

    @property
    def other_side_room(self) -> str:
        return self._transition_doors.other_side_room

    @property
    def max_number(self) -> int:
        return self._transition_doors.max_number

    def add_authorized_rfid(self, rfid_list: str):
        self._transition_doors.add_authorized_rfid(rfid_list)

    def start(self):
        self._transition_doors.start()

    def stop(self):
        self._transition_doors.stop()

    def on_allowed_rfid_changed(self, sender: DeviceProperty, old: str, new: str):
        self._transition_doors.add_authorized_rfid(rfid_list=new)

    def on_mouse_moved(self, sender: ITransitionDoors, event: TransitionEvent):
        prop = self.transition
        prop.set_str_value(json.dumps(event.__dict__, cls=DateTimeEncoder))

    @property
    def transition(self) -> DeviceProperty:
        prop = self.get_property("transition")
        return prop


