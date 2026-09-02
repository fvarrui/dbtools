import os
import argparse
from getpass import getpass

from tabulate import tabulate

from dbutils import __module_name__, __module_description__
from dbutils.config import Config, CONFIG_INIFILE
from dbutils.dbconfig import DBConfig, DBMS_DEFAULT_CONFIG
from dbutils.dbini import DBIni, DB_INIFILE, DBTOOLS_DIR
from dbutils.customhelp import CustomHelpFormatter
from dbutils.dbutils import test_connection

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

def input_db_config(
    config: DBIni,
    section_name: str = None,
    type: str = None,
    username: str = None,
    password: str = None,
    host: str = None,
    port: int = None,
    database: str = None,
    driver: str = None,
    trusted_connection: bool = None,
) -> tuple[str, DBConfig]:
    """
    Solicita al usuario los datos de configuración de la base de datos que no se hayan indicado ya.
    Args:
        config (DBIni): Fichero de configuración donde comprobar si ya existe la sección.
        Los demás argumentos son valores ya conocidos (p.ej. proporcionados por línea de comandos);
        si se indican, no se pregunta por ellos.
    Returns:
        tuple[str, DBConfig]: Nombre de la sección y configuración de la base de datos.
    """
    if section_name is None:
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
    if type is None:
        type = default_input("- Tipo de base de datos (mssql, mysql, postgresql)", mandatory=True, default=db_config.type if db_config else None)
    if type not in DBMS_DEFAULT_CONFIG:
        raise ValueError(f"Tipo de base de datos no soportado: {type}")
    if username is None:
        username = default_input("- Usuario", default=db_config.username if db_config else None)
    if password is None:
        password = getpass("- Contraseña: ") if username else None
    if host is None:
        host = default_input("- Servidor (host)", default=db_config.host if db_config else "localhost")
    if port is None:
        port = int(default_input("- Puerto", default=db_config.port if db_config else DBMS_DEFAULT_CONFIG[type]['port']))
    if database is None:
        database = default_input("- Base de datos", mandatory=True, default=db_config.database if db_config else None)
    if driver is None:
        driver = default_input("- Controlador ODBC", default=db_config.driver if db_config else DBMS_DEFAULT_CONFIG[type]['driver']) if type == "mssql" else None
    if trusted_connection is None:
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
        description=__module_description__,
        epilog='¡Déjame ayudarte!',
        add_help=False,
        formatter_class=CustomHelpFormatter
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('--create-config', action='store_true', help=f'Crea el fichero de configuración (por defecto: {DEFAULT_CONFIG_INIFILE})')
    commands.add_argument('--create-db-config', metavar='DIR', nargs='?', const='', help=f'Crea el fichero de configuración de las bases de datos (por defecto: {DEFAULT_DB_INIFILE})')
    commands.add_argument('--test-connection', metavar='DIR', nargs='?', const='', help=f'Prueba la conexión a la base de datos')
    commands.add_argument('--get-url', metavar='DIR', nargs='?', const='', help=f'Devuelve la URL de conexión para un --db-name dado')
    commands.add_argument('--list', action='store_true', help=f'Lista los nombres de las configuraciones de bases de datos del fichero {DB_INIFILE} que se alcance (directorio actual o {DBTOOLS_DIR})')
    commands.add_argument('--show', metavar='NAME', help='Muestra la configuración completa de la base de datos indicada')
    commands.add_argument('--add', metavar='NAME', help=f'Añade una nueva configuración de base de datos al fichero {DEFAULT_DB_INIFILE}. Los datos no indicados por línea de comandos se piden por consola.')

    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--db-name', metavar='NAME', help='Nombre de la configuración de la base de datos')
    options.add_argument('--db-url', metavar='URL', help='URL de conexión a la base de datos')
    options.add_argument('--type', metavar='TYPE', choices=list(DBMS_DEFAULT_CONFIG.keys()), help='Tipo de base de datos (mysql, postgresql, mssql). Usado con --add.')
    options.add_argument('--host', metavar='HOST', help='Servidor de la base de datos. Usado con --add.')
    options.add_argument('--port', metavar='PORT', type=int, help='Puerto de la base de datos. Usado con --add.')
    options.add_argument('--database', metavar='DATABASE', help='Nombre de la base de datos. Usado con --add.')
    options.add_argument('--username', metavar='USERNAME', help='Usuario de conexión a la base de datos. Usado con --add. La contraseña nunca se acepta por línea de comandos: se pide por consola.')
    options.add_argument('--driver', metavar='DRIVER', help='Controlador ODBC (SQL Server). Usado con --add.')
    options.add_argument('--trusted-connection', action='store_true', help='Usa conexión confiable / autenticación de Windows (SQL Server). Usado con --add.')

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
            if args.db_url:
                connection_url = args.db_url
                label = args.db_url
            elif args.db_name:
                if args.test_connection == '':
                    db_config_path = DEFAULT_DB_INIFILE
                else:
                    db_config_path = os.path.join(args.test_connection, DB_INIFILE)
                config = DBIni(db_config_path)
                db_config = config.get_config(args.db_name)
                connection_url = db_config.to_url()
                label = args.db_name
            else:
                raise ValueError("Se debe indicar --db-name o --db-url")
            print(f"Probando la conexión: {label}...")
            ok, error = test_connection(connection_url)
            if ok:
                print(f"- Conexión exitosa.")
            else:
                print(f"- Error al conectar: {error}")
        except ValueError as e:
            print(f"Error: {e}")
        return

    if args.get_url is not None:
        try:
            if not args.db_name:
                raise ValueError("No se ha indicado el nombre de la configuración de la base de datos")
            if args.get_url == '':
                db_config_path = DEFAULT_DB_INIFILE
            else:
                db_config_path = os.path.join(args.get_url, DB_INIFILE)
            config = DBIni(db_config_path)
            db_config = config.get_config(args.db_name)
            print(db_config.to_url())
        except ValueError as e:
            print(f"Error: {e}")
        return

    if args.list:
        try:
            config = DBIni.load()
            names = sorted(config.list_sections())
            print(f"Configuraciones de bases de datos en {config.inifile}:\n")
            if names:
                print(tabulate([[name] for name in names], headers=["DB_NAME"], tablefmt="grid"))
            print(f"\n{len(names)} configuraciones encontradas")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        return

    if args.show is not None:
        try:
            config = DBIni.load()
            db_config = config.get_config(args.show)
            section = db_config.to_section()
            if "password" in section:
                section["password"] = DBConfig.censor(section["password"])
            print(f"Configuración de '{args.show}' en {config.inifile}:\n")
            print(tabulate(section.items(), headers=["CAMPO", "VALOR"], tablefmt="grid"))
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
        return

    if args.add is not None:
        try:
            if not os.path.exists(DEFAULT_DB_INIFILE):
                create = default_input(f"El fichero de configuración {DEFAULT_DB_INIFILE} no existe. ¿Quieres crearlo? (S/n)", default="s").lower() == "s"
                if not create:
                    print("Cancelando la operación.")
                    return
            config = DBIni(DEFAULT_DB_INIFILE)
            result = input_db_config(
                config,
                section_name=args.add,
                type=args.type,
                username=args.username,
                host=args.host,
                port=args.port,
                database=args.database,
                driver=args.driver,
                trusted_connection=True if args.trusted_connection else None,
            )
            if result:
                section_name, db_config = result
                config.add_config(section_name, db_config)
                config.save()
                print(f"\nURL de la conexión: {db_config.to_url(include_lib=False, censored=True)}")
                print(f"Configuración guardada en la sección {section_name} del fichero {DEFAULT_DB_INIFILE}")
            else:
                print("- No se ha guardado la configuración.")
        except ValueError as e:
            print(f"Error: {e}")
        return