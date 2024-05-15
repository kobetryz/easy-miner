import psycopg2
from utils import get_value_from_env

def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname=get_value_from_env("DB_NAME"),
            user=get_value_from_env("DB_USER"),
            password=get_value_from_env("DB_PASSWORD"),
            host=get_value_from_env("DB_HOST"),
            port=get_value_from_env("DB_PORT"),  
        )
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        return None
