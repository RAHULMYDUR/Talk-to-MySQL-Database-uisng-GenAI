import mysql.connector

def connect_to_mysql(host, port, username, password):
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            password=password
        )
        return conn
    except mysql.connector.Error as e:
        return None
