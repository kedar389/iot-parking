from certificates.certificates_loaders import get_ssl_parameters
from components.actuators import GeneralGate, SG90Servo
from components.microcontrollers import *
from components.publishers import Button
from components.sensors import *
from components.services import GateService, LedsService, ServiceSet, ServiceType
import micropython
from lib.umqtt.simple import MQTTClient

"""
    Micropython does not support abstract classes from abc library,
    therefore is used unstandard implementation of it.  
"""

if __name__ == "__main__":
    print("BASIC STARTUP SETTINGS\n\n")
    # TODO CHANGE TO 30 OR 60 IN REAL PRODUCTION
    CYCLE_DURATION = 30

    pico = RPiPico()
    pico.start_controller()

    # Publishers
    distance_sensor = IRDistance("location_001", 15)
    pico.add_component(distance_sensor, 15, ComponentResponseType.REGULAR)

    button = Button("location_007", 14)
    pico.add_component(button, 14, ComponentResponseType.INTERRUPT)

    dht11_thermometer = DHT11Thermometer("location_001", 4)
    pico.add_component(dht11_thermometer, 4, ComponentResponseType.REGULAR)

    internal_thermometer = InternalThermometer("location_002")
    pico.add_component(internal_thermometer, pico.pin_count, ComponentResponseType.REGULAR)

    dht11_humidity_sensor = DHT11HumiditySensor("location_001", 4)
    pico.add_component(dht11_humidity_sensor, 4, ComponentResponseType.REGULAR)

    # Subscribers
    #pico.add_component(LCD("location_001", 0, 1), [0, 1])
    # TODO MAYBE SET OTHER LOCATION
    gate = SG90Servo("location_001", 12)
    pico.add_component(gate, 12, ComponentResponseType.INTERRUPT)

    # Services
    services = ServiceSet()
    gate_service = GateService("ButtonToGateService", ServiceType.INTERRUPT, button, gate)
    services.add_service(gate_service)
    # services.add_service(LedsService("efsdghtreawesfgdhjgukyi7u56rsetwasfr", distance_sensor, led))

    pico.disconnect_all(ComponentResponseType.INTERRUPT)
    services.disconnect_all(ServiceType.INTERRUPT)
    print("\n\nSTARTING MAIN CYCLE...\n\n\n")
    while True:
        start_time = time.time()
        # Health check regular components and services
        print("☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰")
        print("\n\nSTART OF ITERATION\n\n")
        print("――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("HEALTH CHECK:\n\n")
        print("Microcontroller memory log:\n", micropython.mem_info())
        pico.handle_health_check(ComponentResponseType.REGULAR)
        services.handle_health_check(ServiceType.REGULAR)

        # All sensors measure and subscribers check for messages
        print("――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("COMPONENTS AND SERVICES HANDLING:\n\n")
        pico.component_handler(ComponentResponseType.REGULAR)
        services.check_messages(ServiceType.REGULAR)
        
        pico.disconnect_all(ComponentResponseType.REGULAR)
        time.sleep(0.1)
        pico.connect_all(ComponentResponseType.INTERRUPT)
        services.connect_all(ServiceType.INTERRUPT)

        # Health check interrupt components and services
        print("――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("HEALTH CHECK:\n\n")
        print("Microcontroller memory log:\n", micropython.mem_info())
        pico.handle_health_check(ComponentResponseType.INTERRUPT)
        services.handle_health_check(ServiceType.INTERRUPT)

        # Checking interrupt events in services and components while waiting for
        # time to pass to new iteration of measurement
        print("――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("COMPONENTS AND SERVICES HANDLING:\n\n")
        while time.time() - start_time < CYCLE_DURATION:
            services.check_messages(ServiceType.INTERRUPT)
            pico.component_handler(ComponentResponseType.INTERRUPT)
            time.sleep(0.5)

        pico.disconnect_all(ComponentResponseType.INTERRUPT)
        services.disconnect_all(ServiceType.INTERRUPT)
        
        time.sleep(0.1)
        pico.connect_all(ComponentResponseType.REGULAR)
        services.connect_all(ServiceType.REGULAR)
        print("――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("\n\nEND OF ITERATION\n\n")
