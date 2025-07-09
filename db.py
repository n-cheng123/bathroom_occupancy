import mysql.connector

db_config = {
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

