import json
import utime
from machine import Pin
import network
from lib.umqtt.robust2 import MQTTClient
from components.sensors import Sensor
from components.components import Component
from components.devices import Device, Gate
# can use umqtt.simple as well
import sys

# TODO: MAYBE NOT CONNECT TO MQTT HERE AS WELL

"""
    Maybe add closeAllGates to Microcontroller class
"""


# Abstract class
class Microcontroller:
    def __init__(self):
        if type(self) is Microcontroller:
            raise Exception('Error init: <Microcontroller is abstract class>')

    def start_controller(self) -> None:
        raise NotImplementedError(
            "All subclasses of Microcontroller must have implemented function for startup!")

    def add_component(self, component: Component, pin: int) -> None:
        raise NotImplementedError(
            "All subclasses of Microcontroller must have implemented function for component addition!")

    def remove_component(self, pin: int) -> None:
        raise NotImplementedError(
            "All subclasses of Microcontroller must have implemented function for component removal!")

    def component_handler(self) -> None:
        raise NotImplementedError(
            "All subclasses of Microcontroller must have implemented function for component handling!")


class RPiPico(Microcontroller):
    pin_count = 40
    instance_counter = 0
    _components = (pin_count + 1) * [None]  # PIN MAX is reserved for internal thermometer

    def __init__(self, pico_id: str = None, mqtt_server: str = "broker.hivemq.com"):
        super().__init__()
        self.__start_sequence()
        if pico_id is not None:
            self.id = pico_id
        else:
            self.id = "RPiPico#" + str(self.instance_counter)
            RPiPico.instance_counter += 1

        self.__mqtt_server = mqtt_server
        self.__wlan = None
        self.__mqtt_client = MQTTClient(self.id, self.__mqtt_server, keepalive=3600)

    def start_controller(self) -> None:
        print(f"\nMicrocontroller \"{self.id}\" -> starting\n")
        self.__start_sequence()
        self.connect_to_internet()
        self.connect_to_mqtt()
        print(f"\nMicrocontroller \"{self.id}\" -> started successfully\n\n")

    @staticmethod
    def __start_sequence() -> None:
        led = Pin("LED", Pin.OUT)
        led.on()
        utime.sleep(1)
        led.off()

    def add_component(self, component: Component, pin: int) -> None:
        try:
            if self._components[pin] is None:
                self._components[pin] = component
            else:
                print(f"Pin {pin} is already occupied.")
        except IndexError:
            print(f"Pin {pin} does not exist on RPiPico!")

    def remove_component(self, pin: int) -> None:
        try:
            if self._components[pin] is not None:
                self._components[pin] = None
            else:
                print(f"Pin {pin} is already available.")
        except IndexError:
            print(f"Pin {pin} does not exist on RPiPico!")

    def connect_to_internet(self) -> None:
        try:
            self.__wlan = network.WLAN(network.STA_IF)
            self.__wlan.active(True)
            self.__wlan.connect("<SSID>", "<PASSWORD>")
            print(f'Internet connection: {self.__wlan.isconnected()}')

            if not self.__wlan.isconnected():
                print('   ---reconnecting\n')
                utime.sleep(5)
                self.connect_to_internet()
        except (MemoryError, RuntimeError, OSError):
            print('Internet connection: FAILED\n')
            print('Exiting process...')
            sys.exit()

    def connect_to_mqtt(self) -> None:
        self.__mqtt_client.connect()
        print(f'Mqtt connection: {self.__mqtt_server}')

    @staticmethod
    def __device_handler(device: Device) -> None:
        if device.is_connected_to_mqtt:
            device.check_message()

    @staticmethod
    def __sensor_handler(sensor: Sensor) -> None:
        if sensor.is_connected_to_mqtt:
            sensor.measure()
            sensor.publish_measurement()

    def component_handler(self) -> None:
        for component in self._components:
            if isinstance(component, Device):
                self.__device_handler(component)

            elif isinstance(component, Sensor):
                self.__sensor_handler(component)

    def close_all_gates(self) -> None:
        for component in self._components:
            if isinstance(component, Gate):
                self.__mqtt_client.publish(component.topic, json.dumps({"close": "True"}))
