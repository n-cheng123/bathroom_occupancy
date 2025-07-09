import mysql.connector

db_config = {
<<<<<<< HEAD
    'host': 'gator4236.hostgator.com',
    'user': 'sevenlog_gojji',
    'password': 'Test1234',
    'database': 'sevenlog_gojjidw',
    'port': 3306,
    'autocommit': True
}

def get_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("DEBUG: Successfully connected to HostGator database.")
            return connection
        else:
            print("ERROR: Connection to HostGator database failed (is_connected() returned False).")
            raise ConnectionError("Failed to connect to the database.")
    except mysql.connector.Error as err:
        print(f"ERROR: MySQL Connection Error: {err}")
        raise ConnectionError(f"Database connection error: {err}")
    except Exception as e:
        print(f"ERROR: Unexpected error in get_connection: {e}")
        raise ConnectionError(f"Unexpected database connection error: {e}")

=======
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
>>>>>>> f034381b7a5ba8648b9dcf6263dc8286e458ad50
