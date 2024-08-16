import sqlite3 
def create_db():
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    create_table_tokens_sql = '''
        CREATE TABLE IF NOT EXISTS tokens (
            id_token INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL,
            id_representante INTEGER 
        );
    '''
    create_table_notifications_sql = '''
        CREATE TABLE IF NOT EXISTS notifications (
            idnotificacao  INTEGER PRIMARY KEY,
            idrepresentante INTEGER,
            titulo TEXT,
            mensagem TEXT,
            sent INTEGER
        );
    '''
    cursor.execute(create_table_tokens_sql)
    cursor.execute(create_table_notifications_sql)
    conn.commit()
    conn.close()

def grava_notificacao(idnotificacao, idrepresentante, titulo, mensagem):
    create_db()
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM notifications WHERE idnotificacao = ? AND idrepresentante = ? AND titulo = ? AND mensagem = ? AND sent = ?', 
                   (idnotificacao, idrepresentante, titulo, mensagem, 0))
    existing_notificacao = cursor.fetchone()

    if not existing_notificacao:
        armazena_notificacao = '''
        INSERT INTO notifications (idnotificacao, idrepresentante, titulo, mensagem, sent)
        VALUES (?, ?, ?, ?, ?)
        '''
        cursor.execute(armazena_notificacao, (idnotificacao, idrepresentante, titulo, mensagem, 0))
    
    conn.commit()
    conn.close()

def atualiza_notificacao_sent(idnotificacao):
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE notifications SET sent = 1 WHERE idnotificacao = ?', (idnotificacao,))
    conn.commit()
    conn.close()

def retorna_ids_notificacoes_enviadas():
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notifications WHERE sent = 1')
    rows = cursor.fetchall()
    conn.close()
    notificaoes_envivadas = [
        {
            'idnotificacao': row[0]
        }
        for row in rows
    ]
    return notificaoes_envivadas

def retorna_notificacoes_nao_enviadas():
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notifications WHERE sent = 0')
    rows = cursor.fetchall()
    conn.close()

    notificacoes_nao_enviadas = [
        {
            'idnotificacao': row[0],
            'titulo': row[1],
            'mensagem': row[2],
            'idrepresentante': row[3]
        }
        for row in rows
    ]
    return notificacoes_nao_enviadas

def exclui_notificacoes_enviadas():
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notifications WHERE sent = 1')
    conn.commit()
    conn.close()

def grava_token(idrep, token):
    create_db()
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()

    cursor.execute('SELECT token FROM tokens WHERE id_representante = ? AND token = ?', (idrep, token))
    existing_token = cursor.fetchone()
    if existing_token:
        print("Token já existe para o respectivo distribuidor.")
    else:
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

    cursor.execute('''
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name='tokens'
    ''')
    table_exists = cursor.fetchone()

    if table_exists:
        select_tokens = '''
            SELECT token 
            FROM tokens 
            WHERE id_representante = ?
        '''
        cursor.execute(select_tokens, (id_representante,))
        tokens = cursor.fetchall()
        conn.close()

        token_list = [token[0] for token in tokens]
        print(token_list)
        return token_list

    else:
        conn.close()
        return []


def retorna_tudo_banco():
    conn = sqlite3.connect('tokens.db')
    cursor = conn.cursor()
    

    cursor.execute('SELECT * FROM tokens')
    column_names = [description[0] for description in cursor.description]
    

    rows = cursor.fetchall()
    conn.close()
    
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