
import logging

from flask_cors import CORS
from flask import Flask, request, jsonify
from database_functions import grava_token, retorna_tudo_banco, delete_token, delete_db_query

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*"}})

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/delete_db', methods=['GET'])
def delete_db():
    delete_db_query()
    return jsonify({"message": "Banco de dados tokens excluído com sucesso!"}), 200


@app.route('/delete_token/<idrep>', methods=['GET'])
def delete(idrep):
    if idrep:
        delete_token(idrep)
        return jsonify({'message': 'Deletado com sucesso!'}), 200
    else:
        return jsonify({'message': 'Erro ao deletar'}), 400

@app.route('/return_all', methods=['GET'])
def return_all():
    data = retorna_tudo_banco()
    if data is None:
        data = []
    return jsonify(data)

@app.route('/register_token/<id_rep>/<token>', methods=['GET'])
def register_token(id_rep, token):
    id_repr = id_rep
    token_fcm = token
    if token_fcm and id_repr:
        logging.info(f"Token recebido: {token_fcm}")
        grava_token(id_repr, token)
        return jsonify({"sucess": True}), 200
    else:
        return jsonify({'sucess': False}), 200
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4000)
