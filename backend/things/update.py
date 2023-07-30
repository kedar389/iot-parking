import machine
from lib.umqtt.simple import MQTTClient
import json
from machine import reset



class Update:


    def __init__(self):
        self.version = 1
        self.verified_url = 'http://ourproject.sk/update.py'
        self.broker_url = "broker.hivemq.com"
        self.broker_port = 1883
        self.client_id = "pico_1"
        self.update_client = MQTTClient(self.client_id, self.broker_url, self.broker_port)
        self.update_client.set_callback(self.on_message)
        self.update_client.connect()
        self.update_client.subscribe("parking/ota/updates")
        self.print_current_version()


    def on_message(self, topic, message):
        if type(message) is bytes:
            message = message.decode("utf-8")

        try:
            message_dict = json.loads(message)
            if message_dict['url'] != self.verified_url:
                print(">> Update rejected due to unverified publisher")
            print(f">> New update available: version {message_dict['version']}")
            print(f">> Current version is: {self.version}.")
            print(">> Updating...")

            # download update
            print(f">> Downloading from {message_dict['url']}")

            print('>> Writing...')
            self.version = message_dict['version']
            print(f"Update {self.client_id} status: SUCCESS\n")
            # reset()
        except ValueError:
            print(f"Update {self.client_id} status: FAILURE - WRONG JSON FORMAT\n")
        except Exception:
            print(f"Update {self.client_id} status: FAILURE - MQTT CONNECTION FAILED\n")

    def check_for_updates(self):
        self.update_client.check_msg()

    def print_current_version(self):
        print(f'>> Running version {self.version}')
        
    def disconnect_updates(self):
        self.update_client.disconnect()
        
    def connect_updates(self):
        self.update_client.connect()


