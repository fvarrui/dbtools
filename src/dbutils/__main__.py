import os
import argparse
from getpass import getpass

from dbutils import __module_name__, __module_description__, __module_version__
from dbutils.config import Config, CONFIG_INIFILE
from dbutils.dbconfig import DBConfig, DBMS_DEFAULT_CONFIG
from dbutils.dbini import DBIni, DB_INIFILE
from dbutils.customhelp import CustomHelpFormatter
from dbutils.dbutils import test_connection

DBTOOLS_DIR = os.path.join(os.path.expanduser("~"), ".dbtools")
DEFAULT_CONFIG_INIFILE = os.path.join(DBTOOLS_DIR, CONFIG_INIFILE)
DEFAULT_DB_INIFILE = os.path.join(DBTOOLS_DIR, DB_INIFILE)

def default_input(prompt: str, default: str = None, mandatory: bool = False) -> str:
    """
    Solicita al usuario un valor de entrada con un valor por defecto.
    Args:
        prompt (str): Mensaje de entrada.
        default (str): Valor por defecto.
    Returns:
        str: Valor introducido por el usuario o el valor por defecto.
    """
    if mandatory and default is None:
        prompt += " *"
    if default is None:
        value = input(f"{prompt}: ")
    else:
        value = input(f"{prompt} [{default}]: ")
    if default and not value:
        value = default
    if mandatory and not value:
        raise ValueError("El valor es obligatorio")
    return value if value else default

def input_db_config(config : DBIni) -> tuple[str, DBConfig]:
    """
    Solicita al usuario los datos de configuración de la base de datos.
    Returns:
        DBConfig: Objeto con la configuración de la base de datos.
    """
    section_name = default_input("- Indica el nombre de la configuración", mandatory=True)
    db_config = None
    if config.exists(section_name):
        overwrite = default_input(f"Ya existe una configuración con el nombre {section_name}. ¿Quieres sobrescribirla? (S/n)", default="n").lower() == "s"
        if not overwrite:
            print("Cancelando la operación.")
            return None
        else:
            db_config = config.get_config(section_name)
    print("\nIntroduce los datos de configuración de la base de datos:")
    type = default_input("- Tipo de base de datos (mssql, mysql, postgresql)", mandatory=True, default=db_config.type if db_config else None)
    if type not in DBMS_DEFAULT_CONFIG:
        raise ValueError(f"Tipo de base de datos no soportado: {type}")
    username = default_input("- Usuario", default=db_config.username if db_config else None)
    password = getpass("- Contraseña: ") if username else None
    host = default_input("- Servidor (host)", default=db_config.host if db_config else "localhost")
    port = int(default_input("- Puerto", default=db_config.port if db_config else DBMS_DEFAULT_CONFIG[type]['port']))
    database = default_input("- Base de datos", mandatory=True, default=db_config.database if db_config else None)
    driver = default_input("- Controlador ODBC", default=db_config.driver if db_config else DBMS_DEFAULT_CONFIG[type]['driver']) if type == "mssql" else None
    trusted_connection = default_input("- Conexión confiable (True/False): ", default=db_config.trusted_connection if db_config else 'False').lower() == "true" if type == "mssql" else None
    return section_name, DBConfig(
        type=type,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
        driver=driver,
        trusted_connection=trusted_connection,
    )

def main():

    # define el parser
    parser = argparse.ArgumentParser(
        prog=__module_name__, 
        description=f"{__module_description__} (v{__module_version__})", 
        epilog='¡Déjame ayudarte!', 
        add_help=False, 
        formatter_class=CustomHelpFormatter
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('--create-config', action='store_true', help=f'Crea el fichero de configuración (por defecto: {DEFAULT_CONFIG_INIFILE})')
    commands.add_argument('--create-db-config', metavar='DIR', nargs='?', const='', help=f'Crea el fichero de configuración de las bases de datos (por defecto: {DEFAULT_DB_INIFILE})')
    commands.add_argument('--test-connection', metavar='DIR', nargs='?', const='', help=f'Prueba la conexión a la base de datos')
    
    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--db-name', metavar='NAME', nargs='?', help='Nombre de la configuración de la base de datos')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return
    
    if args.create_config:
        try:
            print(f"Creando el fichero de configuración {DEFAULT_CONFIG_INIFILE}...")
            if not os.path.exists(DEFAULT_CONFIG_INIFILE):
                config = Config(DEFAULT_CONFIG_INIFILE)
                config.save()
                print(f"- Fichero de configuración creado: {DEFAULT_CONFIG_INIFILE}")
            else:
                print(f"- El fichero de configuración ya existe: {DEFAULT_CONFIG_INIFILE}")        
        except ValueError as e:
            print(f"Error: {e}")

    if args.create_db_config is not None:
        try:
            if args.create_db_config == '':
                db_config_path = DEFAULT_DB_INIFILE
            else:
                db_config_path = os.path.join(args.create_db_config, DB_INIFILE)
            print(f"Creando configuración de bases de datos en {db_config_path}...")
            config = DBIni(db_config_path)
            section_name, db_config = input_db_config(config)
            if db_config:
                config.add_config(section_name, db_config)
                config.save()
                print(f"\nURL de la conexión: {db_config.to_url(include_lib=False, censored=True)}")
                print(f"Configuración guardada la sección {section_name} del fichero {db_config_path}")
            else:
                print("- No se ha guardado la configuración.")
        except ValueError as e:
            print(f"Error: {e}")
        return
    
    if args.test_connection is not None:
        try:
            if not args.db_name:
                raise ValueError("No se ha indicado el nombre de la configuración de la base de datos")
            if args.test_connection == '':
                db_config_path = DEFAULT_DB_INIFILE
            else:
                db_config_path = os.path.join(args.test_connection, DB_INIFILE)
            print(f"Probando la conexión a la base de datos {args.db_name} en {db_config_path}...")
            config = DBIni(db_config_path)
            if args.db_name:
                db_config = config.get_config(args.db_name)
                ok, error = test_connection(db_config.to_url())
                if ok:
                    print(f"- Conexión a la base de datos {args.db_name} exitosa.")
                else:
                    print(f"- Error al conectar a la base de datos {args.db_name}: {error}")
        except ValueError as e:
            print(f"Error: {e}")
        return