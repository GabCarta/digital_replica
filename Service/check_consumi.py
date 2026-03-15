from flask import Flask, jsonify, request
import datetime
from database import db_instance 
import json

app = Flask(__name__)

@app.route('/api/check_consumo', methods=["GET"])
def calcola_consumi():
    id_dispositivo = request.args.get('id')
    nome_collezione_yaml = request.args.get('collection')
    
    # Connessione al DB
    db, config = db_instance.get_connection()
    if db is None:
        return jsonify({"Stato": "Errore connessione DB. Verifica che il DB sia inizializzato."}), 500
        
    nome_db = config.get('collections', {}).get(nome_collezione_yaml, {}).get('db_collection_name')
    if not nome_db:
        return jsonify({"Stato": f"Collezione '{nome_collezione_yaml}' non definita nella configurazione."}), 400

    # Query per ricercare i dati all'interno del db(-1 per ordine crescente)
    documento = db[nome_db].find_one(
        {"id": id_dispositivo}, 
        sort=[("_id", -1)] 
    )

    if documento:
        if documento.get('stato') == "OFF":
            documento['_id'] = str(documento['_id']) 
            return jsonify({
                "Stato": "Correct", 
                "Azione": "Il dispositivo è già OFF. Nessun calcolo o aggiornamento necessario.", 
                "dati": documento
            }), 200  
        try:
            # Recupero dei consumi dispositivo e stabilisco una soglia
            potenza_kw = float(documento.get('consumo', 0))
            soglia_kwh = 0.2

            # Conversione/gestione orario invio comando 
            orario_accensione = documento.get('orario_invio')
            if not orario_accensione:
                 return jsonify({"Stato": "Errore", "message": "Orario di invio mancante nel DB"}), 400
            
            if isinstance(orario_accensione, str):
                orario_accensione = datetime.datetime.strptime(orario_accensione, "%a, %d %b %Y %H:%M:%S GMT")
            
            if orario_accensione.tzinfo is not None:
                orario_accensione = orario_accensione.replace(tzinfo=None)

            # Calcolo tempo passato dall'invio del comando espresso in secondi
            orario_attuale = datetime.datetime.now()
            tempo_trascorso = orario_attuale - orario_accensione
            minuti_trascorsi = tempo_trascorso.total_seconds() / 60.0
            
            # Per evitare valori negativi
            if minuti_trascorsi < 0:
                minuti_trascorsi = 0

            #Calcolo consumo totale (kWh)
            consumo_totale_kwh = potenza_kw * (minuti_trascorsi / 60.0)

            #Check soglia
            if consumo_totale_kwh > soglia_kwh:
                
                # Se il consumo è > della soglia viene spento il dispositivo
                risultato_aggiornamento = db[nome_db].update_one(
                    {"_id": documento['_id']}, 
                    {"$set": {
                        "stato": "OFF",
                        "consumo_totale_kwh": consumo_totale_kwh, 
                        "data_spegnimento": datetime.datetime.now()
                    }}
                )
                # Verifica salvataggio nel db
                if risultato_aggiornamento.modified_count > 0:
                    documento['stato'] = "OFF"
                    azione = f"Soglia superata! Consumati {consumo_totale_kwh:.4f} kWh in {minuti_trascorsi:.2f} min. Dispositivo SPENTO e salvato in DB."
                else:
                    azione = "Soglia superata, ma impossibile aggiornare lo stato nel DB (nessuna modifica effettuata)."
            else:
                azione = f"Consumo ok: {consumo_totale_kwh:.4f} kWh in {minuti_trascorsi:.2f} min. Dispositivo rimane ON."

            #  dati per la risposta JSON approssimati alle 2 cifra dopo la virgola
            documento['_id'] = str(documento['_id'])
            documento['minuti_trascorsi_calcolati'] = round(minuti_trascorsi, 2)
            documento['consumo_totale_kwh'] = round(consumo_totale_kwh, 2)
            
            return jsonify({
                "Stato": "Correct", 
                "Azione": azione, 
                "dati": documento
            }), 200

        # gestione eccezioni
        except ValueError as er:
            return jsonify({"Stato": "Errore ValueError", "message": str(er)}), 400
        except Exception as e:
            return jsonify({"Stato": "Errore generico", "message": str(e)}), 500
            
    else:
        return jsonify({"Stato": "Not Found", "message": "Nessun dispositivo in stato ON trovato"}), 404