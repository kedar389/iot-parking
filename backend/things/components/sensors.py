import machine
import json
from machine import Pin
import dht
from components.components import Component


# Abstract class
class Sensor(Component):
    __current_measurement = None

    def __init__(self, sensor_location: str, sensor_id: str, spec_attr_name: str):
        if type(self) is Sensor:
            raise Exception('Error init: <Sensor is abstract class>')

        super().__init__(sensor_location, sensor_id)
        self._spec_attr_name = spec_attr_name

    def connect_to_mqtt(self) -> None:
        try:
            self._mqtt_client.connect()
            self.is_connected_to_mqtt = True
            print(f'Sensor "{self._id}" -> mqtt connection: {self._mqtt_server}\n')
        except OSError:
            print(f'Sensor "{self._id}" -> mqtt connection: FAILED\n')

    def params_to_json(self) -> json:
        """
        if isinstance(self.__current_measurement, float):
            self.__current_measurement = round(self.__current_measurement, 2)
        """
        param_combined = {
            'sensor_location': self._location,
            'sensor_id': self._id,
            self._spec_attr_name: self.__current_measurement
        }

        return json.dumps(param_combined)

    def measure(self) -> None:
        raise NotImplementedError("All subclasses of Sensor must have implemented function for measurement!")

    def get_topic(self) -> str:
        return "sensors"

    def publish_measurement(self) -> None:
        self._mqtt_client.publish(self.get_topic(), self.params_to_json())


"""
    Maybe set instance counter here, with names only thermometer
"""
# Abstract class
class GeneralThermometer(Sensor):
    def __init__(self, sensor_location: str, sensor_id: str):
        if type(self) is GeneralThermometer:
            raise Exception('Error init: <GeneralThermometer is abstract class>')
        super().__init__(sensor_location, sensor_id, "temperature")

    def get_topic(self) -> str:
        return super().get_topic() + "/thermometers"


class InternalThermometer(GeneralThermometer):
    __current_measurement = None
    instance_counter = 0

    def __init__(self, sensor_location: str):
        super().__init__(sensor_location, "internal_thermometer#" + str(self.instance_counter))
        InternalThermometer.instance_counter += 1

    def measure(self) -> None:
        temp_sensor = machine.ADC(4)
        conversion_factor = 3.3 / 65535
        reading = temp_sensor.read_u16() * conversion_factor
        self.__current_measurement = 27 - (reading - 0.706) / 0.001721


"""
    3v3 -> power
    GP0 -> com
"""
class ExternalThermometer(GeneralThermometer):
    """
        Assumpting using ONLY DHT11 sensors.
        For usage of other create separate classes renamed accordingly.
        DHT11 could potentially be used for humidity. In that case we need
        to change RPiPico array, which do not allow us to have multiple
        sensors on one pin.
    """
    __current_measurement = None
    instance_counter = 0

    def __init__(self, sensor_location: str, pin: int):
        super().__init__(sensor_location, "external_thermometer#" + str(self.instance_counter))
        self.__pin = Pin(pin, Pin.OUT, Pin.PULL_DOWN)
        self.__internal_sensor = dht.DHT11(self.__pin)

    def measure(self) -> None:
        self.__internal_sensor.measure()
        self.__current_measurement = self.__internal_sensor.temperature()
