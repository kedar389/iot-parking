import machine
import json
from machine import Pin
import dht
from components.publishers import Publisher
from lib.umqtt.simple import MQTTClient

# TODO: change topics when ready
# Abstract class
class Sensor(Publisher):
    __current_measurement = None

    def __init__(self, sensor_location: str, sensor_id: str, spec_attr_name: str, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is Sensor:
            raise Exception('Error init: <Sensor is abstract class>')

        super().__init__(sensor_location, sensor_id, mqtt_client, mqtt_server)
        self._spec_attr_name = spec_attr_name

    def params_to_json(self) -> json:
        param_combined = {
            'sensor_location': self._location,
            'sensor_id': self._id,
            self._spec_attr_name: self.__current_measurement
        }

        return json.dumps(param_combined)

    def measure(self) -> None:
        raise NotImplementedError("All subclasses of Sensor must have implemented function for measurement!")

    def get_topic(self) -> str:
        return super().get_topic() + "/sensors"

    def publish_measurement(self) -> None:
        print(f"Sensor {self._id} message:")
        print(f'    Topic: {self.get_topic()}, Measurement: {self.__current_measurement}, JSON: {self.params_to_json()}')
        if self.is_connected_to_mqtt:
            try:
                self._mqtt_client.publish(self.get_topic(), self.params_to_json())
                print(f"Sensor {self._id} publishing status: SUCCESS\n")
            except Exception:
                self.is_connected_to_mqtt = False
                print(f"Sensor {self._id} publishing status: FAILURE - MQTT CONNECTION FAILED\n")
        else:
            print(f"Sensor {self._id} publishing status: FAILURE - MQTT NOT CONNECTED\n")


"""
    Maybe set instance counter here, with names only thermometer
"""


# Abstract class
class GeneralThermometer(Sensor):
    def __init__(self, sensor_location: str, sensor_id: str, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is GeneralThermometer:
            raise Exception('Error init: <GeneralThermometer is abstract class>')
        super().__init__(sensor_location, sensor_id, "temperature", mqtt_client, mqtt_server)

    def get_topic(self) -> str:
        return super().get_topic() + "/thermometers/" + self._id
        # return "devices/parkslot1/messages/events/"


# Abstract class
class GeneralHumiditySensor(Sensor):
    def __init__(self, sensor_location: str, sensor_id: str, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is GeneralHumiditySensor:
            raise Exception('Error init: <GeneralHumiditySensor is abstract class>')
        super().__init__(sensor_location, sensor_id, "humidity", mqtt_client, mqtt_server)

    def get_topic(self) -> str:
        return super().get_topic() + "/humidity_sensors/" + self._id
        # return "devices/parkslot1/messages/events/"

# Abstract class
class GeneralDistanceSensor(Sensor):
    def __init__(self, sensor_location: str, sensor_id: str, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        if type(self) is GeneralDistanceSensor:
            raise Exception('Error init: <GeneralDistanceSensor is abstract class>')
        super().__init__(sensor_location, sensor_id, "distance", mqtt_client, mqtt_server)

    def get_topic(self) -> str:
        return super().get_topic() + "/distance_sensors/" + self._id
        # return "distance_sensors/" + self._id
        # return "devices/parkslot1/messages/events/"


class InternalThermometer(GeneralThermometer):
    __current_measurement = None
    instance_counter = 0

    def __init__(self, sensor_location: str, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        super().__init__(sensor_location, "internal_thermometer_" + str(self.instance_counter), mqtt_client, mqtt_server)
        InternalThermometer.instance_counter += 1

    def measure(self) -> None:
        temp_sensor = machine.ADC(4)
        conversion_factor = 3.3 / 65535
        reading = temp_sensor.read_u16() * conversion_factor
        self.__current_measurement = 27 - (reading - 0.706) / 0.001721


"""
    Cannot have DHT11 sensors in one class, because there would be only
    one mqtt connection, which would then violate mqtt scheme. Changing
    the class to support multiple mqtt connections would be more complicated.
"""
"""
    3v3 -> power
    GP4 -> com
"""


class DHT11Thermometer(GeneralThermometer):
    __current_measurement = None
    instance_counter = 0

    def __init__(self, sensor_location: str, pin: int, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        super().__init__(sensor_location, "dht11_thermometer_" + str(self.instance_counter), mqtt_client, mqtt_server)
        self.__pin = Pin(pin, Pin.OUT, Pin.PULL_DOWN)
        self.__internal_sensor = dht.DHT11(self.__pin)
        self.__is_sensor_working = True

    def measure(self) -> None:
        try:
            self.__internal_sensor.measure()
            self.__current_measurement = self.__internal_sensor.temperature()
            self.__is_sensor_working = True
        except OSError:
            self.__current_measurement = None
            self.__is_sensor_working = False
            print(f"DHT sensor {self._id} not working properly\n")

    def health_check(self) -> (bool, json):
        healthy, health_report = super().health_check()
        health_report = json.loads(health_report)
        health_report["sensor_working"] = self.__is_sensor_working
        return healthy and self.__is_sensor_working, json.dumps(health_report)


"""
    3v3 -> power
    GP4 -> com
"""


class DHT11HumiditySensor(GeneralHumiditySensor):
    __current_measurement = None
    instance_counter = 0

    def __init__(self, sensor_location: str, pin: int, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        super().__init__(sensor_location, "dht11_humidity_sensor_" + str(self.instance_counter), mqtt_client, mqtt_server)
        self.__pin = Pin(pin, Pin.OUT, Pin.PULL_DOWN)
        self.__internal_sensor = dht.DHT11(self.__pin)
        self.__is_sensor_working = True

    def measure(self) -> None:
        try:
            self.__internal_sensor.measure()
            self.__current_measurement = self.__internal_sensor.humidity()
        except OSError:
            self.__current_measurement = None
            self.__is_sensor_working = False
            print(f"DHT sensor {self._id} not working properly\n")

    def health_check(self) -> (bool, json):
        healthy, health_report = super().health_check()
        health_report = json.loads(health_report)
        health_report["sensor_working"] = self.__is_sensor_working
        return healthy and self.__is_sensor_working, json.dumps(health_report)


"""
    3V3 -> power
    GP15 -> com
"""
class IRDistance(GeneralDistanceSensor):
    __current_measurement = None
    instance_counter = 0

    def __init__(self, sensor_location: str, pin: int, mqtt_client: MQTTClient = None, mqtt_server: str = "iot-hub-parking.azure-devices.net"):
        super().__init__(sensor_location, "distance_sensor_" + str(self.instance_counter), mqtt_client, mqtt_server)
        self.__pin = Pin(pin, Pin.IN)
        self.__is_sensor_working = True

    def measure(self) -> None:
        try:
            self.__current_measurement = self.__pin.value()
        except OSError:
            self.__current_measurement = None
            self.__is_sensor_working = False
            print(f"Distance sensor {self._id} not working properly\n")

    def health_check(self) -> (bool, json):
        healthy, health_report = super().health_check()
        health_report = json.loads(health_report)
        health_report["sensor_working"] = self.__is_sensor_working
        return healthy and self.__is_sensor_working, json.dumps(health_report)