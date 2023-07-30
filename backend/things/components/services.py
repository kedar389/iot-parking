import json
import time

from components.publishers import Button, Publisher
from components.sensors import GeneralDistanceSensor
from lib.umqtt.simple import MQTTClient
from components.actuators import LED, GeneralGate, Actuator, LCD
from certificates.certificates_loaders import get_ssl_parameters


# enum lib does not exist in micropython
class ServiceType:
    REGULAR = 1
    INTERRUPT = 2


# Abstract class
class Service:
    def __init__(self, service_id: str, service_type: ServiceType, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is Service:
            raise Exception('Error init: <Service is abstract class>')

        self._id = service_id
        self._mqtt_server = mqtt_server
        self.service_type = service_type
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
        raise NotImplementedError("All subclasses of Service must have implemented function for mqtt connection!")

    def disconnect(self) -> None:
        try:
            self._mqtt_client.disconnect()
            self.is_connected_to_mqtt = False
        except Exception:
            print(f"Service {self._id} disconnecting status: FAILURE\n")

    def health_check(self) -> (bool, json):
        return self.is_connected_to_mqtt, json.dumps({"mqtt_connection": self.is_connected_to_mqtt})

    def print_id(self) -> None:
        print(self._id, end="")


class ServiceSet:
    def __init__(self):
        self.__services = set()

    def add_service(self, service: Service):
        self.__services.add(service)

    def remove_service(self, service: Service):
        self.__services.discard(service)

    def handle_health_check(self, service_type: ServiceType):
        for service in self.__services:
            if service.service_type == service_type:
                print("Service ", end="")
                service.print_id()
                healthy, health_report = service.health_check()
                print(f" health status: \"{'HEALTHY' if healthy else 'UNHEALTHY'}\" | full report: \"{health_report}\"\n")

                if not service.is_connected_to_mqtt:
                    service.connect_to_mqtt()

    def check_messages(self, service_type: ServiceType):
        for service in self.__services:
            # If is instance of all service subclasses, which support "check_message()" function
            if isinstance(service, ServicePublisherToActuator) and service.service_type == service_type:
                service.check_message()

    def disconnect_all(self, service_type: ServiceType):
        for service in self.__services:
            if service.service_type == service_type:
                service.disconnect()

    def connect_all(self, service_type: ServiceType):
        for service in self.__services:
            if service.service_type == service_type:
                service.connect_to_mqtt()


# Abstract class
class ServicePublisherToActuator(Service):
    def __init__(self, service_id: str, service_type: ServiceType, publisher: Publisher, actuator: Actuator, mqtt_client: MQTTClient = None,
                 mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is ServicePublisherToActuator:
            raise Exception('Error init: <ServicePublisherToActuator is abstract class>')

        self._subscription_topic = publisher.get_topic()
        self._publishing_topic = actuator.subscription_topic
        super().__init__(service_id, service_type, mqtt_client, mqtt_server)

    def connect_to_mqtt(self) -> None:
        try:
            self._mqtt_client.set_callback(self._react_to_message)
            self._mqtt_client.connect()
            self._set_subscription()
            self.is_connected_to_mqtt = True
            print(f'Service "{self._id}" mqtt connection: {self._mqtt_server}\n')
        except OSError:
            print(f'Service "{self._id}" mqtt connection: FAILED\n')
            self.is_connected_to_mqtt = False

    def _react_to_message(self, topic: str, message: str) -> None:
        raise NotImplementedError("All subclasses of ServicePublisherToActuator must have implemented function for "
                                  "message reaction!")

    def _set_subscription(self) -> None:
        self._mqtt_client.subscribe(self._subscription_topic)

    def check_message(self) -> None:
        if self.is_connected_to_mqtt:
            try:
                self._mqtt_client.check_msg()
            except Exception:
                print(f'Service "{self._id}" mqtt connection: FAILED\n')
                self.is_connected_to_mqtt = False


class GateService(ServicePublisherToActuator):
    def __init__(self, service_id: str, service_type: ServiceType, button: Button, gate: GeneralGate, mqtt_client: MQTTClient = None,
                 mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        super().__init__(service_id, service_type, button, gate, mqtt_client, mqtt_server)

    def _react_to_message(self, topic: str, message: str) -> None:
        if type(message) is bytes:
            message = message.decode("utf-8")

        try:
            message_dict = json.loads(message)
            if "pressed" not in message_dict:
                raise ValueError

            if message_dict.get("pressed") == "True":
                self._mqtt_client.publish(self._publishing_topic, json.dumps({"open": "True"}))
                time.sleep(2)
                self._mqtt_client.publish(self._publishing_topic, json.dumps({"close": "True"}))

            print(f"Service {self._id} reaction status: SUCCESS\n")
        except ValueError:
            print(f"Service {self._id} reaction status: FAILURE - WRONG JSON FORMAT\n")
        except Exception:
            print(f"Service {self._id} reaction status: FAILURE - MQTT CONNECTION FAILED\n")
            self.is_connected_to_mqtt = False


class LedsService(ServicePublisherToActuator):
    def __init__(self, service_id: str, service_type: ServiceType, distance_sensor: GeneralDistanceSensor, leds: LED, mqtt_client: MQTTClient = None,
                 mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        super().__init__(service_id, service_type, distance_sensor, leds, mqtt_client, mqtt_server)

    def _react_to_message(self, topic: str, message: str) -> None:
        if type(message) is bytes:
            message = message.decode("utf-8")

        try:
            message_dict = json.loads(message)
            if "distance" not in message_dict:
                raise ValueError
            if message_dict.get("distance") == 1:
                self._mqtt_client.publish(self._publishing_topic, json.dumps({"occupied": "True"}))
            elif message_dict.get("distance") == 0:
                self._mqtt_client.publish(self._publishing_topic, json.dumps({"occupied": "False"}))
            print(f"Service {self._id} reaction status: SUCCESS\n")
        except ValueError:
            print(f"Service {self._id} reaction status: FAILURE - WRONG JSON FORMAT\n")
        except Exception:
            print(f"Service {self._id} reaction status: FAILURE - MQTT CONNECTION FAILED\n")
            self.is_connected_to_mqtt = False


class LCDService(ServicePublisherToActuator):

    def __init__(self, service_id: str, service_type: ServiceType, distance_sensor: GeneralDistanceSensor, lcd: LCD,
                 mqtt_client: MQTTClient = None,
                 mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        super().__init__(service_id, service_type, distance_sensor, lcd, mqtt_client, mqtt_server)

    def _react_to_message(self, topic: str, message: str) -> None:
        if type(message) is bytes:
            message = message.decode("utf-8")

        try:
            message_dict = json.loads(message)
            if "distance" not in message_dict:
                raise ValueError
            if message_dict.get("distance") == 1:
                self._mqtt_client.publish(self._publishing_topic, json.dumps({'occupied': 'True'}))
            elif message_dict.get("distance") == 0:
                self._mqtt_client.publish(self._publishing_topic, json.dumps({'occupied': 'False'}))
            print(f"Service {self._id} reaction status: SUCCESS\n")
        except ValueError:
            print(f"Service {self._id} reaction status: FAILURE - WRONG JSON FORMAT\n")
        except Exception:
            print(f"Service {self._id} reaction status: FAILURE - MQTT CONNECTION FAILED\n")
            self.is_connected_to_mqtt = False
