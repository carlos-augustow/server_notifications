import sqlite3
import requests
import urllib3
import time
import firebase_admin
import schedule
import threading

from flask_cors import CORS

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*"}})

def create_db():
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    create_table_tokens_sql = '''
        CREATE TABLE IF NOT EXISTS tokens (
            id_token INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL,
            id_representante INTEGER,
            FOREIGN KEY (id_representante) REFERENCES representatives(id_representante)
        );
    '''
    create_table_representatives_sql = '''
        CREATE TABLE IF NOT EXISTS representatives (
            id_rep_index INTEGER PRIMARY KEY AUTOINCREMENT,
            id_representante INTEGER 
        );
    '''
    cursor.execute(create_table_tokens_sql)
    cursor.execute(create_table_representatives_sql)
    conn.commit()
    conn.close()

def grava_token(idrep, token):
    create_db()
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()

    # Inserindo o representante se ainda não existir
    cursor.execute('INSERT OR IGNORE INTO representatives DEFAULT VALUES')

    # Obtendo o id_representante do representante inserido ou existente
    cursor.execute('SELECT id_representante FROM representatives ORDER BY id_representante DESC LIMIT 1')
    id_representante = cursor.fetchone()[0]

    # Verificando se o token já existe para o respectivo distribuidor
    cursor.execute('SELECT token FROM tokens WHERE id_representante = ? AND token = ?', (idrep, token))
    existing_token = cursor.fetchone()
    if existing_token:
        print("Token já existe para o respectivo distribuidor.")
    else:
        # Armazenando o token junto com o id_representante na tabela tokens
        armazena_token = '''
        INSERT INTO tokens (token, id_representante)
        VALUES (?, ?)
        '''
        cursor.execute(armazena_token, (token, idrep))

    conn.commit()
    conn.close()


def get_tokens(id_representante):
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()

    select_tokens = '''
        SELECT token 
        FROM tokens 
        WHERE id_representante = ?
    '''
    cursor.execute(select_tokens, (id_representante))
    tokens = cursor.fetchall()
    conn.close()

    return tokens

def retorna_tudo_banco():
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    
    # Fetch column names
    cursor.execute('SELECT * FROM tokens')
    column_names = [description[0] for description in cursor.description]
    
    # Fetch all rows
    rows = cursor.fetchall()
    conn.close()
    
    # Convert rows to list of dictionaries
    result = [dict(zip(column_names, row)) for row in rows]
    
    return result

def delete_token(id_representante):
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    delete_token_sql = '''
    DELETE FROM
    tokens WHERE id_representante = ?
    '''
    cursor.execute(delete_token_sql, (id_representante,))
    conn.commit()
    conn.close()


def delete_db_query():
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    delete_table_sql = '''
        DROP TABLE IF EXISTS tokens;
    '''
    cursor.execute(delete_table_sql)
    conn.commit()
    conn.close()


@app.route('/.well-known/<path:path>', methods=['GET'])
def send_json(path):
    return send_from_directory('.well-known', path)


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
    # data = request.json

    id_repr = id_rep
    token_fcm = token
  

    if token_fcm and id_repr:
        print("Token recebido: ", token_fcm)
        grava_token(id_repr, token)
        return jsonify({"sucess": True}), 200
    else:
        return jsonify({'sucess': False}), 200
    #     return jsonify({'sucess': True}), 200
    # return jsonify({'sucess': False}), 200


@app.route('/write_message/<message>', methods=['GET'])
def write_message(message):
    return jsonify({'message': message})

@app.route('/send_message/<token>/<title>/<message>', methods=['GET'])
def send_message(token, title, message):
    if message and token and title:
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


def enviar_notificacao(token, idmsg, title, mensage):
    resultado = enviar_token(token, idmsg, str(title), str(mensage), None, None)
    print(resultado)

    if resultado["STATUS_CODE"] != 200:
        print("Opa, falhou no envio. Não vou continuar.")
        print(resultado["STATUS_CODE"])

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



def chama_msg_noti():
        try:
            response = requests.get("https://desenvolvimento.sistema.romancemoda.com.br/desenv/romance/vol/notipush")
            response.raise_for_status()  # Levanta um erro se a requisição falhar
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")


def exibe_msg_noti():
    msgs_da_noti = chama_msg_noti()
    
    if 'items' in msgs_da_noti:
        notifs = msgs_da_noti['items']
        print(notifs)

        for notif in notifs:
            print(notif)
            id_representante = notif['idrepresentante']
            tokens = get_tokens(id_representante)
            if tokens:
                for token in tokens:
                    print(token)
                    enviar_notificacao(token["token"], notif["idnotificacao"], notif['titulo'], notif['mensagem'])
                    time.sleep(0.2)


 
    else:
        print("Resposta inesperada:", msgs_da_noti)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(10).seconds.do(exibe_msg_noti)

if __name__ == "__main__":
    # Start the schedule in a separate thread
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()

    # Start the Flask app
    app.run(debug=True, host="0.0.0.0", port=5000)
