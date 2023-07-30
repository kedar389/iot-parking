from certificates.certificates_loaders import get_ssl_parameters
from components.actuators import GeneralGate, SG90Servo, LCD, LED
from components.microcontrollers import *
from components.publishers import Button
from components.sensors import *
from components.services import GateService, LedsService, ServiceSet, ServiceType, LCDService
import micropython
from lib.umqtt.simple import MQTTClient
from machine import WDT
from update import *

"""
    Micropython does not support abstract classes from abc library,
    therefore is used unstandard implementation of it.  
"""

if __name__ == "__main__":
    print("BASIC STARTUP SETTINGS\n\n")
    CYCLE_DURATION = 30

    pico = RPiPico()
    pico.start_controller()
    
    # ota = Update()
    database_mqtt = MQTTClient(client_id="parkslot1",
                                           server="parking-iot-hub.azure-devices.net",
                                           port=8883,
                                           user="parking-iot-hub.azure-devices.net/parkslot1/?api-version=2021-04-12",
                                           password="SharedAccessSignature sr=parking-iot-hub.azure-devices.net%2Fdevices%2Fparkslot1&sig=xvah6HtPd1u9WcGSxaSxVVOSqu%2BS9OtSBKuL8Z1yrG8%3D&se=4672927147",
                                           keepalive=3600,
                                           ssl=True,
                                           ssl_params=get_ssl_parameters())


    # Publishers
    distance_sensor = IRDistance("location_001", 15)
    pico.add_component(distance_sensor, 15, ComponentResponseType.REGULAR)
    
    # distance_sensor_database = IRDistance("location_001", 15, mqtt_client=database_mqtt)
    # pico.add_component(distance_sensor_database, 15, ComponentResponseType.INTERRUPT)

    button = Button("location_002", 14)
    pico.add_component(button, 14, ComponentResponseType.INTERRUPT)

    # dht11_thermometer = DHT11Thermometer("location_001", 4, mqtt_client=database_mqtt)
    # pico.add_component(dht11_thermometer, 4, ComponentResponseType.REGULAR)

    # internal_thermometer = InternalThermometer("location_001", mqtt_client=database_mqtt)
    # pico.add_component(internal_thermometer, pico.pin_count, ComponentResponseType.REGULAR)

    # dht11_humidity_sensor = DHT11HumiditySensor("location_001", 4, mqtt_client=database_mqtt)
    # pico.add_component(dht11_humidity_sensor, 4, ComponentResponseType.REGULAR)

    # Subscriberss
    gate = SG90Servo("location_002", 12)
    pico.add_component(gate, 12, ComponentResponseType.INTERRUPT)

    lcd = LCD("location_002", 0, 1)
    pico.add_component(lcd, [0, 1], ComponentResponseType.REGULAR)
    
    led = LED("location_001", 11, 16)
    pico.add_component(led, [11, 16], ComponentResponseType.REGULAR)

    

    # Services
    services = ServiceSet()
    gate_service = GateService("ButtonToGateService", ServiceType.INTERRUPT, button, gate)
    services.add_service(gate_service)
    lcd_service = LCDService("DistanceToLCDService", ServiceType.REGULAR, distance_sensor, lcd)
    services.add_service(lcd_service)

    leds_service = LedsService("DistanceToLedsService", ServiceType.REGULAR, distance_sensor, led)
    services.add_service(leds_service)

    pico.disconnect_all(ComponentResponseType.INTERRUPT)
    services.disconnect_all(ServiceType.INTERRUPT)
    print("\n\nSTARTING MAIN CYCLE...\n\n\n")

    # watch_dog_timer = WDT(timeout=CYCLE_DURATION*2)
    while True:
        start_time = time.time()
        # watch_dog_timer.feed()
        # ota.check_for_updates()
        # Health check regular components and services
        print("☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰")
        print("\n\nSTART OF ITERATION\n\n")
        print(
            "――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("HEALTH CHECK:\n\n")
        print("Microcontroller memory log:\n", micropython.mem_info())
        pico.handle_health_check(ComponentResponseType.REGULAR)
        services.handle_health_check(ServiceType.REGULAR)
        # All sensors measure and subscribers check for messages
        print(
            "――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("COMPONENTS AND SERVICES HANDLING:\n\n")
        time.sleep(0.5)
        while time.time() - start_time < 4:
            lcd.reset_spaces_left()
            services.check_messages(ServiceType.REGULAR)
            pico.component_handler(ComponentResponseType.REGULAR)
            time.sleep(1)
        pico.disconnect_all(ComponentResponseType.REGULAR)
        services.disconnect_all(ServiceType.REGULAR)
        time.sleep(0.1)
        pico.connect_all(ComponentResponseType.INTERRUPT)
        services.connect_all(ServiceType.INTERRUPT)
        # Health check interrupt components and services
        print(
            "――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("HEALTH CHECK:\n\n")
        print("Microcontroller memory log:\n", micropython.mem_info())
        pico.handle_health_check(ComponentResponseType.INTERRUPT)
        services.handle_health_check(ServiceType.INTERRUPT)
        # Checking interrupt events in services and components while waiting for
        # time to pass to new iteration of measurement
        print(
            "――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("COMPONENTS AND SERVICES HANDLING:\n\n")
        while time.time() - start_time < CYCLE_DURATION:
            services.check_messages(ServiceType.INTERRUPT)
            pico.component_handler(ComponentResponseType.INTERRUPT)
            time.sleep(1)
        pico.disconnect_all(ComponentResponseType.INTERRUPT)
        services.disconnect_all(ServiceType.INTERRUPT)
        time.sleep(0.1)
        pico.connect_all(ComponentResponseType.REGULAR)
        services.connect_all(ServiceType.REGULAR)
        print(
            "――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――")
        print("\n\nEND OF ITERATION\n\n")