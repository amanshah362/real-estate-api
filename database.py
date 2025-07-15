import mysql.connector
from mysql.connector import Error

# Connection config
def connect_db():
    return mysql.connector.connect(
    host= "mysql-199520-0.cloudclusters.net",
    port= 10075,
    user= "user001",
    password= "user001@",
    database= "qr_secure_db"
    )

def create_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    conn.close()
    return True

def verify_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_client_by_qr(client_id, pin):
    conn = mysql.connector.connect(
        host= "mysql-199520-0.cloudclusters.net",
        port= 10075,
        user= "user001",
        password= "user001@",
        database= "qr_secure_db"
    )
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM clients WHERE id=%s AND pin=%s"
    cursor.execute(query, (client_id, pin))
    client = cursor.fetchone()
    conn.close()
    return client