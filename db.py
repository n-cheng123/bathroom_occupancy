import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Summer2020$',
    'database': 'bathroom_extra'
}

def get_connection():
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        return connection
    else:
        raise ConnectionError("Failed to connect to the database.")