import time
import urllib3
import requests
import firebase_admin
from flask import Flask, request, jsonify

app = Flask(__name__)

tokens = {}
representatives = {}


@app.route('/register_token', methods=['POST'])
def register_token():
    data = request.json
    print("Data_recives: ", data)
    if 'token' in data and 'representative_id' in data:
        token = data['token']
        representative_id = data['representative_id']
        tokens[token] = representative_id
        representatives[representative_id] = token
        print("tokens", tokens)
        print("representatives", representatives)
        return jsonify({'message': 'Token registered successfully'}), 200
    else:
        return jsonify({'error': 'Missing token or representative_id in request'}), 400


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    if 'message' in data and 'token' in data and 'title' in data:
        print("Data_recives: ", data)
        token = data['token']
        title = data['title']
        message = data['message']
        enviar_notificacao(token, title, message)
        # print(retorno)
        return jsonify({'message': 'Informations body were recived successfully'}), 200
    else:
        return jsonify({'error': 'Missing informations body request'}), 400


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


def enviar_notificacao(token, title, mensage):
    resultado = enviar_token(token, 39493, str(title), str(mensage), None, None)
    print(resultado)

    if resultado["STATUS_CODE"] != 200:
        print("Opa, falhou no envio. Não vou continuar.")

    time.sleep(2)


def enviar_token(TOKEN, IDMSG, TITLE, MESSAGE, IMGSRC, URL):
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

    if IMGSRC is not None:
        params["message"]["data"]["imgsrc"] = IMGSRC
        params["notification"]["data"]["image"] = IMGSRC

    if URL is not None:
        params["message"]["data"]["url"] = URL

    return enviar_msg(params)


if __name__ == "__main__":
    app.run(debug=True)

# print("a")