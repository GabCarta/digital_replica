"""
contiene la gestione della connessione al database. 
Fornisce funzioni per aprire la connessione usando l’indirizzo salvato nel profilo e
per leggere/scrivere dati.
"""
import pymongo


class DB_connection:
    def __init__(self):
        self.db = None
        self.config = {}
    # funzione utilizzata per andare a stabilire la connessione con il db
    def get_connection(self, json_postman=None):
        if self.db is not None:
            return self.db, self.config

        if json_postman is None or 'database' not in json_postman:
            return None, None

        try:
            self.config = json_postman
            db_conf = self.config['database']

            client = pymongo.MongoClient(
                host=db_conf['host'],
                port=db_conf['port'],
                serverSelectionTimeoutMS=5000
            )

            self.db = client[db_conf['dbname']]  
            self.db.command('ping')
            print("Stato: Connessione al DB avvenuta con successo")
            return self.db, self.config

        except Exception as e:
            print(f"Stato: Errore durante connessione DB: {e}")
            return None, None

    # funzione utilizzata per creare/aggiornare il profilo
    def update_config_and_create(self, json_postman, security_key):
        if not json_postman:
            return
            
        if 'collections' in json_postman:
            self.config['collections'] = json_postman['collections']
            self.create_collections()
    
        if self.db is not None:
            try:
                profile_data = json_postman.get("Profile", {})
                device_id = profile_data.get("id")
                
                if device_id:
                    dati_device = {
                        "id": device_id,
                        "Profile": profile_data,
                    }
                    self.db['registered_devices'].update_one(
                        {"id": device_id},
                        {"$set": dati_device},
                        upsert=True
                    )
                    print(f"Stato: Profilo dispositivo con ID {device_id} salvato/aggiornato in DB")
                else:
                    print("Stato: ID dispositivo non presente, impossibile salvare profilo in DB")
            except Exception as e:
                print(f"Stato: Errore durante salvataggio profilo dispositivo in DB: {e}")

    # funzione per la creazione delle collection
    def create_collections(self):
        if self.db is None:
            print("Nessuna connessione al db")
            return

        try:
            table = self.config.get('collections', {})
            existing = self.db.list_collection_names()
            
            for nome_logico, regole in table.items():
                nome_collezione = regole['db_collection_name']
                if nome_collezione not in existing:
                    self.db.create_collection(nome_collezione)
                    print(f"collezione creata: {nome_collezione}")
        except Exception as e:
            print(f"errore collezione: {e}")
            
# Creazione dell'istanza
db_instance = DB_connection()