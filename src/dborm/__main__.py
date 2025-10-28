import os
import sys
import argparse

from dborm import __module_name__, __module_description__, __module_version__, logger
from dborm.dborm import generate_orm_code

from dbutils.dbini import DBIni, DB_INIFILE
from dbutils.customhelp import CustomHelpFormatter

def main():

    # define el parser
    parser = argparse.ArgumentParser(
        prog=__module_name__, 
        description=f"{__module_description__} (v{__module_version__})", 
        epilog='Y dborm dijo: ¡Háganse tus clases!', 
        add_help=False, 
        formatter_class=CustomHelpFormatter
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('--gen-classes', metavar='PREFIX', nargs='?', const='', help='Genera las clases ORM para la base de datos. Si se especifica un prefijo, sólo se incluirán las tablas que empiecen por ese prefijo.')
    
    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--db-url', metavar='URL', nargs='?', help='URL de conexión a la base de datos')
    options.add_argument('--db-name', metavar='DB', nargs='?', help=f"Nombre de la base de datos en el fichero {DB_INIFILE}")
    options.add_argument('--output', metavar='DIR', nargs='?', const='.', help='Directorio de salida para los ficheros generados. Por defecto, el directorio actual.')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return
    
    # Carga la configuración y conecta a la base de datos
    if args.db_url or args.db_name:
        # Si no se ha especificado una URL de conexión a la base de datos, intenta obtenerla de las variables de entorno
        try:
            db_url = args.db_url or DBIni.load().get_url(args.db_name)
        except Exception as e:
            logger.error(f"No se ha podido obtener la URL de conexión a la base de datos", e)
            sys.exit(1)

    
    if args.gen_classes is not None:
        output = args.output or '.'
        prefix = args.gen_classes or ''
        try:
            print(f"Generando las clases ORM en el directorio '{output}'...")
            generate_orm_code(db_url, prefix, output)
        except ValueError as e:
            logger.error(f"Error: {e}")
