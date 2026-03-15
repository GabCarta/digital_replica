"""
contiene la creazione e l’aggiornamento del file profiles/device.yaml
a partire dal profilo ricevuto in registrazione, e la lettura del profilo 
quando arrivano richieste successive.
"""

from flask import Flask, request, jsonify
from database import db_instance
import os
import yaml
import json


app= Flask(__name__)
@app.route('/api/service_pf', methods=['GET','POST'])
def maintenance_profile():

    # percorso del file di configurazione del profilo dispositivo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    target_path = os.path.join(root_dir, 'profile')
    file_patch = os.path.join(target_path, "device.json")
    
    # Controllo se il file del profilo dispositivo esiste
    if not os.path.exists(file_patch):
        return jsonify({"Stato": "Errore: Nessun profilo dispositivo presente"}), 400
    # Se il file esiste, vado a gestire le richieste GET e POST
    if request.method == 'GET':
        try:
            with open(file_patch, 'r') as f:
                device_profile = yaml.safe_load(f)
            return jsonify({"messaggio": f"Dati Profilo salvati: {device_profile['id']}"}), 200
        except Exception as e:
            return jsonify({"Stato": f"Errore durante lettura profilo dispositivo: {e}"}), 500
   
    # POST per aggiornare il profile e passo la configurazione aggiornata su Postman
    elif request.method == 'POST':
        new_profile = request.get_json()
        if not new_profile:
            return jsonify({"Stato": "Errore: Nessun dato ricevuto"}), 400
            
        try:
            # Apertura file modalità lettura
            with open(file_patch, 'r') as f:
                old_profile = yaml.safe_load(f) or {}
                
            # recupero la chiave presente nel file json
            file_patch_json = os.path.join(target_path, "device.json")
            old_key = None
            if os.path.exists(file_patch_json):
                with open(file_patch_json, 'r') as f_json:
                    old_device_data = json.load(f_json)
                    old_key = old_device_data.get("security", {}).get("security_key")
                
            # aggiorno il profilo
            updated_profile = {
                "Profile": new_profile.get("Profile", old_profile.get("Profile")),
                "database": new_profile.get("database", old_profile.get("database")),
                "collections": new_profile.get("collections", old_profile.get("collections")),
                "brokers": new_profile.get("brokers", old_profile.get("brokers")),
                "security": {
                    "security_key": old_key
                }
            }  
            
            # salvataggio modifiche nel file yaml
            with open(file_patch, 'w') as f:
                yaml.dump(updated_profile, f, default_flow_style=False, sort_keys=False)
            
            # salvataggio modifiche nel file json
            device_json_data = {
                "id": updated_profile.get("Profile", {}).get("id"),
                "security": {
                    "security_key": old_key
                }
            }
            with open(file_patch_json, 'w') as f_json:
                json.dump(device_json_data, f_json, indent=4)
            
            # aggiornamento profile presente nel db
            db, _ = db_instance.get_connection(updated_profile)
            if db is not None:
                db_instance.update_config_and_create(updated_profile, old_key)
            
            return jsonify({"Stato": "Profilo dispositivo aggiornato con successo"}), 200
            
        except Exception as e:
            return jsonify({"Stato": f"Errore aggiornamento profilo dispositivo: {e}"}), 500