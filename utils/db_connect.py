import psycopg2
from typing import Dict, Any

def connect_to_postgres(db_config: Dict[str, Any] = {"dbname": "rnd", "user": "readusr", "password": "LiaII|r~01-0", "host": "aidf-dev-postgres.postgres.database.azure.com"}) -> psycopg2.extensions.connection:
    try:
        connection = psycopg2.connect(**db_config)
        print("Connection to database successful")
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
