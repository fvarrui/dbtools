import re
from dataclasses import dataclass
from urllib.parse import urlparse, quote_plus, unquote_plus
from string import Template

"""
Configuración por defecto para los SGBD soportados.
- mysql: MySQL/MariaDB
- postgresql: PostgreSQL
- mssql: SQL Server
"""
DBMS_DEFAULT_CONFIG = {
    "mysql": {
        "library": "pymysql",
        "template": "mysql${library}://${credentials}@${host}:${port}/${database}",
        "port": 3306
    },
    "postgresql": {
        "library": "psycopg2",
        "template": "postgresql${library}://${credentials}@${host}:${port}/${database}",
        "port": 5432
    },
    "mssql": {
        "library": "pyodbc",
        "template": "mssql${library}://${credentials}@${host}:${port}/${database}?driver=${driver}&trusted_connection=${trusted_connection}",
        "port": 1433,
        "driver": "ODBC Driver 17 for SQL Server"
    },
}
CREDENTIALS_TEMPLATE = "${username}:${password}"
PASSWORD_PLACEHOLDER = "{PASSWORD}"

@dataclass
class DBConfig():
    """
    Clase para almacenar la configuración de la base de datos.
    """
    type: str
    username: str
    password: str
    host: str
    port: int
    database: str
    driver: str
    trusted_connection: bool

    def __init__(self, type: str, host: str, port: int, database: str, username: str = None, password: str = None, driver: str = None, trusted_connection: bool = False):
        """
        Inicializa la configuración de la base de datos.
        Args:
            type (str): Tipo de base de datos (mysql, postgresql, mssql).
            host (str): Host de la base de datos.
            port (int): Puerto de la base de datos.
            database (str): Nombre de la base de datos.
            username (str): Nombre de usuario para la conexión.
            password (str): Contraseña para la conexión.
            driver (str): Controlador ODBC para SQL Server.
            trusted_connection (bool): Si se debe usar una conexión confiable para SQL Server.
        """
        if type not in DBMS_DEFAULT_CONFIG:
            raise ValueError(f"Tipo de base de datos no soportado: {type}")
        if type == "mssql" and driver is None:
            driver = DBMS_DEFAULT_CONFIG[type]["driver"]
        if type == "mssql" and username is None:
            trusted_connection = True
        if username is not None and password is None:
            password = PASSWORD_PLACEHOLDER
        self.type = type
        self.username = username
        self.password = password
        self.host = host
        self.port = port if port is not None else DBMS_DEFAULT_CONFIG[type]["port"]
        self.database = database
        self.driver = driver
        self.trusted_connection = trusted_connection

    @classmethod
    def from_section(cls, section: dict) -> "DBConfig":
        """
        Crea una instancia de DBConfig a partir de una sección de configuración.
        Args:
            section (dict): Sección de configuración de la base de datos.
        Returns:
            DBConfig: Objeto con la configuración de la base de datos.
        """
        # Comprueba si el tipo de base de datos es válido
        db_type = section["type"]
        if db_type not in DBMS_DEFAULT_CONFIG:
            raise ValueError(f"Tipo de base de datos no soportado: {db_type}")
        
        # Crea una instancia de DBConfig con los valores descompuestos
        return cls(
            type = db_type,
            username = section["username"] if "username" in section else None,
            password = section["password"] if "password" in section else None,
            host = section["host"],
            port = int(section["port"]) if "port" in section else DBMS_DEFAULT_CONFIG[db_type]["port"],
            database = section["database"],
            driver = section.get("driver", DBMS_DEFAULT_CONFIG[db_type]["driver"] if db_type == "mssql" else None),
            trusted_connection = section.get("trusted_connection") == "yes" if "trusted_connection" in section else False
        )

    @classmethod
    def from_url(cls, dburl: str) -> "DBConfig":
        """
        Crea una instancia de DBConfig a partir de una URL de conexión.
        Args:
            url (str): URL de conexión a la base de datos.
        Returns:
            DBConfig: Objeto con la configuración de la base de datos.
        """
        # Descompone la URL de conexión en sus componentes
        url_parsed = urlparse(dburl)

        # Comprueba si la URL tiene un esquema válido        
        db_type = url_parsed.scheme
        if db_type not in DBMS_DEFAULT_CONFIG:
            raise ValueError(f"Tipo de base de datos no soportado: {db_type}")
        
        # Convierte los parámetros de la URL en un diccionario
        query_params = {}
        for param in url_parsed.query.split("&"):
            key, value = param.split("=")
            query_params[key] = unquote_plus(value)

        username = unquote_plus(url_parsed.username) if url_parsed.username else None
        password = unquote_plus(url_parsed.password) if url_parsed.password else None

        if username is not None and password is None:
            password = ''

        # Crea una instancia de DBConfig con los valores descompuestos        
        return cls(
            type = db_type,
            username = username,
            password = password,
            host = url_parsed.hostname or "",
            port = int(url_parsed.port) if url_parsed.port else None,
            database = unquote_plus(url_parsed.path[1:]) if url_parsed.path else "",
            driver = unquote_plus(query_params["driver"]) if "driver" in query_params else None,
            trusted_connection = query_params["trusted_connection"] == "yes" if "trusted_connection" in query_params else None
        )
    
    def to_section(self) -> dict:
        """
        Devuelve una representación en diccionario de la configuración de la base de datos.
        Returns:
            dict: Representación en diccionario de la configuración de la base de datos.
        """
        config = {
            "type": self.type,
            "username": self.username,
            "password": self.password,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "driver": self.driver,
            "trusted_connection": "yes" if self.trusted_connection else "no"
        }
        return {k: v for k, v in config.items() if v is not None}  # Elimina valores None

    def to_url(self, include_lib = True, placeholders: dict = None) -> str:
        """
        Devuelve una representación en cadena de la configuración de la base de datos.
        Returns:
            str: Representación en cadena de la configuración de la base de datos.
        """

        # Obtiene la plantilla de la URL de conexión para el SGBD especificado
        template = Template(DBMS_DEFAULT_CONFIG[self.type]["template"])

        # Compone las credenciales de la URL de conexión
        if self.username:
            credentials_template = Template(CREDENTIALS_TEMPLATE)
            credentials = credentials_template.substitute(
                username=quote_plus(self.username) if self.username else "", 
                password=quote_plus(self.password) if self.password != PASSWORD_PLACEHOLDER else PASSWORD_PLACEHOLDER
            )
        else:
            credentials = ""

        # Sustituye los marcadores de posición por los valores de la sección
        url = template.substitute(
            library=f"+{DBMS_DEFAULT_CONFIG[self.type]["library"]}" if include_lib else "",
            credentials=credentials, 
            host=self.host, 
            port=self.port, 
            database=quote_plus(self.database), 
            driver=quote_plus(self.driver) if self.driver else "", 
            trusted_connection=self.trusted_connection        
        )

        # Si se especifican marcadores de posición, los sustituye por sus valores
        return url if placeholders is None else self.__replace_placeholders__(url, placeholders)

    def find_placeholders(self) -> list[str]:
        """
        Busca los marcadores de posición en la URL de conexión y devuelve un diccionario con los valores.
        Args:
            connection_url (str): URL de conexión a la base de datos.
        Returns:
            dict: Diccionario con los valores de los marcadores de posición.
        """
        placeholder_regex = r"\{(.+)\}"
        placeholders = []
        matches = re.findall(placeholder_regex, self.to_url())
        for match in matches:
            match = match.strip()
            placeholders.append(match)
        return placeholders

    def __replace_placeholders__(self, url, placeholders : dict[str,any]) -> str:
        """
        Reemplaza los marcadores de posición en la URL de conexión con sus valores correspondientes.
        Args:
            placeholders (dict): Diccionario con los valores de los marcadores de posición.
        Returns:    
            str: URL de conexión a la base de datos con los marcadores de posición reemplazados.
        """
        for key, value in placeholders.items():
            if value is None:
                continue
            if isinstance(value, str):
                value = quote_plus(value)
            connection_url = url.replace(f"{{{key}}}", str(value))
        return connection_url