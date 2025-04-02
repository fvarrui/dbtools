import os
from configparser import ConfigParser
from dbutils.dbconfig import DBConfig

DBTOOLS_DIR = os.path.join(os.path.expanduser("~"), ".dbtools")
DB_INIFILE = "dbtools.ini"

class DBIni():

    inifile: str = None
    config: ConfigParser = None

    def __init__(self, inifile: str):
        """
        Inicializa la clase DBIni.
        Args:
            inifile (str): Ruta al archivo de configuración .ini.
        """
        self.inifile = inifile
        self.config = ConfigParser()
        if os.path.exists(inifile):
            self.config.read(inifile)
 
    def exists(self, section_name: str) -> bool:
        """
        Comprueba si una sección existe en el archivo .ini.
        Args:
            section_name (str): Nombre de la sección a comprobar.
        Returns:
            bool: True si la sección existe, False en caso contrario.
        """
        return self.config.has_section(section_name)

    @classmethod
    def load(cls) -> "DBIni":
        """
        Carga la configuración de un archivo .ini.
        Args:
            inifile (str): Ruta al archivo .ini.
        Returns:
            DBIni: Instancia de la clase DBIni.
        """
        local_inifile = os.path.join(os.getcwd(), DB_INIFILE)
        user_inifile = os.path.join(DBTOOLS_DIR, DB_INIFILE)
        if os.path.exists(local_inifile):
            return cls(local_inifile)
        elif os.path.exists(user_inifile):
            return cls(user_inifile)
        raise FileNotFoundError(f"No se ha encontrado el archivo de configuración: {local_inifile} o {user_inifile}")

    def save(self):
        """
        Guarda los cambios en el archivo .ini.
        """
        dirname = os.path.dirname(self.inifile)
        if dirname != '' and not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(self.inifile, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

    def get_config(self, section_name: str) -> DBConfig:
        """
        Obtiene la configuración de una sección del archivo .ini.
        Args:
            section_name (str): Nombre de la sección a obtener.
        Returns:
            dict: Diccionario con la configuración de la sección.
        """
        if section_name not in self.config:
            raise ValueError(f"No se ha encontrado la sección '{section_name}' en el archivo de configuración")
        return DBConfig.from_section(self.config[section_name])
    
    def get_url(self, section_name: str, placeholders: dict[str,any] = None, censored: bool = False) -> str:
        """
        Obtiene la URL de conexión a la base de datos a partir de una sección del archivo .ini.
        Args:
            section_name (str): Nombre de la sección a obtener.
        Returns:
            str: URL de conexión a la base de datos.
        """
        return self.get_config(section_name).to_url(placeholders=placeholders, censored=censored)

    def add_config(self, section_name: str, config: DBConfig):
        """
        Añade una sección de configuración a un archivo .ini. (si existe la sección, la actualiza)
        Args:
            section_name (str): Nombre de la sección a añadir.
            config (dict): Diccionario con la configuración a añadir.
        """
        if section_name not in self.config:
            self.config.add_section(section_name)
        else:
            raise ValueError(f"La sección '{section_name}' ya existe en el archivo de configuración")
        for key, value in config.to_section().items():
            self.config.set(section_name, key, str(value))

    def remove_config(self, section_name: str):
        """
        Elimina una sección de configuración de un archivo .ini.
        Args:
            section_name (str): Nombre de la sección a eliminar.
        """
        if section_name not in self.config:
            raise ValueError(f"No se ha encontrado la sección '{section_name}' en el archivo de configuración")
        self.config.remove_section(section_name)



