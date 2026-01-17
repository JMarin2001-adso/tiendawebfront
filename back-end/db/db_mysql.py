import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_HOST = os.environ["MYSQL_HOST"]
MYSQL_PORT = os.environ["MYSQL_PORT"]


class ConnectDB:
    def __init__(self):
        # No mantenemos conexión persistente
        pass

    def get_connection(self):
        try:
            connection = pymysql.connect(
                host=MYSQL_HOST,
                port=int(MYSQL_PORT),
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database="tiendaweb",
                cursorclass=pymysql.cursors.DictCursor  # Para que siempre devuelva diccionarios
            )
            print("Conexion exitosa a MYSQL")
            return connection
        except Exception as e:
            print(f"Error en la conexion: {e}")
            return None


# Instancia única para acceder a la clase
db_conn = ConnectDB()


def get_db_connection():
    return db_conn.get_connection()
