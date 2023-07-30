import json

from lib.umqtt.simple import MQTTClient
from certificates.certificates_loaders import get_ssl_parameters


# Abstract class
class Component:
    def __init__(self, location: str, component_id: str, mqtt_client: MQTTClient = None,
                 mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is Component:
            raise Exception('Error init: <Component is abstract class>')

        self._location = location
        self._id = component_id
        self._mqtt_server = mqtt_server

        if mqtt_client is None:
            # self._mqtt_client = MQTTClient(client_id="parkslot1",
            #                                server="parking-iot-hub.azure-devices.net",
            #                                port=8883,
            #                                user="parking-iot-hub.azure-devices.net/parkslot1/?api-version=2021-04-12",
            #                                password="SharedAccessSignature sr=parking-iot-hub.azure-devices.net%2Fdevices%2Fparkslot1&sig=xvah6HtPd1u9WcGSxaSxVVOSqu%2BS9OtSBKuL8Z1yrG8%3D&se=4672927147",
            #                                keepalive=3600,
            #                                ssl=True,
            #                                ssl_params=get_ssl_parameters())
            self._mqtt_client = MQTTClient(self._id, "broker.hivemq.com", keepalive=3600)
        else:
            self._mqtt_client = mqtt_client

        self.is_connected_to_mqtt = False
        self.connect_to_mqtt()

    def connect_to_mqtt(self) -> None:
        raise NotImplementedError("All subclasses of Component must have implemented function for mqtt connection!")

    def print_id(self) -> None:
        print(self._id, end="")

    def reconnect(self) -> None:
        try:
            self._mqtt_client.disconnect()
            self.is_connected_to_mqtt = False
            self._mqtt_client.connect()
            self.is_connected_to_mqtt = True
            print(f"Component {self._id} reconnecting status: SUCCESS\n")
        except Exception:
            print(f"Component {self._id} reconnecting status: FAILURE\n")

    def disconnect(self):
        try:
            self._mqtt_client.disconnect()
            self.is_connected_to_mqtt = False
        except Exception:
            print(f"Component {self._id} disconnecting status: FAILURE\n")

    def health_check(self) -> (bool, json):
        return self.is_connected_to_mqtt, json.dumps({"mqtt_connection": self.is_connected_to_mqtt})
