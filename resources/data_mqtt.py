"""
contiene la chiamata HTTP dedicata ai comandi verso MQTT. 
Contiene la chiamata tipo setData e usa le informazioni MQTT salvate in profiles/device.yaml.
"""
from flask import Flask, request, jsonify
import json
import paho.mqtt.client as mqtt
from database import db_instance
import datetime
from services.mqtt_service import MQTTService
from security import check_key
import os

app = Flask(__name__)

@app.route('/api/setData', methods=['POST'])
def set_data():
    # verifica dati ricevuti
    comando_dict = request.get_json()
    if not comando_dict:
        return jsonify({"status": "Errore: Nessun dato ricevuto"}), 400
    
    # estrazione dati essenziali
    sender_id = comando_dict.get('sender_id')   
    id_dispositivo = comando_dict.get('id')     
    received_key = comando_dict.get('security_key') 

    if not id_dispositivo or not sender_id:
        return jsonify({"status": "Errore: Mancano id o sender_id"}), 400
    
    # connessione al DB 
    db, config = db_instance.get_connection()
    if db is None:
        return jsonify({
            "status": "Errore DB", 
            "messaggio": "DB non connesso. Esegui prima una chiamata di registrazione per connettere il server."
        }), 500

    # controllo chiave di sicurezza
    authorized = check_key(sender_id, received_key)
    if not authorized:
        return jsonify({"status": "Errore: Chiave di sicurezza non trovata o non valida"}), 403

    # per evitare di salvare i dati sensibili nel db
    temp_dict = comando_dict.copy()
    if 'sender_id' in temp_dict:
        del temp_dict['sender_id']
    if 'security_key' in temp_dict:
        del temp_dict['security_key']
    
    #percorso del mio file device.yaml
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir) 
    percorso_yaml = os.path.join(root_dir, 'profile', 'device.yaml')
    
    # estrazione configurazione MQTT da file e validazione dati
    mqtt_service = MQTTService(config_file=percorso_yaml)
    broker_address, broker_port, topic_base = mqtt_service.get_config_mqtt()
    if not broker_address or not broker_port or not topic_base:
        return jsonify({"status": "Errore: Config MQTT non valida"}), 500
    
    # estraiamo le chiavi ricevute per confrontarle con quelle richieste dai template
    keys_ricevute = set(temp_dict.keys())
    nome_collezione_target = None
    
    # inizio dei controlli sui template definiti in fase di configurazione (device.yaml)
    for _, rules in config.get('collections', {}).items():
        raw_req = rules['required_fields']
        required_keys = set(raw_req.keys()) if isinstance(raw_req, dict) else set(raw_req)

        if not required_keys.issubset(keys_ricevute):
            continue
            
        allowed_id = rules.get('allowed_id', [])
        if allowed_id and id_dispositivo not in allowed_id:
            continue
            
        valori_ok = True
        allowed_values_map = rules.get('allowed_values', {})
        for campo, regole_ammese in allowed_values_map.items():
            if campo in temp_dict:
                valore_ricevuto = temp_dict[campo]
                
                # check sui valori ammessi
                if isinstance(regole_ammese, list):
                    if valore_ricevuto not in regole_ammese:
                        valori_ok = False
                        break
                
                # check sul tipo di dato
                elif isinstance(regole_ammese, str):
                    if regole_ammese == "float" and not isinstance(valore_ricevuto, (float, int)):
                        valori_ok = False
                        break
                    elif regole_ammese == "string" and not isinstance(valore_ricevuto, str):
                        valori_ok = False
                        break
                    elif regole_ammese == "int" and not isinstance(valore_ricevuto, int):
                        valori_ok = False
                        break
        if not valori_ok:
            continue
        
        # Salvataggio nel DB 
        orario_invio_comando= datetime.datetime.now()
        nome_collezione_target = rules['db_collection_name']
        temp_dict['orario_invio'] = orario_invio_comando
        try:
            db[nome_collezione_target].insert_one(temp_dict.copy())
        except Exception as e:
            return jsonify({"status": f"Errore Salvataggio DB: {e}"}), 500
        break
        
    if nome_collezione_target is None:
        return jsonify({"status": "Errore: Dati non validi o ID condizionatore non autorizzato"}), 400
    
    # invio dati  tramite MQTT
    try:
        client = mqtt.Client(transport="tcp") # o rimuovi transport="tcp" a seconda di come l'avevi configurato
        client.connect(broker_address, broker_port, 60)
        client.loop_start()

        topic = f"{topic_base}/{id_dispositivo}"
        
        # Rimuoviamo l'_id generato da mongo se presente prima della conversione
        if '_id' in temp_dict:
            del temp_dict['_id']
            
        payload = json.dumps(temp_dict, default=str)

        info = client.publish(topic, payload)
        info.wait_for_publish()
        
        print(f"MQTT inviato su: {topic} -> {payload}")

        client.loop_stop()
        client.disconnect()

        return jsonify({
            "status": "Successo",
            "messaggio": "Dati salvati su DB e inviati via MQTT",
            "mqtt_topic": topic,
            "db_collection": nome_collezione_target
        }), 200

    except Exception as e:
        print(f"Errore MQTT: {e}")
        return jsonify({"status": "Warning", "messaggio": "Salvato su DB ma errore MQTT", "errore": str(e)}), 500
     
