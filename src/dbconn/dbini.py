import os
from string import Template
from urllib.parse import quote_plus
import configparser

DBMS_DEFAULT_CONFIG = {
    "mysql": {
        "port": 3306,
        "template": "mysql+pymysql://${username}:${password}@${host}:${port}/${database}"
    },
    "postgresql": {
        "port": 5432,
        "template": "postgresql+psycopg2://${username}:${password}@${host}:${port}/${database}"
    },
    "sqlserver": {
        "port": 1433,
        "template": "mssql+pyodbc://${username}:${password}@${host}:${port}/${database}?driver=${driver}&trusted_connection=${trusted_connection}",
        "driver": "ODBC Driver 17 for SQL Server"
    },
    "sqlserver+sspi": {
        "port": 1433,
        "template": "mssql+pyodbc://${host}:${port}/${database}?driver=${driver}&trusted_connection=yes",
        "driver": "ODBC Driver 17 for SQL Server"
    }
}

PASSWORD_PLACEHOLDER = "{PASSWORD}"

def get_connection_url(ini_file_path, section_name):
    """
    Obtiene la URL de conexión a la base de datos desde un archivo .ini.
    Args:
        ini_file_path (str): Ruta al archivo .ini.
        section_name (str): Nombre de la sección que contiene la configuración de la base de datos.
    Returns:
        str: URL de conexión a la base de datos.
    """

    if os.path.exists(ini_file_path) is False:
        raise FileNotFoundError(f"No se ha encontrado el archivo de configuración: {ini_file_path}")

    config = configparser.ConfigParser()
    config.read(ini_file_path)

    if section_name not in config:
        raise ValueError(f"No se ha encontrado la sección '{section_name}' en el archivo de configuración")

    try:
        section = config[section_name]
        db_type = section["type"]

        if db_type not in DBMS_DEFAULT_CONFIG:
            raise ValueError(f"Tipo de base de datos no soportado: {db_type}")

        username = quote_plus(section["username"])
        password = quote_plus(section["password"]) if "password" in section else PASSWORD_PLACEHOLDER
        host = section["host"]
        port = section["port"] if "port" in section else DBMS_DEFAULT_CONFIG[db_type]["port"]
        database = quote_plus(section["database"])
        trusted_connection = "yes" if section.getboolean("trusted_connection", fallback=False) else "no"
        driver = quote_plus(section["driver"] if "driver" in section else DBMS_DEFAULT_CONFIG[db_type].get("driver", ""))        

        template = Template(DBMS_DEFAULT_CONFIG[db_type]["template"])
        connection_url = template.substitute(
            username=username, 
            password=password, 
            host=host, port=port, 
            database=database, 
            driver=driver, 
            trusted_connection=trusted_connection
        )
        return connection_url

    except KeyError as e:
        raise ValueError(f"Falta la clave requerida en la sección '{section}': {e}")

def has_undefined_password(connection_url):
    """
    Comprueba si la URL de conexión contiene una contraseña no definida.
    Args:
        connection_url (str): URL de conexión.
    Returns:
        bool: True si la URL de conexión contiene una contraseña no definida, False en caso contrario.
    """
    return PASSWORD_PLACEHOLDER in connection_url

def replace_password_placeholder(connection_url, password):
    """
    Reemplaza el marcador de posición de la contraseña en la URL de conexión.
    Args:
        connection_url (str): URL de conexión.
        password (str): Contraseña a reemplazar.
    Returns:
        str: URL de conexión con la contraseña reemplazada.
    """
    password = quote_plus(password)
    return connection_url.replace(PASSWORD_PLACEHOLDER, password)