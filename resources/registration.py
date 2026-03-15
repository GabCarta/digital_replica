"""
Contiene la chiamata HTTP di registrazione. Riceve dal dispositivo
il profilo della digital replica, inclusi indirizzo broker MQTT e indirizzo database.
Salva le informazioni su file yaml/json, aggiorna il database e
restituisce l'esito della registrazione con la chiave generata.
"""
from flask import Flask, request, jsonify
import json
import yaml
import os
from database import db_instance
import security

app = Flask(__name__)

@app.route('/api/registration', methods=['POST'])
def registration_pf():
    #  Lettura dei dati ricevuti
    received_config = request.get_json()
    
    if not received_config:
        return jsonify({"Stato": "Errore: Nessun dato ricevuto"}), 400

    #  Generazione della chiave segreta
    security_key = security.create_key()
    print(f"Chiave privata generata: {security_key}")

    # Estrazione dati per la creazione dei file
    device_id = received_config.get("Profile", {}).get("id")
    
    profile = {
        "id": device_id,
        "Profile": received_config.get("Profile"),
        "database": received_config.get("database"),
        "collections": received_config.get("collections"),
        "brokers": received_config.get("brokers")
    }
    
    device = {
        "id": device_id,
        "security": {
            "security_key": security_key
        }
    }

     # Configurazione dei percorsi per il salvataggio dei file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    target_path = os.path.join(root_dir, 'profile')
    file_path_yaml = os.path.join(target_path, "device.yaml")
    file_path_json = os.path.join(target_path, "device.json")

    # Verifica della connessione al database
    db, _ = db_instance.get_connection(received_config)
    if db is None:
        return jsonify({"Stato": "Errore DB: Impossibile connettersi a mio_mongo"}), 500

    # Esecuzione delle operazioni di scrittura e aggiornamento
    try:
        # Creazione della cartella 'profile' se non esiste
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        # Scrittura sul file device.yaml
        with open(file_path_yaml, 'w') as f_yaml:
            yaml.dump(profile, f_yaml)
            
        # Scrittura sul file device.json
        with open(file_path_json, 'w') as f_json:
            json.dump(device, f_json, indent=4)

        # Aggiunta / aggiornamento sul database
        db_instance.update_config_and_create(received_config, security_key.strip())

        # Restituiamo la chiave segreta
        return jsonify({
            "Stato": "Registrazione dispositivo avvenuta con successo",
            "chiave": security_key
        }), 200

    except Exception as e:
        return jsonify({"Stato": f"Errore durante registrazione dispositivo: {e}"}), 500