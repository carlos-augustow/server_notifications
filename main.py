import requests
import urllib3
import time
import firebase_admin
import schedule
import logging
from flask_cors import CORS
from flask import Flask
from database_functions import get_tokens, retorna_ids_notificacoes_enviadas, grava_notificacao, retorna_notificacoes_nao_enviadas, atualiza_notificacao_sent

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*"}})

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_access_token():
    cred = firebase_admin.credentials.Certificate("second-14d46-firebase-adminsdk-egrsc-e857f12342.json")
    t = cred.get_access_token()
    return t.access_token

def enviar_msg(params, idmsg):

    idsEnviados = retorna_ids_notificacoes_enviadas()

    logging.info(f"ID da mensagem: {idmsg}, IDs enviados: {idsEnviados}")

    if idmsg not in idsEnviados:
        logging.info("Enviando mensagem")

        headers = {"Content-Type": "application/json",
                "Authorization": "Bearer " + get_access_token()}

        urllib3.disable_warnings()

        r = requests.post("https://fcm.googleapis.com/v1/projects/second-14d46/messages:send",
                        json=params,

                        headers=headers,
                        verify=False)
        if r.status_code == 200:
            idsEnviados.append({"idnotificacao": idmsg})
        
        return {"STATUS_CODE": r.status_code, "TEXT": r.text}
    else:
        return {"STATUS_CODE": 400, "TEXT": "ID já enviado"}

def enviar_notificacao(token, idmsg, title, mensage):
    resultado = enviar_token(token, idmsg, str(title), str(mensage), None, None)
    logging.info(f"Resultado do envio: {resultado}")
    if resultado["STATUS_CODE"] == 200:
        atualiza_notificacao_sent(idmsg)
        return {"sucesso": True}
    else:
        return {"sucesso": False, "msg": resultado["TEXT"] }

def setando_enviado(idsEnviados):

    if idsEnviados is None:
        idsEnviados = []

    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post("https://desenvolvimento.sistema.romancemoda.com.br/desenv/romance/vol/notipushenv", json=list(idsEnviados), headers=headers)
        
        if response.status_code == 200:
            return {"sucesso": True}
        else:
            logging.error(f"Falha na requisição: {response.status_code} - {response.text}")
            return {"sucesso": False}
    
    except Exception as e:
        logging.error(f"Erro ao enviar a requisição: {e}")
        return {"sucesso": False}

def enviar_token(TOKEN, IDMSG, TITLE, MESSAGE, IMGSRC, URL):
    logging.info(f"TOKEN: {TOKEN}")

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
  
    return enviar_msg(params, IDMSG)

def chama_msg_noti():
    try:
        response = requests.get("https://desenvolvimento.sistema.romancemoda.com.br/desenv/romance/vol/notipush")
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Erro ao obter mensagens: {response.status_code} - {response.text}")
            return None
    except Exception as err:
        logging.error(f"Erro ao obter mensagens: {err}")
        return None

def envia_id_noti():

    idsEnviados = retorna_ids_notificacoes_enviadas()
    
    if idsEnviados is None:
        idsEnviados = []

    for _ in range(3):
        if idsEnviados:
            logging.info(f"IDs a enviar: {idsEnviados}")
            retorno = setando_enviado(idsEnviados)
            time.sleep(0.2)
            if retorno.get('sucesso'): 
                logging.info(f"IDs enviados com sucesso: {idsEnviados}")
                idsEnviados = []
                break




def main_xfunc():

        try:
            envia_id_noti()

            msgs_da_noti = chama_msg_noti()

            if msgs_da_noti and 'items' in msgs_da_noti:
                notifs = msgs_da_noti['items']
                logging.info(f"Notificações recebidas: {notifs}")

                for notif in notifs:
                    grava_notificacao(notif["idnotificacao"], notif['idrepresentante'], notif["titulo"], notif["mensagem"])
    
            notifs_banco = retorna_notificacoes_nao_enviadas()
            logging.info(f"Notificações banco: {notifs_banco}")

            if notifs_banco:
                for notif in notifs:
                    id_representante = notif.get('idrepresentante')
                    if id_representante:
                        tokens = get_tokens(id_representante)
                        if tokens:
                            for token in tokens:
                                envio = enviar_notificacao(token, notif["idnotificacao"], notif["titulo"], notif["mensagem"])
                                if envio['sucesso']:
                                    logging.info(f"Notificação {notif['idnotificacao']} enviada com sucesso.")
                                else:
                                    return envio
                        else:
                            logging.warning(f"Nenhum token encontrado para o representante: {id_representante}")
                    else:
                        logging.warning(f"Notificação sem idrepresentante: {notif}")


            return "Executado"
        except Exception as e:
            logging.error(f"Erro na execução: {str(e)}")


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(10).seconds.do(main_xfunc)

if __name__ == "__main__":
    run_schedule()

    app.run(debug=True, host="0.0.0.0", port=4002)