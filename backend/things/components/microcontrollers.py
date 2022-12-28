import time
from machine import Pin
import network
from components.sensors import Sensor
from components.components import Component
from components.actuators import Actuator
import sys

# TODO: MAYBE NOT CONNECT TO MQTT HERE AS WELL
# TODO: CHANGE UTIME TO TIME
"""
    Maybe add closeAllGates to Microcontroller class
"""


# enum lib does not exist in micropython
class ComponentResponseType:
    REGULAR = 1
    INTERRUPT = 2


# Abstract class
class Microcontroller:
    def __init__(self):
        if type(self) is Microcontroller:
            raise Exception('Error init: <Microcontroller is abstract class>')

    def start_controller(self) -> None:
        raise NotImplementedError(
            "All subclasses of Microcontroller must have implemented function for startup!")

    def add_component(self, component: Component, pins, component_type: ComponentResponseType) -> None:
        raise NotImplementedError(
            "All subclasses of Microcontroller must have implemented function for component addition!")

    def remove_component(self, component: Component) -> None:
        raise NotImplementedError(
            "All subclasses of Microcontroller must have implemented function for component removal!")

    def component_handler(self, component_type: ComponentResponseType) -> None:
        raise NotImplementedError(
            "All subclasses of Microcontroller must have implemented function for component handling!")


class RPiPico(Microcontroller):
    pin_count = 40
    instance_counter = 0

    def __init__(self, pico_id: str = None):
        super().__init__()
        self.__start_sequence()
        if pico_id is not None:
            self.id = pico_id
        else:
            self.id = "RPiPico#" + str(self.instance_counter)
            RPiPico.instance_counter += 1

        self.__wlan = None
        self._regular_components = {}
        self._interrupt_components = {}

    def start_controller(self) -> None:
        print(f"\nMicrocontroller \"{self.id}\" -> starting\n")
        self.__start_sequence()
        self.connect_to_internet()
        print(f"\nMicrocontroller \"{self.id}\" -> started successfully\n\n")

    @staticmethod
    def __start_sequence() -> None:
        led = Pin("LED", Pin.OUT)
        led.on()
        time.sleep(1)
        led.off()

    def add_component(self, component: Component, pins, component_type: ComponentResponseType) -> None:
        try:
            if isinstance(pins, int):
                if not 0 <= pins <= self.pin_count:
                    raise IndexError
            else:
                # itterating when one component needs more pins
                for pin in pins:
                    if not 0 <= pin <= self.pin_count:
                        raise IndexError
            if component_type == ComponentResponseType.REGULAR not in self._regular_components:
                self._regular_components[component] = pins
            elif component_type == ComponentResponseType.INTERRUPT not in self._interrupt_components:
                self._interrupt_components[component] = pins
            else:
                print("Component ", end="")
                component.print_id()
                print(" is already connected")
        except IndexError:
            print(f"Pin {pins} does not exist on RPiPico!")

    def remove_component(self, component: Component) -> None:
        if component not in self._regular_components and component not in self._interrupt_components:
            print("Component ", end="")
            component.print_id()
            print(" is already not connected")
            return

        self._regular_components.pop(component, None)
        self._interrupt_components.pop(component, None)

    def connect_to_internet(self) -> None:
        try:
            self.__wlan = network.WLAN(network.STA_IF)
            self.__wlan.active(True)
            self.__wlan.connect("<SSID>", "<PASSWORD>")
            print(f'Internet connection: {self.__wlan.isconnected()}')

            if not self.__wlan.isconnected():
                print('   ---reconnecting\n')
                time.sleep(5)
                self.connect_to_internet()
        except (MemoryError, RuntimeError, OSError):
            print('Internet connection: FATAL ERROR\n')
            print('Microcontroller shutdown...')
            sys.exit()

    @staticmethod
    def __device_handler(device: Actuator) -> None:
        if device.is_connected_to_mqtt:
            device.check_message()

    @staticmethod
    def __sensor_handler(sensor: Sensor) -> None:
        if sensor.is_connected_to_mqtt:
            sensor.measure()
            sensor.publish_measurement()

    def component_handler(self, component_type: ComponentResponseType) -> None:
        component_dict = {}
        if component_type == ComponentResponseType.REGULAR:
            component_dict = self._regular_components
        elif component_type == ComponentResponseType.INTERRUPT:
            component_dict = self._interrupt_components

        for component in component_dict:
            if isinstance(component, Actuator):
                self.__device_handler(component)

            elif isinstance(component, Sensor):
                self.__sensor_handler(component)

    def __components_health_check(self, component_type: ComponentResponseType) -> None:
        component_dict = {}
        if component_type == ComponentResponseType.REGULAR:
            component_dict = self._regular_components
        elif component_type == ComponentResponseType.INTERRUPT:
            component_dict = self._interrupt_components

        for component in component_dict:
            print("Component ", end="")
            component.print_id()
            healthy, health_report = component.health_check()
            print(
                f" health status: \"{'HEALTHY' if healthy else 'UNHEALTHY'}\"\n    full report: \"{health_report}\"\n")

            if not component.is_connected_to_mqtt:
                component.connect_to_mqtt()

    def disconnect_all(self, component_type: ComponentResponseType):
        component_dict = {}
        if component_type == ComponentResponseType.REGULAR:
            component_dict = self._regular_components
        elif component_type == ComponentResponseType.INTERRUPT:
            component_dict = self._interrupt_components

        for component in component_dict:
            component.disconnect()

    def connect_all(self, component_type: ComponentResponseType):
        component_dict = {}
        if component_type == ComponentResponseType.REGULAR:
            component_dict = self._regular_components
        elif component_type == ComponentResponseType.INTERRUPT:
            component_dict = self._interrupt_components

        for component in component_dict:
            component.connect_to_mqtt()

    def handle_health_check(self, component_type: ComponentResponseType) -> None:
        if not self.__wlan.isconnected():
            self.connect_to_internet()

        self.__components_health_check(component_type)
