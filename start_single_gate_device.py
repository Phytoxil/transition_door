import logging
import sys
import traceback
from pathlib import Path

from PyQt5 import QtWidgets, QtCore

current_dir = Path(__file__).parent
# path_to_add = ['lmt-blocks', 'mqtt_device']
path_to_add = ['lmt-blocks']

for path_str in path_to_add:
    path = current_dir / path_str
    print(f"module path added : '{path}'")
    sys.path.append(str(path))

from transition_doors.single_mouse_sas import SingleMouseSas
from transition_doors.container import LocalSingleDoorContainer

from transition_doors.presentation.LMTVisualExperimentSingle import WWVisualExperiment
from mqtt_device.local.client import LocalClient
from transition_doors.local_transition_doors import LocalTransitionDoorsDevice
from dependency_injector.wiring import Provide




def init(ini_file: Path, *args):

    container = LocalSingleDoorContainer()
    container.config.from_ini(ini_file)

    container.wire(modules=[__name__])

    main(*args)

def excepthook(type_, value, traceback_):
    traceback.print_exception(type_, value, traceback_)
    QtCore.qFatal('')

def main(
        local_client: LocalClient = Provide[LocalSingleDoorContainer.local_client], transition_doors: SingleMouseSas = Provide[LocalSingleDoorContainer.transition_doors]
):

    local_client.connect()

    transition_doors.start()

    local = LocalTransitionDoorsDevice(transition_doors=transition_doors, device_id="transition_door_t")
    local_client.add_local_device(local)

    app = QtWidgets.QApplication([])

    sys.excepthook = excepthook

    logging.info('Application started')

    def exitHandler():
        visualExperiment.stop()

    app.aboutToQuit.connect(exitHandler)

    visualExperiment = WWVisualExperiment(transition_doors=transition_doors)
    visualExperiment.start()
    visualExperiment.show()


    sys.exit(app.exec_())


if __name__ == "__main__":

    init(*sys.argv[1:])