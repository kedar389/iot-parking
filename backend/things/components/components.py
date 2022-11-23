# TODO: MAYBE CHANGE TO ALL COMPONENTS WLAN CONNECTION, BUT NOT SURE HOW IT IS SUPPOSED TO WORK
from lib.umqtt.simple import MQTTClient


# Abstract class
class Component:
    def __init__(self, location: str, component_id: str, mqtt_server: str = "broker.hivemq.com"):
        if type(self) is Component:
            raise Exception('Error init: <Component is abstract class>')

        self._location = location
        self._id = component_id
        self._mqtt_server = mqtt_server
        self._mqtt_client = MQTTClient(component_id, self._mqtt_server, keepalive=3600)

        self.is_connected_to_mqtt = False
        self.connect_to_mqtt()

    def connect_to_mqtt(self) -> None:
        raise NotImplementedError("All subclasses of Component must have implemented function for mqtt connection!")
