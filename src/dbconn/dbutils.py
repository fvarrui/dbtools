
from sqlalchemy import create_engine
from dbconn.dbini import get_db_connection_url
from urllib.parse import urlparse

def test_connection(connection_url):
    """
    Prueba la conexión a la base de datos.
    """
    try:
        engine = create_engine(connection_url)
        with engine.connect() as connection:
            print("Conexión exitosa")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")

# Test the function
connection_url = get_db_connection_url("dbtools.ini", "triacademy")
print("Connection URL:", connection_url)
test_connection(connection_url)
