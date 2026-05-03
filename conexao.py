import sqlite3 as sql

def get_conn():
    conn = sql.connect('senhas.db')
    conn.row_factory = sql.Row
    return conn

# Inicializa o banco de dados
conn = get_conn()
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS senhas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    valor       TEXT    NOT NULL,
    tipo        TEXT    NOT NULL DEFAULT 'normal',
    status      TEXT    NOT NULL DEFAULT 'aguardando',
    guiche      INTEGER,
    criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chamado_em  TIMESTAMP
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS funcionarios (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome    TEXT    NOT NULL,
    email   TEXT    NOT NULL UNIQUE,
    senha   TEXT    NOT NULL
)''')

conn.commit()
cursor.close()
conn.close()
