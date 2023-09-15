import datetime
import json
from json import JSONEncoder

from mqtt_device.event_handler import EventArgs


class DateTimeEncoder(json.JSONEncoder):

    def default(self, z):
        if isinstance(z, datetime.datetime):
            return z.timestamp()
        else:
            return super().default(z)

class StartedEvent(EventArgs):
    pass


class OrdersDoneEvent(EventArgs):
    pass


class BaseEvent(EventArgs):

    EVENT_TYPE: str = None

    def __init__(self, id_device: str, timestamp: float, rfid: str = None):
        self.id_device = id_device
        self.date = datetime.datetime.fromtimestamp(timestamp)
        self.rfid: str = rfid

    # @property
    # def date(self) -> datetime.date:
    #     return

    @property
    def event_type(self) -> str:
        if self.EVENT_TYPE:
            return self.EVENT_TYPE
        else:
            raise Exception(f"EVENT_TYPE for class '{type(self)}' needed")

class TransitionEvent(BaseEvent):

    EVENT_TYPE = "transition"

    def __init__(self, id_device: str, timestamp: float, rfid: str, from_room: str, to_room: str, weight: float = 0):
        super().__init__(id_device, timestamp)

        self.rfid = rfid
        self.from_room = from_room
        self.to_room = to_room
        self.weight = weight

    def __eq__(self, other: 'TransitionEvent'):
        if type(other) != type(self):
            return False

        return self.id_device == other.id_device and self.rfid == other.rfid\
               and self.from_room == other.from_room and self.to_room == other.to_room and self.date == other.date and self.weight != other.weight