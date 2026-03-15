"""
contiene la generazione della chiave fornita dal server in fase di registrazione
e il controllo della chiave nelle richieste successive. 
"""

from cryptography.fernet import Fernet
from flask import Flask, request, jsonify
import os
import json
app = Flask(__name__)

@app.route('/api/generate_keys', methods=['GET'])
# funzione per generare una chiave di sicurezza
def create_key():
    secret_key = Fernet.generate_key()
    return secret_key.decode('utf-8')

# funzione per andare a verificare la chiave di sicurezza
def check_key(sender_id, received_key):
    # percorso del file json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'profile', 'device.json')

    try:
        # apertura file modalità lettura
        with open(file_path, 'r') as f:
            data = json.load(f)
        
         # Estraggo l'ID e la chiave salvati nel file
        saved_id = data.get("id")
        saved_key = data.get("security", {}).get("security_key")

        # Confronto sulla chiave e id
        if saved_id == sender_id and saved_key == received_key:
            return True 
        else:
            return False 
            
    except FileNotFoundError:
        print("Errore: Il file device.json non esiste ancora.")
        return False
    except Exception as e:
        print(f"Errore durante la lettura del file: {e}")
        return False