from certificates.certificates_loaders import get_ssl_parameters
from components.components import Component
from machine import Pin, PWM, I2C
import utime
import json
from lcd.lcd_api import LcdApi
from lcd.pico_i2c_lcd import I2cLcd
from lib.umqtt.simple import MQTTClient
from components.sensors import IRDistance


# Abstract class
class Actuator(Component):
    def __init__(self, subscriber_location: str, subscriber_id: str, subscription_topic: str,
                 mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is Actuator:
            raise Exception('Error init: <Actuator is abstract class>')

        self.subscription_topic = subscription_topic
        self._id = subscriber_id
        super().__init__(subscriber_location, subscriber_id, mqtt_client, mqtt_server)

    def connect_to_mqtt(self) -> None:
        try:
            self._mqtt_client.set_callback(self._react_to_message)
            self._mqtt_client.connect()
            self.set_subscription()
            self.is_connected_to_mqtt = True
            print(f'Actuator "{self._id}" mqtt connection: {self._mqtt_server}\n')
        except Exception:
            print(f'Actuator "{self._id}" mqtt connection: FAILED\n')
            self.is_connected_to_mqtt = False

    def _react_to_message(self, topic: str, message: str) -> None:
        raise NotImplementedError("All subclasses of Actuator must have implemented function for message reaction!")

    def set_subscription(self) -> None:
        raise NotImplementedError(
            "All subclasses of Actuator must have implemented function for message subscription!")

    def check_message(self) -> None:
        if self.is_connected_to_mqtt:
            try:
                self._mqtt_client.check_msg()
            except Exception:
                print(f'Actuator "{self._id}" mqtt connection: FAILED\n')
                self.is_connected_to_mqtt = False


# enum lib does not exist in micropython
class GateState:
    OPENED = 1
    OPENING = 2
    CLOSED = 3
    CLOSING = 4


# Abstract class
class GeneralGate(Actuator):
    instance_counter = 0

    def __init__(self, gate_location: str, mqtt_client: MQTTClient = None,
                 mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is GeneralGate:
            raise Exception('Error init: <GeneralGate is abstract class>')

        gate_name = "gate_" + str(self.instance_counter)
        self.gate_state = GateState.CLOSED
        super().__init__(gate_location, gate_name, "devices/parkslot1/messages/events/subscribers/gates/" + gate_name, mqtt_client,
                         mqtt_server)
        # "devices/parkslot1/messages/events/subscribers/gates/" + gate_name
        # devices/parkslot1/messages/events/
        GeneralGate.instance_counter += 1

    def _react_to_message(self, topic: str, message: str) -> None:
        if type(message) is bytes:
            message = message.decode("utf-8")

        try:
            message_dict = json.loads(message)
            if message_dict.get("open") == "True" and message_dict.get("close") != "True":
                self._open()
            elif message_dict.get("close") == "True" and message_dict.get("open") != "True":
                self._close()

            print(f"Gate {self._id} reaction status: SUCCESS\n")
        except ValueError:
            print(f"Gate {self._id} reaction status: FAILURE - WRONG JSON FORMAT\n")

    def set_subscription(self) -> None:
        self._mqtt_client.subscribe(self.subscription_topic)

    def _open(self) -> None:
        raise NotImplementedError(
            "All subclasses of GeneralGate must have implemented function for gate opening!")

    def _close(self) -> None:
        raise NotImplementedError(
            "All subclasses of GeneralGate must have implemented function for gate closing!")


"""
    VBUS -> power
    GP16 -> com
"""


class SG90Servo(GeneralGate):
    __closed_position = 1750
    __opened_position = 5000

    def __init__(self, gate_location: str, pin: int, mqtt_client: MQTTClient = None,
                 mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        self.__pwm = PWM(Pin(pin))
        self.__pwm.freq(50)
        super().__init__(gate_location, mqtt_client, mqtt_server)

    def _open(self) -> None:
        if self.gate_state != GateState.CLOSED:
            return

        self.gate_state = GateState.OPENING
        for position in range(self.__closed_position, self.__opened_position, 50):
            self.__pwm.duty_u16(position)
            utime.sleep(0.075)

        self.gate_state = GateState.OPENED

    def _close(self) -> None:
        if self.gate_state != GateState.OPENED:
            return

        self.gate_state = GateState.CLOSING
        for position in range(self.__opened_position, self.__closed_position, -50):
            self.__pwm.duty_u16(position)
            utime.sleep(0.075)

        self.gate_state = GateState.CLOSED


"""
    set json "{"occupied": <bool>}"
"""

"""
    VBUS -> power
    GP0, GP1 -> com
"""


class ParkingSpotsState:
    # maximum number of parking spots
    INITIAL_STATE = 1
    EMPTY = 0


class LCD(Actuator):
    instance_counter = 0
    __I2C_ADDR = 0x27
    __I2C_NUM_ROWS = 4
    __I2C_NUM_COLS = 16
    # max number of parking spots
    __spaces_left = ParkingSpotsState.INITIAL_STATE

    def __init__(self, lcd_location: str, sda_pin: int, scl_pin: int, mqtt_client: MQTTClient = None,
                 mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        lcd_name = "lcd_" + str(self.instance_counter)

        self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
        self.lcd = I2cLcd(self.i2c, self.__I2C_ADDR, self.__I2C_NUM_ROWS, self.__I2C_NUM_COLS)
        super().__init__(lcd_location, lcd_name, "devices/parkslot1/messages/events/subscribers/displays/" + lcd_name
                         , mqtt_client=mqtt_client, mqtt_server=mqtt_server)
        # super().__init__(lcd_location, lcd_name, "displays/" + lcd_name, mqtt_client, mqtt_server)
        LCD.instance_counter += 1
        self.__initialize_display_text()

    def _react_to_message(self, topic: str, message: str) -> None:
        print("LCD reacting to msg")
        if type(message) is bytes:
            message = message.decode("utf-8")

        try:
            message_dict = json.loads(message)
            if message_dict.get("occupied") == "True":
                self.__spaces_left -= 1
        except ValueError:
            print("json sent in wrong format")
        self.lcd.move_to(13, 0)
        self.lcd.putstr(str(self.__spaces_left))

    def set_subscription(self) -> None:
        self._mqtt_client.subscribe(self.subscription_topic)

    def __initialize_display_text(self):
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Spaces left:")
        self.lcd.move_to(13, 0)
        self.lcd.putstr(str(self.__spaces_left))
        self.lcd.move_to(7, 1)
        self.lcd.putstr("->")

    # call this function in the main loop before reading from distance sensors
    def reset_spaces_left(self):
        self.__spaces_left = ParkingSpotsState.INITIAL_STATE
        
    def get_topic(self) -> str:
        return "devices/parkslot1/messages/events/subscribers/displays/" + "lcd_" + str(self.instance_counter)
        # return "displays/" + "lcd_" + str(self.instance_counter)


"""
    set json "{"occupied": <bool>}"
"""

"""
    GP16 -> com_red
    GP11 -> com_green
"""

class LED(Actuator):
    instance_counter = 0

    def __init__(self, led_location: str, led_green_pin: int, led_red_pin: int, mqtt_client: MQTTClient = None,
                 mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        led_name = "led_" + str(self.instance_counter)

        super().__init__(led_location, led_name,"devices/parkslot1/messages/events/subscribers/leds/" + led_name
                         , mqtt_client=mqtt_client, mqtt_server=mqtt_server)
        # super().__init__(led_location, led_name, "leds/" + led_name, mqtt_client, mqtt_server)
        self.led_green = Pin(led_green_pin, Pin.OUT)
        self.led_red = Pin(led_red_pin, Pin.OUT)

    def _react_to_message(self, topic: str, message: str) -> None:
        print("leds reacting to msg")
        if type(message) is bytes:
            message = message.decode("utf-8")

        try:
            message_dict = json.loads(message)
            if message_dict.get("occupied") == "True":
                self.led_green.value(0)
                self.led_red.value(1)
            elif message_dict.get("occupied") == "False":
                self.led_green.value(1)
                self.led_red.value(0)
        except ValueError:
            print("json sent in wrong format")

    def set_subscription(self) -> None:
        self._mqtt_client.subscribe(self.subscription_topic)

    def get_topic(self) -> str:
        return "devices/parkslot1/messages/events/subscribers/leds/" + "led_" + str(self.instance_counter)
        # return "leds/" + "led_" + str(self.instance_counter)
