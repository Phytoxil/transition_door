from abc import abstractmethod


from transition_doors.presentation.gate_view_UI import Ui_gate_view_control
from PyQt5 import QtWidgets as QtWidgets

from transition_doors import GateWrapper


class GateViewWidget:

    def __init__(self, sas_door: GateWrapper):
        self._view = GateViewImpl()
        # model = LogTableModel()
        self._presenter = GatePresenter(sas_door=sas_door, view=self._view)

    @property
    def presenter(self):
        return self._presenter

    @property
    def widget(self) -> QtWidgets.QWidget:
        return self._view

class GatePresenter:

    def __init__(self, sas_door: GateWrapper, view: 'GateView'):
        self.view = view
        self.view.set_presenter(self)

        self.sas_door = sas_door
        self.display_sas_door()

    def display_sas_door(self):

        self.view.set_room_a(self.sas_door.room_a)
        self.view.set_room_b(self.sas_door.room_b)

        if isinstance(self.sas_door, GateWrapper):
            gate = self.sas_door
            self.view.set_com_ports(gate.COM_Servo, gate.COM_Arduino, gate.COM_RFID)
            self.view.set_weight_factor(gate.weightFactor)
            self.view.set_average_weight(gate.mouseAverageWeight)
            self.view.set_door_name(gate.name)


    # @property
    # def widget(self) -> :
    #     return self.view



class GateView:

    @abstractmethod
    def set_presenter(self, presenter: GatePresenter):
        pass

    @abstractmethod
    def set_room_a(self, name:str):
        pass

    @abstractmethod
    def set_room_b(self, name: str):
        pass

    @abstractmethod
    def set_com_ports(self, com_servo: str, com_arduino: str, com_rfid: str):
        pass

    @abstractmethod
    def set_weight_factor(self, value: float):
        pass

    @abstractmethod
    def set_average_weight(self, value: float):
        pass

    @abstractmethod
    def set_door_name(self, name: str):
        pass




class GateViewImpl(QtWidgets.QWidget, Ui_gate_view_control, GateView):

    def __init__(self):
        super(GateViewImpl, self).__init__()
        self.setupUi(self)
        self._presenter: GatePresenter = None

    def set_presenter(self, presenter: GatePresenter):
        self._presenter = presenter

    def set_room_a(self, name: str):
        self.led_room_a.setText(name)

    def set_room_b(self, name: str):
        self.led_room_b.setText(name)

    def set_com_ports(self, com_servo: str, com_arduino: str, com_rfid: str):
        self.led_com_servo.setText(com_servo)
        self.led_com_arduino.setText(com_arduino)
        self.led_com_rfid.setText(com_rfid)

    def set_weight_factor(self, value: float):
        self.led_weight_factor.setText(f"{value:.2f}")

    def set_average_weight(self, value: float):
        self.led_mouse_average.setText(f"{value:.2f}")

    def set_door_name(self, name: str):
        self.group_gate.setTitle(name)

