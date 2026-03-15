"""
contiene la gestione dei messaggi MQTT. Usa broker e impostazioni salvate in profiles/device.yaml
per pubblicare messaggi e, se necessario, leggere messaggi.
"""
import paho.mqtt.client as mqtt
import yaml

class MQTTService:
    def __init__(self, config_file='device.yaml'):
        self.config_file = config_file
    # funzione per recuperare i dati relativi al broker
    def get_config_mqtt(self):
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                mqtt_conf = config['brokers']['mqtt']

                return (
                    mqtt_conf['broker_address'],
                    mqtt_conf['port'],
                    mqtt_conf['topic_subscribe']
                )
        except Exception as e:
            print(f"Errore lettura config MQTT: {e}")
            return None, None, None        

