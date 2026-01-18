import pymysql
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()


MYSQL_URL = os.environ["MYSQL_URL"]


url = urlparse(MYSQL_URL)

MYSQL_USER = url.username
MYSQL_PASSWORD = url.password
MYSQL_HOST = url.hostname
MYSQL_PORT = url.port
MYSQL_DATABASE = url.path.lstrip("/")  # railway

class ConnectDB:
    def __init__(self):
        pass

    def get_connection(self):
        try:
            connection = pymysql.connect(
                host=MYSQL_HOST,
                port=int(MYSQL_PORT),
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Conexion exitosa a MYSQL")
            return connection
        except Exception as e:
            print(f"Error en la conexion: {e}")
            return None



db_conn = ConnectDB()

def get_db_connection():
    return db_conn.get_connection()
