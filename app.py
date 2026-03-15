"""
contiene l'avvio del server e l'aggancio di tutte le chiamate disponibili.
Qui vengono rese attive le API e vengono collegati i moduli che gestiscono
registrazione, gestione dati e invio comandi.
"""
from flask import Flask
from resources.registration import registration_pf
from resources.data_http import send_data
from resources.data_mqtt import set_data
from resources.data_http import get_data
import security
from services.profile_service import maintenance_profile 
from Service.check_consumi import calcola_consumi


app = Flask(__name__)
app.add_url_rule('/api/registration', view_func=registration_pf, methods=['POST'])
app.add_url_rule('/api/sendData', view_func=send_data, methods=['POST'])
app.add_url_rule('/api/setData', view_func=set_data, methods=['POST'])
app.add_url_rule('/api/getData', view_func=get_data, methods=['GET'])
app.add_url_rule('/api/generate_keys', view_func=security.create_key, methods=['GET'])
app.add_url_rule('/api/service_pf', view_func=maintenance_profile, methods=['GET','POST'])
app.add_url_rule('/api/check_consumo', view_func=calcola_consumi,methods=['GET'])
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
   