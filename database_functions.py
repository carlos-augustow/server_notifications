import sqlite3


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


    cursor.execute('INSERT OR IGNORE INTO representatives DEFAULT VALUES')


    cursor.execute('SELECT id_representante FROM representatives ORDER BY id_representante DESC LIMIT 1')
    id_representante = cursor.fetchone()[0]


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

    select_tokens = '''
        SELECT token 
        FROM tokens 
        WHERE id_representante = ?
    '''
    cursor.execute(select_tokens, (id_representante,))
    tokens = cursor.fetchall()
    conn.close()

    return dict(tokens)

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