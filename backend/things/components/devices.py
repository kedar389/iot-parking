from components.components import Component
from machine import Pin, PWM
import utime
import json


# Abstract class
class Device(Component):
    def __init__(self, device_location: str, device_id: str):
        if type(self) is Device:
            raise Exception('Error init: <Device is abstract class>')

        super().__init__(device_location, device_id)

    def connect_to_mqtt(self) -> None:
        try:
            self._mqtt_client.set_callback(self._react_to_message)
            self._mqtt_client.connect()
            self.set_subscription()
            self.is_connected_to_mqtt = True
            print(f'Device "{self._id}" -> mqtt connection: {self._mqtt_server}\n')
        except OSError:
            print(f'Device "{self._id}" -> mqtt connection: FAILED\n')

    def _react_to_message(self, topic: str, message: str) -> None:
        raise NotImplementedError("All subclasses of Device must have implemented function for message reaction!")

    def set_subscription(self) -> None:
        raise NotImplementedError("All subclasses of Device must have implemented function for message subscription!")

    def check_message(self) -> None:
        self._mqtt_client.check_msg()


# enum lib do not exist in micropython
class GateState:
    OPENED = 1
    OPENING = 2
    CLOSED = 3
    CLOSING = 4


"""
    VBUS -> power
    GP1 -> com
"""
class Gate(Device):
    """
        Assumpting using ONLY SG90 Servo.
        For usage of other create separate classes renamed accordingly.
    """
    instance_counter = 0
    __closed_position = 1750
    __opened_position = 5000

    """
        Maybe set only one topic "devices/gates/<gate_name>"
        and set json "{"open": <bool>, "close": <bool>}"
    """

    def __init__(self, gate_location: str, pin: int):
        gate_name = "gate_" + str(self.instance_counter)
        self.topic = "devices/gates/" + gate_name
        self.__pwm = PWM(Pin(pin))
        self.__pwm.freq(50)
        self.gate_state = GateState.CLOSED
        super().__init__(gate_location, gate_name)
        Gate.instance_counter += 1

    def _react_to_message(self, topic: str, message: str) -> None:
        if type(message) is bytes:
            message = message.decode("utf-8")

        try:
            message_dict = json.loads(message)
            if message_dict.get("open") == "True" and message_dict.get("close") != "True":
                self.__open()
            elif message_dict.get("close") == "True" and message_dict.get("open") != "True":
                self.close()
        except ValueError:
            print("json sent in wrong format")

    def set_subscription(self) -> None:
        self._mqtt_client.subscribe(self.topic)

    def __open(self) -> None:
        if self.gate_state != GateState.CLOSED:
            return

        self.gate_state = GateState.OPENING
        for position in range(self.__closed_position, self.__opened_position, 50):
            self.__pwm.duty_u16(position)
            utime.sleep(0.075)

        self.gate_state = GateState.OPENED

    def close(self) -> None:
        if self.gate_state != GateState.OPENED:
            return

        self.gate_state = GateState.CLOSING
        for position in range(self.__opened_position, self.__closed_position, -50):
            self.__pwm.duty_u16(position)
            utime.sleep(0.075)

        self.gate_state = GateState.CLOSED
