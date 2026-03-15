# Digital Replica
Questo progetto si basa sulla costruzione della struttura di una digital replica, ossia la copia virtuale di un oggetto fisico, andando a simulare ed implementare il suo funzionamento nel mondo virtuale. Per l'implementazione di questo progetto è stato utilizzato Flask, che è un micro-framework web leggero e flessibile, utilizzato per creare rapidamente applicazioni web e route API. Mentre per il salvataggio dei dati è stato utilizzato MongoDB

# Struttura del Progetto
digital_replica/
<br>├── app.py
<br>├── database.py
<br>├── security.py
<br>├── requirements.txt
<br>├── Dockerfile
<br>├──Service/
<br>│ ├── check_consumi.py
<br>├── resources/
<br>│ ├── __init__.py
<br>│ ├── registration.py
<br>│ ├── data_http.py
<br>│ └── data_mqtt.py
<br>├── services/
<br>│ ├── __init__.py
<br>│ ├── profile_service.py
<br>│ ├── data_service.py
<br>│ └── mqtt_service.py
<br>└── profiles/
<br>├── device.yaml
<br>└── device.json

# Funzionamento del Sistema
app.py contiene l’avvio del server e l’aggancio di tutte le chiamate disponibili. Qui vengono rese attive le API e vengono collegati i moduli che gestiscono registrazione, gestione dati e invio comandi.
 
database.py contiene la gestione della connessione al database. Fornisce funzioni per aprire la connessione usando l’indirizzo salvato nel profilo e per leggere/scrivere dati.
 
security.py contiene la generazione della chiave fornita dal server in fase di registrazione e il controllo della chiave nelle richieste successive.
 
requirements.txt contiene l’elenco dei pacchetti necessari per eseguire il progetto.
 
Dockerfile contiene le istruzioni per costruire l’immagine Docker del server: copia dei file del progetto, installazione delle dipendenze e comando di avvio del server.
 
resources/registration.py contiene la chiamata HTTP di registrazione. Riceve dal dispositivo il profilo della digital replica, inclusi indirizzo broker MQTT e indirizzo database. Restituisce l’esito della registrazione e la chiave generata dal server che dovrà essere usata nelle chiamate successive.
 
resources/data_http.py contiene le chiamate HTTP dedicate ai dati. Contiene le chiamate tipo sendData e getData e usa il file profiles/device.yaml per determinare regole di validazione e gestione dei dati.
 
resources/data_mqtt.py contiene la chiamata HTTP dedicata ai comandi verso MQTT. Contiene la chiamata tipo setData e usa le informazioni MQTT salvate in profiles/device.yaml.
 
services/registration_service.py contiene la logica della registrazione. Salva le informazioni del dispositivo, genera la chiave lato server, la salva lato server e avvia la creazione o aggiornamento del file profiles/device.yaml.
 
services/profile_service.py contiene la creazione e l’aggiornamento del file profiles/device.yaml a partire dal profilo ricevuto in registrazione, e la lettura del profilo quando arrivano richieste successive.
 
services/data_service.py contiene la gestione dei dati. Esegue la validazione basandosi su profiles/device.yaml e salva/recupera i dati dal database indicato nel profilo.

 
services/mqtt_service.py contiene la gestione dei messaggi MQTT. Usa broker e impostazioni salvate in profiles/device.yaml per pubblicare messaggi e, se necessario, leggere messaggi.

Service/check_consumi.py Servizio utilizzato per andare a calcolare i consumi dei device accessi. Suoperata una certa soglia, il dispositivo viene spento e il comando viene aggiornato andando a scrivere sul database

# Test
Per andare a testare questo progetto viene utilizzato POSTMAN, con il quale andiamo ad effettuare le varie app.route presenti nel progetto. Oltre alla struttura del codice è presente anche un file .json dove sono presenti tutte le chiamate effettuate con POSTMAN, con degli esempi dei dati che vanno necessariamente passati alle varie chiamate per poter funzionare correttamente.

 
profiles/device.yaml contiene l’unico profilo della digital replica, generato o aggiornato in registrazione. Include indirizzi DB e MQTT e le regole/struttura necessarie per validare e gestire le chiamate dati.
 
profiles/device.json contiene le informazioni minime persistenti legate al dispositivo e la chiave salvata lato server, usate per riconoscere e autorizzare le richieste.
