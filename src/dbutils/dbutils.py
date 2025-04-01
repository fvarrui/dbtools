
from sqlalchemy import create_engine

def test_connection(connection_url) -> tuple[bool, Exception]:
    """
    Prueba la conexión a la base de datos.
    """
    try:
        engine = create_engine(connection_url)
        with engine.connect():
            return (True, None)
    except Exception as e:
        return (False, e)