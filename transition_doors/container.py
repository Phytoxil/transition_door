from dependency_injector import containers, providers
from typing import List


from mqtt_device.common.mqtt_client import MQTTClient
from mqtt_device.local.client import LocalClient

from transition_doors.local_transition_doors import LocalTransitionDoorsDevice
from transition_doors.single_mouse_sas import SingleMouseSas
from transition_doors.transition_doors import GateWrapper, TransitionDoors


class DeviceContainer(containers.DeclarativeContainer):
    pass

def as_int_list(str_list: str) -> List[int]:

    if str_list is None:
        return None

    res = [int(elem) for elem in str_list.split(',')]
    return res

def as_int(str_int: str) -> int:

    if str_int:
        return int(str_int)


class SasDoorContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    # TODO : pas forcement besoin de conversion si JSON? A VERIFIER

    sas_door = providers.Singleton(
        GateWrapper,
        COM_Servo=config.com_servo.required(),
        COM_Arduino=config.com_arduino.required(),
        COM_RFID=config.com_rfid.required(),
        name=config.name,
        weightFactor=config.weight_factor.as_float(),
        mouseAverageWeight=config.mouse_average_weight.as_float(),
        enableLIDAR=config.enable_lidar.as_(lambda val: int(val) == 1),
        lidarPinOrder=config.lidar_pin_order.as_(as_int_list),
        # gate=gate,
        room_a=config.room_a,
        room_b=config.room_b,
        position=config.position,
        delta_doors_limits=config.delta_doors_limits.as_(as_int),
        torque_limits=config.torque_limits.as_(as_int)
    )

class LocalSingleDoorContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    gate = providers.Container(
        SasDoorContainer,
        config=config.gate.required()
    )


    # gate_enter = providers.Container(
    #     SasDoorContainer,
    #     config=config.gate_enter.required()
    # )
    #
    # gate_exit = providers.Container(
    #     SasDoorContainer,
    #     config=config.gate_exit.required()
    # )

    mqtt_client = providers.Singleton(
        MQTTClient,
        client_id=config.mqtt.client_id.required(),
        broker_ip=config.mqtt.broker_ip.required()
    )

    local_client = providers.Singleton(
        LocalClient,
        environment_name="souris_city",
        id_env="01",
        client_id=config.mqtt.client_id.required(),
        mqtt_client=mqtt_client
    )

    transition_doors = providers.Singleton(
        SingleMouseSas,
        sas_door=gate.sas_door,
        limited_room=config.general.limited_room.required(),
        other_side_room=config.general.other_side_room.required()
    )

    # transition_doors = providers.Singleton(
    #     TransitionDoors,
    #     sas_enter=gate_enter.sas_door,
    #     sas_exit=gate_exit.sas_door,
    #     limited_room=config.general.limited_room.required(),
    #     other_room=config.general.other_side_room.required(),
    #     max_number=config.general.max_number.required().as_int()
    # )
    #
    # local_device = providers.Singleton(
    #     LocalTransitionDoorsDevice,
    #     transition_doors=transition_doors,
    #     device_id="transition_doors"
    # )

    # local = LocalTransitionDoorsDevice(transition_doors=transition_doors, device_id="transition_doors")

class LocalDeviceContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    gate_enter = providers.Container(
        SasDoorContainer,
        config=config.gate_enter.required()
    )

    gate_exit = providers.Container(
        SasDoorContainer,
        config=config.gate_exit.required()
    )

    mqtt_client = providers.Singleton(
        MQTTClient,
        client_id=config.mqtt.client_id.required(),
        broker_ip=config.mqtt.broker_ip.required()
    )

    local_client = providers.Singleton(
        LocalClient,
        environment_name="souris_city",
        id_env="01",
        client_id=config.mqtt.client_id.required(),
        mqtt_client=mqtt_client
    )

    transition_doors = providers.Singleton(
        TransitionDoors,
        sas_enter=gate_enter.sas_door,
        sas_exit=gate_exit.sas_door,
        limited_room=config.general.limited_room.required(),
        other_room=config.general.other_side_room.required(),
        max_number=config.general.max_number.required().as_int()
    )

    local_device = providers.Singleton(
        LocalTransitionDoorsDevice,
        transition_doors=transition_doors,
        device_id="transition_doors"
    )

    # local = LocalTransitionDoorsDevice(transition_doors=transition_doors, device_id="transition_doors")
