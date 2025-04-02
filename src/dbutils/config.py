import os
from configparser import ConfigParser

CONFIG_INIFILE = "config.ini"
SECTION_NAME = "DBTools"
DEFAULT_PROPS = {
    "open.apikey": ""
}

class Config:

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
        if os.path.exists(self.inifile):
            self.config.read(self)
        if not self.config.has_section(SECTION_NAME):
            self.config.add_section(SECTION_NAME)
            for key, value in DEFAULT_PROPS.items():
                self.config.set(SECTION_NAME, key, value)

    def save(self):
        """
        Guarda los cambios en el archivo .ini.
        """
        dirname = os.path.dirname(self.inifile)
        if dirname != '' and not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(self.inifile, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

    def set_value(self, key: str, value: any):
        """
        Almacena un valor en el archivo de configuración.
        Args:
            key (str): Clave del valor a almacenar.
            value (any): Valor a almacenar.
        """
        self.config.set(SECTION_NAME, key, value)

    def get_value(self, key: str) -> any:
        """
        Obtiene un valor del archivo de configuración.
        Args:
            key (str): Clave del valor a obtener.
        Returns:
            any: Valor almacenado con la clave especificada.
        """
        return self.config.get(SECTION_NAME, key)