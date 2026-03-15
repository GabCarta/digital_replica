"""
contiene la gestione dei dati. Esegue la validazione basandosi su profiles/device.yaml 
e salva/recupera i dati dal database indicato nel profilo.
"""

import yaml


class DataService():
    def __init__(self, config_file='device.yaml'):
        self.config_file = config_file
        
    # funzione per lettura da file device.yaml per andare a recuperare i dati su db e collection
    def data_service(self):
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                db_config = config['database']
                collection_config = config['collections']
                
                return (
                    db_config['host'],
                    db_config['port'],
                    db_config['dbname'],
                    collection_config
                )
        except Exception as e:
            print(f"Errore lettura config: {e}")
            return None, None, None, None