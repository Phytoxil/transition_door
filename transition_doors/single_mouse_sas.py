from threading import Event

# from common import create_logger
# from event_listener.listener import EventHandler
# from events import TransitionEvent, OrdersDoneEvent
# from remote_application.remote_transition_doors import ITransitionDoors
# from transition_doors import SasDoor, TransitionDoorsException
from mqtt_device.common.common_log import create_logger
from mqtt_device.event_handler import EventHandler

from transition_doors.events import TransitionEvent
from transition_doors.remote_transition_doors import ITransitionDoors
from transition_doors.transition_doors import SasDoor


class SingleMouseSas(ITransitionDoors):

    def __init__(self, sas_door: SasDoor, limited_room: str, other_side_room: str):
        self.logger = create_logger(self)

        self._mouse_moved: EventHandler[TransitionEvent] = EventHandler(self)
        self.sas_door = sas_door
        self._limited_room = limited_room
        self._other_side_room = other_side_room
        self._enabled = False
        self._nb_mice_in_limited = 0
        self.is_ended: Event = Event()

    def on_transition_done(self, sender: 'SasDoor', event: 'TransitionEvent'):

        if not self.enabled:
            return

        # with self._lock:

        self.mouse_moved(event=event)

        if event.to_room == self.limited_room:
            self.nb_mice_in_limited += 1
        else:
            self.nb_mice_in_limited -= 1

        self.logger.critical(f"NB MICE IN '{self.limited_room}'={self.nb_mice_in_limited}")

        self.update_rules()

    @property
    def mouse_moved(self) -> EventHandler[TransitionEvent]:
        return self._mouse_moved


    @property
    def limited_room(self) -> str:
        return self._limited_room

    @property
    def other_side_room(self) -> str:
        return self._other_side_room

    @property
    def max_number(self) -> int:
        return 1

    def add_authorized_rfid(self, rfid_list: str):
        self.sas_door.add_authorized_rfid(rfid=rfid_list)

    def on_orders_done(self,  sender: 'SasDoor', event: 'OrdersDoneEvent'):
        self.update_rules()


    def start(self):
        self.sas_door.start()
        self.sas_door.mouse_moved.register(self.on_transition_done)
        self.sas_door.orders_done.register(self.on_orders_done)
        self.is_ended.clear()

    def stop(self):
        self.sas_door.stop()
        self.sas_door.mouse_moved.unregister(self.on_transition_done)
        self.sas_door.orders_done.unregister(self.on_orders_done)
        self.is_ended.set()

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

            self.sas_door.authorize_access(from_room=self.limited_room, to_room=self.other_side_room)
        else:
            self.sas_door.authorize_access(from_room=self.other_side_room, to_room=self.limited_room)

    def startExperiment(self):
        self.enabled = True
        self.update_rules()

    def pauseExperiment(self):
        self.sas_door.set_inactive()
        self.enabled = False
