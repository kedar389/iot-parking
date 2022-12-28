import time

from machine import Pin
from components.components import *


# Abstract class
class Publisher(Component):

    def __init__(self, publisher_location: str, publisher_id: str, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is Publisher:
            raise Exception('Error init: <Publisher is abstract class>')

        super().__init__(publisher_location, publisher_id, mqtt_client, mqtt_server)

    def connect_to_mqtt(self) -> None:
        try:
            self._mqtt_client.connect()
            self.is_connected_to_mqtt = True
            print(f'Publisher "{self._id}" mqtt connection: {self._mqtt_server}\n')
        except Exception:
            print(f'Publisher "{self._id}" mqtt connection: FAILED\n')
            self.is_connected_to_mqtt = False

    def get_topic(self) -> str:
        return "devices/parkslot1/messages/events/publishers"


class Button(Publisher):
    instance_counter = 0

    def __init__(self, sensor_location: str, pin: int, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        super().__init__(sensor_location, "button_" + str(self.instance_counter), mqtt_client, mqtt_server)
        self.__pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.__pin.irq(self.__react_on_click, Pin.IRQ_RISING)
        self.__last_detection = None

    def get_topic(self) -> str:
        return "random/button" # TODO REMOVE
        return super().get_topic() + "/buttons/" + self._id

    def __react_on_click(self, *args) -> None:
        if self.__last_detection is None or time.time() - self.__last_detection > 1:
            self.__last_detection = time.time()
            print("Button {self._id} message:")
            print(
                f'    Topic: {self.get_topic()}, JSON: {json.dumps({"pressed": "True"})}')
            try:
                self._mqtt_client.publish(self.get_topic(), json.dumps({'pressed': "True"}))
                print(f"Button {self._id} publishing status: SUCCESS\n")
            except Exception:
                self.is_connected_to_mqtt = False
                print(f"Button {self._id} publishing status: FAILURE\n")
