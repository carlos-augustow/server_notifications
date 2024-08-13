import requests
import urllib3
import time
import firebase_admin
import schedule
import threading
from database_functions import grava_token, get_tokens, retorna_tudo_banco, delete_token, delete_db_query

from flask_cors import CORS

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*"}})

lock = False

idsEnviados = []

@app.route('/delete_db', methods=['GET'])
def delete_db():
    delete_db_query()
    return jsonify({"message": "Banco de dados tokens excluído com sucesso!"}), 200


@app.route('/delete_token', methods=['POST'])
def delete():
    data = request.json
    if 'idrep' in data:
        id = data['idrep']
        delete_token(id)
        return jsonify({'message': 'Deletado com sucesso!'}, 200)
    else:
        return jsonify({'message': 'Erro ao deletar'}, 400)


@app.route('/return_all', methods=['GET'])
def return_all():
    data = retorna_tudo_banco()
    return jsonify(data)


@app.route('/register_token/<id_rep>/<token>', methods=['GET'])
def register_token(id_rep, token):
    id_repr = id_rep
    token_fcm = token
    if token_fcm and id_repr:
        print("Token recebido: ", token_fcm)
        grava_token(id_repr, token)
        return jsonify({"sucess": True}), 200
    else:
        return jsonify({'sucess': False}), 200

def get_access_token():
    cred = firebase_admin.credentials.Certificate("second-14d46-firebase-adminsdk-egrsc-e857f12342.json")
    t = cred.get_access_token()
    return t.access_token
               

def enviar_msg(params):
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + get_access_token()}

    print(headers)
    print(params)

    urllib3.disable_warnings()

    r = requests.post("https://fcm.googleapis.com/v1/projects/second-14d46/messages:send",
                      json=params,
                      headers=headers,
                      verify=False)
    return {"STATUS_CODE": r.status_code, "TEXT": r.text}


def enviar_notificacao(token, idmsg, title, mensage):
    resultado = enviar_token(token, idmsg, str(title), str(mensage), None, None)
    print(resultado)
    if resultado["STATUS_CODE"] == 200:
        return {"sucesso": True}
    else:
        return {"sucesso": False, "msg": resultado.text }

import requests

def setando_enviado(enviados):
    try:
        print("entrou")
        print("enviados: ", enviados)
        headers = {"Content-Type": "application/json"}
        response = requests.post("https://desenvolvimento.sistema.romancemoda.com.br/desenv/romance/vol/notipushenv", json=enviados, headers=headers)
        
        if response.status_code == 200:
            return {"sucesso": True}
        else:
            print(f"Falha na requisição: {response.status_code} - {response.text}")
            return {"sucesso": False}
    
    except Exception as e:
        print(f"Erro ao enviar a requisição: {e}")
        return {"sucesso": False}





def enviar_token(TOKEN, IDMSG, TITLE, MESSAGE, IMGSRC, URL):
    print("TOKEN: ",  (TOKEN))

    params = {"message": {
                    "data": {
                        "title": TITLE,
                        "body": MESSAGE,
                        "idmsg": str(IDMSG),
                    },
                    "notification": {
                        "title": TITLE,
                        "body": MESSAGE,
                    },
                    "token": TOKEN,
                    }
                }
    if IMGSRC:
        params["message"]["data"]["imgsrc"] = IMGSRC
        params["notification"]["data"]["image"] = IMGSRC

    if URL:
        params["message"]["data"]["url"] = URL

    print("payload: ", params)
  
    return enviar_msg(params)


def chama_msg_noti():
        try:
            response = requests.get("https://desenvolvimento.sistema.romancemoda.com.br/desenv/romance/vol/notipush")
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")


# def main_func():

#     for x in range(3):  
#         if not len(idsEnviados) == 0:  
#             print("ids: ", idsEnviados)
#             # retorno = setando_enviado(idsEnviados)
#             # if retorno == True: 
#             #     idsEnviados = []
#             #     break 

#     msgs_da_noti = chama_msg_noti()

#     if 'items' in msgs_da_noti:
#         notifs = msgs_da_noti['items']
#         print("######################")
#         print(notifs)
#         print("######################")

#         for notif in notifs:
#             id_representante = notif['idrepresentante']
#             if id_representante:
#                 tokens = get_tokens(id_representante)
#                 print(f"{tokens.values()}")
#                 if not "vazio" in tokens:
#                 #    for token in tokens:
#                     for token in tokens.values():  # Agora token é uma string (o token em si)
#                         envio = enviar_notificacao(token, notif["idnotificacao"], notif["titulo"], notif["mensagem"])
#                         if envio['sucesso']:
#                             idsEnviados.append(notif["idnotificacao"])
#                             return "sucess"
#                         else:
#                             return envio
#             else:
#                 print("Resposta inesperada:", msgs_da_noti)


def main_xfunc():
    try:
        global lock
        if lock: 
            return
        lock = True
        for x in range(3):  
            if idsEnviados:  # Verifica se idsEnviados não está vazio
                print("ids: ", idsEnviados)
                # retorno = setando_enviado(idsEnviados)
                # if retorno == True: 
                #     idsEnviados = []
                #     break 
                time.sleep(.2)

        msgs_da_noti = chama_msg_noti()

        if 'items' in msgs_da_noti:
            notifs = msgs_da_noti['items']
            print("######################")
            print(notifs)
            print("######################")

            for notif in notifs:
                id_representante = notif['idrepresentante']
                if id_representante:
                    tokens = get_tokens(id_representante)
                    print(f"tokens db: {tokens.values()}")
                    if "vazio" not in tokens:
                        for token in tokens.values():  # Agora token é uma string (o token em si)
                            envio = enviar_notificacao(token, notif["idnotificacao"], notif["titulo"], notif["mensagem"])
                            if envio['sucesso']:
                                idsEnviados.append({"idnotificacao": notif["idnotificacao"]})
                                # Não retorna ainda, continue o loop para processar todas as notificações
                            else:
                                return envio  # Retorna apenas se houver falha
                else:
                    print("Resposta inesperada:", msgs_da_noti)
        lock = False
        return "Executado"
    except:
        lock = False

 
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(10).seconds.do(main_xfunc)

if __name__ == "__main__":
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()
    app.run(debug=True, host="0.0.0.0", port=5000)
