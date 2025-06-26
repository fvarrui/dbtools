import os
import sys
import time
import json
import argparse

from dbanalyzer import __module_name__, __module_description__, __module_version__
from dbanalyzer.analyze import analyze_table

from dbschema.database import Database

from dbutils.dbini import DB_INIFILE, DBIni
from dbutils.customhelp import CustomHelpFormatter
from dbutils.config import Config

    
def main():

    # define el parser
    parser = argparse.ArgumentParser(
        prog=__module_name__, 
        description=f"{__module_description__} (v{__module_version__})", 
        epilog='¡IA-stoy aquí para hacer lo que tú no quieres hacer!',
        add_help=False, 
        formatter_class=CustomHelpFormatter
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('--analyze-table', metavar='TABLE_NAME', help='Realiza el análisis semántico de la tabla especificada.')
    commands.add_argument('--analyze-schema', metavar='FILTER', nargs='?', const='', help='Analiza todas las tablas con el prefijo indicado, o todas las tablas de la base de datos si no se especifica un prefijo. La opción --json genera el resultado en un formato JSON.')
    
    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--db-url', metavar='URL', nargs='?', help='URL de conexión a la base de datos')
    options.add_argument('--db-name', metavar='DB', nargs='?', help=f"Nombre de la base de datos en el fichero {DB_INIFILE}")
    options.add_argument('--output', metavar='DIR', nargs='?', const='.', help='Directorio de salida para guardar los resultados del análisis semántico. Si no se especifica, se guardará en el directorio actual.')

    # Parsea los argumentos
    args = parser.parse_args()

    start = time.time()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return

    # Carga la clave de API de OpenAI desde la configuración    
    apikey = Config().get_value("openai.apikey")
    print(f"🔑 Clave de API de OpenAI: {'✅ Encontrada' if apikey else '❌ No especificada'}")
    if not apikey:
        print("No se ha especificado la clave de API de OpenAI. Por favor, configura 'openai.apikey' en el fichero de configuración.", file=sys.stderr)
        sys.exit(1)

    # Carga la configuración y conecta a la base de datos
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
            print(f"Conectado a la base de datos '{database.name}'")
        except Exception as e:
            print(f"¡No se ha podido conectar a la base de datos!", e, file=sys.stderr)
            sys.exit(1)    

    # Analizar una tabla específica
    if args.analyze_table:

        # Verifica si se ha especificado una base de datos
        if database is None:
            print("No se ha especificado una base de datos. Por favor, utiliza --db-url o --db-name para conectarte a una base de datos.")
            sys.exit(1)

        # Análisis semántico de la tabla especificada
        table_name = args.analyze_table
        table = analyze_table(apikey, database, table_name)

        # Verifica si se ha obtenido una tabla válida
        if not table:
            print(f"❌ No se ha podido analizar la tabla '{table_name}'. Asegúrate de que existe en la base de datos.")
            sys.exit(1)
        
        # Imprime el resultado del análisis semántico
        table.print()

        if args.output is not None:
            output_dir = args.output
            if not os.path.exists(output_dir) or not os.path.isdir(output_dir):
                print(f"⚠️ El directorio de salida '{output_dir}' no existe. Creando el directorio...")
                os.makedirs(output_dir, exist_ok=True)
            json_file = f"{output_dir}/{table_name}.json"
            print(f"📒 Guardando el resultado del análisis semántico de {table_name} en {json_file}")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(table.model_dump(), f, indent=4, ensure_ascii=False)

    ellapsed_time = time.time() - start
    print(f"Tiempo de ejecución: {ellapsed_time:.2f} segundos")

if __name__ == "__main__":
    main()
