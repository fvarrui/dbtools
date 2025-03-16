from urllib.parse import quote_plus
import configparser
from getpass import getpass

def __get_mysql_connection_url(section, ask_password=False):
    username = quote_plus(section["username"])
    password = quote_plus(section["password"]) if "password" in section else ""
    host = section["host"]
    port = section["port"] if "port" in section else "3306"
    database = quote_plus(section["database"])
    if not password and ask_password:
        password = quote_plus(getpass(f"Introduce la contraseña para el usuario {username}: "))    
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

def __get_postgresql_connection_url(section, ask_password=False):
    username = quote_plus(section["username"])
    password = quote_plus(section["password"] if "password" in section else "")
    host = section["host"]
    port = section["port"] if "port" in section else "5432"
    database = quote_plus(section["database"])
    if not password and ask_password:
        password = quote_plus(getpass(f"Introduce la contraseña para el usuario {username}: "))    
    return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

def __get_sqlserver_connection_url(section, ask_password=False):
    username = quote_plus(section["username"])
    password = quote_plus(section["password"] if "password" in section else "")
    host = section["host"]
    port = section["port"] if "port" in section else "1433"
    database = section["database"]
    trusted_connection = "yes" if section.getboolean("trusted_connection", fallback=False) else "no"
    driver = quote_plus(section["driver"] if "driver" in section else "ODBC Driver 17 for SQL Server")
    if username:
        if not password and ask_password:
            password = quote_plus(getpass(f"Introduce la contraseña para el usuario {username}: "))
        return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver={driver}&trusted_connection={trusted_connection}"
    else:
        return f"mssql+pyodbc://{host}:{port}/{database}?driver={driver}&trusted_connection={trusted_connection}"

def get_db_connection_url(ini_file_path, section_name, ask_password=False):
    """
    Obtiene la URL de conexión a la base de datos desde un archivo .ini.

    Args:
        ini_file_path (str): Ruta al archivo .ini.
        section_name (str): Nombre de la sección que contiene la configuración de la base de datos.

    Returns:
        str: URL de conexión a la base de datos.
    """
    config = configparser.ConfigParser()
    config.read(ini_file_path)

    if section_name not in config:
        raise ValueError(f"La sección '{section_name}' no existe en el archivo {ini_file_path}")

    try:
        section = config[section_name]
        db_type = section["type"]
        if db_type == "mysql":
            return __get_mysql_connection_url(section, ask_password=ask_password)
        elif db_type == "postgresql":
            return __get_postgresql_connection_url(section, ask_password=ask_password)
        elif db_type == "sqlserver":
            return __get_sqlserver_connection_url(section, ask_password=ask_password)
        else:
            raise ValueError(f"Tipo de base de datos no soportado: {db_type}")
    except KeyError as e:
        raise ValueError(f"Falta la clave requerida en la sección '{section}': {e}")
