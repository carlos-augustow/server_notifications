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


@app.route("/endpoint_oracle/<idmsg>/<title>/<msg>/<idrep>", methods=['GET'])
def function_endpoint_oracle(idmsg, title, msg, idrep):
    if idmsg and title and msg and idrep:
        tokens = get_tokens(idrep)
        for token in tokens:
            if token['idrepresentante'] == idrep:   
               envio = enviar_notificacao(token['token'], idmsg, title, msg)
               if (envio['sucesso'] == True):
                  return setando_noti_como_s(idrep, idmsg)
               else:
                   return envio
               

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
        return jsonify({"sucesso": True})
    else:
        return jsonify({"sucesso": False, "msg": resultado.text })

def setando_noti_como_s(idrep, idmsg):
     set_like_s = requests.put(f"https://desenvolvimento.sistema.romancemoda.com.br/desenv/romance/vol/notipushenv?idrep={idrep}&idnoti={idmsg}")
     if set_like_s.status_code == 200:
            return jsonify({"sucesso": True})
     else:
            return jsonify({"sucesso": False, "msg": set_like_s.text})




def enviar_token(TOKEN, IDMSG, TITLE, MESSAGE, IMGSRC, URL):
    print("TOKEN: ", str(TOKEN).split("'")[1])

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
                    "token": str(TOKEN).split("'")[1],
                    }
                }
    if IMGSRC is not None:
        params["message"]["data"]["imgsrc"] = IMGSRC
        params["notification"]["data"]["image"] = IMGSRC

    if URL is not None:
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


def exibe_msg_noti():
    msgs_da_noti = chama_msg_noti()
    # print(retorna_tudo_banco())

    if 'items' in msgs_da_noti:
        notifs = msgs_da_noti['items']
        print("######################")
        print(notifs)
        print("######################")

        for notif in notifs:
            id_representante = notif['idrepresentante']
            if id_representante:
                tokens = get_tokens(id_representante)
                print(f"{tokens}")
                if not "vazio" in tokens:
                #    for token in tokens:
                    for i, token in tokens.items():
                        if token['idrepresentante'] == id_representante:   
                            envio = enviar_notificacao(token['token'], notif["idnotificacao"], notif["titulo"], notif["mensagem"])
                            if (envio['sucesso'] == True):
                                # return setando_noti_como_s(id_representante, notif["idnotificacao"])
                                return "sucess"
                            else:
                               return envio
            else:
                print("Resposta inesperada:", msgs_da_noti)

 
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(10).seconds.do(exibe_msg_noti)

if __name__ == "__main__":
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()
    app.run(debug=True, host="0.0.0.0", port=5000)
