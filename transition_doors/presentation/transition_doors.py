from abc import abstractmethod

import PyQt5.QtWidgets as QtWidgets

from transition_doors.presentation.gate_view import GateViewWidget
from transition_doors.presentation.transition_doors_view_UI import Ui_transition_doors
from transition_doors import TransitionDoors, SasDoor, TransitionDoorsException
from events import TransitionEvent


def display_error_message(error_msg: str):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    # msg.setText("Error")
    msg.setInformativeText(error_msg)
    msg.setWindowTitle("Error")
    msg.exec_()



class TransitionDoorsPresenter:

    def __init__(self, transition_doors: TransitionDoors, view: 'TransitionDoorsView'):
        self.transition_doors = transition_doors
        self.view = view
        self.view.set_presenter(self)

        # TODO : to place in app model but yet in the presenter


        self.init()
        # self.view.add_door(self.transition_doors.sas_enter)
        # self.view.add_door(self.transition_doors.sas_exit)

    def init(self):
        self.transition_doors.mouse_moved.register(self.on_mouse_moved)
        self.view.add_door(self.transition_doors.sas_enter)
        self.view.add_door(self.transition_doors.sas_exit)
        self.view.enable_start(True)
        self.view.enable_stop(False)

        self.view.set_nb_mice(0)

    def on_mouse_moved(self, sender: TransitionDoors, event: TransitionEvent):
        self.view.set_nb_mice(sender.nb_mice_in_limited)

    def start_transition_doors(self):
        try:
            self.transition_doors.start()
            self.view.enable_start(False)
            self.view.enable_stop(True)
        except TransitionDoorsException as exc:

            err_msg = f"{exc}.\nCause : {exc.__cause__}"
            display_error_message(err_msg)

    def stop_transition_doors(self):

        self.transition_doors.stop()
        self.view.enable_start(True)
        self.view.enable_stop(False)


class TransitionDoorsView:

    @abstractmethod
    def set_presenter(self, presenter: TransitionDoorsPresenter):
        pass

    @abstractmethod
    def add_door(self, sas_door: SasDoor):
        pass

    @abstractmethod
    def set_transition_info(self, transition_doors: TransitionDoors):
        pass

    @abstractmethod
    def set_nb_mice(self, nb_mice: int):
        pass

    @abstractmethod
    def enable_start(self, enable: bool = True):
        pass

    @abstractmethod
    def enable_stop(self, enable: bool = True):
        pass


class TransitionDoorsViewImpl(QtWidgets.QWidget, Ui_transition_doors, TransitionDoorsView):

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self._presenter: TransitionDoorsPresenter = None

        self.init_UI()

    def init_UI(self):
        self.btn_start.clicked.connect(self._on_btn_start_clicked)
        self.btn_stop.clicked.connect(self._on_btn_stop_clicked)

    def _on_btn_start_clicked(self):
        self._presenter.start_transition_doors()

    def _on_btn_stop_clicked(self):
        self._presenter.stop_transition_doors()

    def set_presenter(self, presenter: TransitionDoorsPresenter):
        self._presenter = presenter

    def add_door(self, sas_door: SasDoor):
        self.layout_doors.addWidget(GateViewWidget(sas_door=sas_door).widget)

    def set_transition_info(self, transition_doors: TransitionDoors):
        msg = f"Transition between '{transition_doors.sas_enter.room_a}' and '{transition_doors.sas_enter.room_b}'"
        self.lbl_transition.setText(msg)

        msg = f"Restricted room : '{transition_doors.limited_room}' with max mice set to {transition_doors.nb_mice_in_limited}"
        self.lbl_restricted.setText(msg)

    def set_nb_mice(self, nb_mice: int):
        msg = f"Nb mice in limited room : {nb_mice}"
        self.lbl_nb_mice.setText(msg)

    def enable_start(self, enable: bool = True):
        self.btn_start.setEnabled(enable)

    def enable_stop(self, enable: bool = True):
        self.btn_stop.setEnabled(enable)






