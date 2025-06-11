import mysql.connector

db_config = {
    'host': 'database-1.c70ocqomyiwx.us-east-2.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Summer2020$',
    'database': 'AWS_Bathroom_Occupancy',
    'port': 3306
}

def get_connection():
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        return connection
    else:
        raise ConnectionError("Failed to connect to the database.")
