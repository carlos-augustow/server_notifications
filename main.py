from flask import Flask, request, jsonify
import cx_Oracle
import sys

app = Flask(__name__)

tokens = {}
representatives = {}
host = "dbcrisdu.crisdulabs.com.br"
port = "1521"
service_name = "desenv.snprodcrisdupri.vcnprdcrisdu.oraclevcn.com"


def conecting_to_db():
    try:

        dsn = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST={host})(PORT={port}))(CONNECT_DATA=(SERVICE_NAME={service_name})(SERVER=dedicated)))"

        return cx_Oracle.connect("roman", "desenv", dsn)
    except cx_Oracle.DatabaseError as e:
        print("Error connecting to dbcrisdu.crisdulabs.com" + str(e))


cnxn = conecting_to_db()


def busca_tokens_rep(representative_id):
    cnxn.prepare("select TOKEN from ROMAN.TOKENNOTIFICACOESVENDAS where IDREPRESENTANTE = :id_representative")
    cnxn.execute(None, {'TOKEN': representative_id})
    return cnxn.fetchall()


@app.route('/register_token', methods=['POST'])
def register_token():
    data = request.json
    print("Data_recives: ", data)
    if 'token' in data and 'representative_id' in data:
        token = data['token']
        representative_id = data['representative_id']
        busca = busca_tokens_rep(representative_id)
        print("busca:", busca)
        tokens[token] = representative_id
        representatives[representative_id] = token
        print("tokens", tokens)
        print("representatives", representatives)
        return jsonify({'message': 'Token registered successfully'}), 200
    else:
        return jsonify({'error': 'Missing token or representative_id in request'}), 400


@app.route('/send_notification', methods=['POST'])
def send_notification():
    data = request.json
    if 'token' in data and 'message' in data:
        token = data['token']
        message = data['message']
        if token in tokens:
            representative_id = tokens[token]
            # Aqui você pode implementar o envio da notificação para o representante específico
            return jsonify({'message': f'Notification sent to representative {representative_id}'}), 200
        else:
            return jsonify({'error': 'Invalid token'}), 400
    else:
        return jsonify({'error': 'Missing token or message in request'}), 400


if __name__ == '__main__':
    app.run(debug=True)
