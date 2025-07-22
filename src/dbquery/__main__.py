import sys
import json
import argparse

from tabulate import tabulate

from sqlalchemy import text
from dbquery import __module_name__, __module_description__, __module_version__
from dbquery.natlang import generate_query
from dbschema.database import Database
from dbutils.config import Config
from dbutils.customhelp import CustomHelpFormatter
from dbutils.dbini import DB_INIFILE, DBIni

def db_connect(args):
    database = None
    if args.db_url or args.db_name:
        try:
            # Si no se ha especificado una URL de conexión a la base de datos, intenta obtenerla de las variables de entorno
            db_url = args.db_url or DBIni.load().get_url(args.db_name)
        except Exception as e:
            print(f"No se ha podido obtener la URL de conexión a la base de datos: {e}", file=sys.stderr)
            sys.exit(1)

        # Conecta a la base de datos
        try:
            database = Database(db_url)
            database.connect()
            print(f"🏓 Conectado a la base de datos '{database.name}'")
        except Exception as e:
            print(f"😨 ¡No se ha podido conectar a la base de datos!", e, file=sys.stderr)
            sys.exit(1)
    return database

def load_sql(sql_file):
    try:
        print(f"📄 Leyendo consulta SQL desde el fichero '{sql_file}'...")
        with open(sql_file, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ No se ha encontrado el fichero '{sql_file}'.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al leer el fichero '{sql_file}': {e}", file=sys.stderr)
        sys.exit(1)

def main():

    # define el parser
    parser = argparse.ArgumentParser(
        prog=__module_name__, 
        description=f"{__module_description__} (v{__module_version__})", 
        epilog='¡No me pidas un deseo, pídeme datos! ... pero pídelos por favor', 
        add_help=False, 
        formatter_class=CustomHelpFormatter
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('--sql', metavar='QUERY', nargs='?', const='', help='Devuelve el resultado de una consulta SQL')
    commands.add_argument('--sql-file', metavar='FILE', nargs='?', const='', help='Devuelve el resultado de una consulta SQL proporcionada en un fichero')
    commands.add_argument('--nat-lang', '-nl', metavar='QUERY', nargs='?', const='', help='Devuelve el resultado de una consulta en lenguaje natural')
    
    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--db-url', metavar='URL', nargs='?', help='URL de conexión a la base de datos')
    options.add_argument('--db-name', metavar='DB', nargs='?', help=f"Nombre de la base de datos en el fichero {DB_INIFILE}")
    options.add_argument('--json', metavar='FILE', nargs='?', const='', help='Entrada o salida en formato JSON. Si no se especifica un fichero, se utiliza la entrada y salida estándar.')
    options.add_argument('--output', metavar='DIR', nargs='?', const='.', help='Directorio de salida para los ficheros generados. Por defecto, el directorio actual.')
    options.add_argument('--schema', metavar='DIR', nargs='?', const='.', help='Directorio con el esquema de la base de datos en formato JSON. Necesario para consultas en lenguaje natural.')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return

    database = db_connect(args)

    # Listar las vistas
    if args.sql is not None or args.sql_file is not None:

        if database is None:
            print("❌ No se ha especificado una base de datos. Por favor, utiliza --db-url o --db-name para conectarte a una base de datos.")
            sys.exit(1)

        if args.sql_file is not None and args.sql_file != '':
            sql = load_sql(args.sql_file)
        elif args.sql is not None and args.sql != '':
            sql = args.sql if args.sql else input("❔ Introduce la consulta SQL: ")
            
        print(f"⚙️ Ejecutando consulta SQL: '{sql}'...")

        sql = sql.strip()
        query = text(sql)
        result = database.execute(query)

        if args.json is not None:
            
            if args.json == '':
                json_output = sys.stdout
            else:
                json_output = open(args.json, 'w', encoding='utf-8')

            json.dump(result, json_output, indent=4, ensure_ascii=False)            

            if args.json != '':
                print(f"\n✅ Resultado guardado en {args.json} con {len(result)} filas.")
            else:
                print(f"\n✅ Resultado mostrado con {len(result)} filas.")

        else:
            print(tabulate(result, headers="keys", tablefmt="grid"))
            print(f"✅ Resultado mostrado con {len(result)} filas.")

    if args.nat_lang is not None:

        # Carga la clave de API de OpenAI desde la configuración    
        apikey = Config().get_value("openai.apikey")
        print(f"🔑 Clave de API de OpenAI: {'✅ Encontrada' if apikey else '❌ No especificada'}")
        if not apikey:
            print("No se ha especificado la clave de API de OpenAI. Por favor, configura 'openai.apikey' en el fichero de configuración.", file=sys.stderr)
            sys.exit(1)

        sql = generate_query(apikey, "schemas/PincelPreDB", "Módulos del ciclo formativo de grado superior de Desarrollo de Aplicaciones Web del curso 2024")
        print(f"⚙️ Consulta generada:", sql)

if __name__ == "__main__":
    main()