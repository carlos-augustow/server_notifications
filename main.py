import time
import urllib3
import requests
import firebase_admin
import sqlite3

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

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
    cursor.execute(select_tokens, (id_representante,))
    tokens = cursor.fetchall()
    conn.close()

    return tokens


def retorna_tudo_banco():
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    select_tokens = '''
     SELECT *
     FROM tokens;
     '''
    cursor.execute(select_tokens)
    rows = cursor.fetchall()
    conn.close()
    return rows


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


@app.route('/register_token', methods=['POST'])
def register_token():
    data = request.json
    print("Data_recives: ", data)
    if 'token' in data and 'idrep' in data:
        token = data['token']
        id_representante = data['idrep']
        grava_token(id_representante, token)
        return jsonify({'message': 'Token registered successfully'}), 200
    else:
        return jsonify({'error': 'Missing token or representative_id in request'}), 400


@app.route('/write_message/<message>', methods=['GET'])
def write_message(message):
    return jsonify({'message': message})

@app.route('/send_message/<token>/<title>/<message>', methods=['GET'])
def send_message(token, title, message):
    if message and token and title:
        enviar_notificacao(token, title, message)
        # print(retorno)
        return jsonify({'message': 'Informations body were recived successfully'), 200
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
