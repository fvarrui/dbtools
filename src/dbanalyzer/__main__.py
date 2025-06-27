import os
import sys
import time
import argparse

from dbanalyzer import __module_name__, __module_description__, __module_version__, logger
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
    logger.info(f"🔑 Clave de API de OpenAI: {'✅ Encontrada' if apikey else '❌ No especificada'}")
    if not apikey:
        logger.error("No se ha especificado la clave de API de OpenAI. Por favor, configura 'openai.apikey' en el fichero de configuración.")
        sys.exit(1)

    # Carga la configuración y conecta a la base de datos
    database = None
    if args.db_url or args.db_name:
        # Si no se ha especificado una URL de conexión a la base de datos, intenta obtenerla de las variables de entorno
        try:
            db_url = args.db_url or DBIni.load().get_url(args.db_name)
        except Exception as e:
            logger.error(f"No se ha podido obtener la URL de conexión a la base de datos", e)
            sys.exit(1)

        # Conecta a la base de datos
        try:
            database = Database(db_url)
            database.connect()
            logger.info(f"👍 Conectado a la base de datos '{database.server}\{database.name}'")
        except Exception as e:
            logger.error(f"¡No se ha podido conectar a la base de datos!", e)
            sys.exit(1)

    # Verifica si el directorio de salida existe, si no, lo crea
    output_dir = None
    if args.output is not None:
        output_dir = os.path.join(args.output, database.name)
        if not os.path.exists(output_dir) or not os.path.isdir(output_dir):                
            logger.warning(f"⚠️ El directorio de salida '{output_dir}' no existe. Creando el directorio...")
            os.makedirs(output_dir, exist_ok=True)

    # Analizar una tabla específica
    if args.analyze_table:

        # Verifica si se ha especificado una base de datos
        if database is None:
            logger.error("No se ha especificado una base de datos. Por favor, utiliza --db-url o --db-name para conectarte a una base de datos.")
            sys.exit(1)

        # Análisis semántico de la tabla especificada
        table_name = args.analyze_table
        table_name = analyze_table(apikey, database, table_name)

        # Verifica si se ha obtenido una tabla válida
        if not table_name:
            logger.error(f"❌ No se ha podido analizar la tabla '{table_name}'. Asegúrate de que existe en la base de datos.")
            sys.exit(1)
        
        # Imprime el resultado del análisis semántico
        table_name.print()

        # Si se ha especificado un directorio de salida, guarda el resultado en un archivo JSON        
        json_file = os.path.join(output_dir, f"{table_name}.json") if output_dir else None
        if json_file and os.path.exists(json_file):
            table_name.save(json_file)
            logger.info(f"📒 Resultado del análisis semántico de {table_name} guardado en {json_file}")

    # Analizar el esquema de la base de datos
    elif args.analyze_schema:

        # Verifica si se ha especificado una base de datos
        if database is None:
            logger.error("No se ha especificado una base de datos. Por favor, utiliza --db-url o --db-name para conectarte a una base de datos.")
            sys.exit(1)

        # Recupera el esquema de la base de datos
        prefix = args.analyze_schema or None
        table_names = database.list_tables(filter=prefix)

        logger.info(f"🔍 Iniciando análisis semántico de {len(table_names)} tablas con prefijo '{prefix}'...")
        logger.info(f"📋 Tablas a analizar: {'Todas' if not prefix else table_names if table_names else 'Ninguna'}")

        stats = {
            "total_tables": len(table_names),
            "analyzed_tables": 0,
            "skipped_tables": 0,
            "errors": []
        }

        # Recorre las tablas y realiza el análisis semántico de todas ellas
        for table_name in table_names:
            logger.info(f"\n🔍 Analizando la tabla '{table_name}'...")

            try:

                # Verifica si el archivo JSON ya existe
                json_file = os.path.join(output_dir, f"{table_name}.json") if output_dir else None
                if json_file and os.path.exists(json_file):
                    logger.warning(f"⚠️ El archivo JSON '{json_file}' ya existe.")
                    stats["skipped_tables"] += 1
                    continue

                # Realiza el análisis semántico de la tabla
                analyzed_table = analyze_table(apikey, database, table_name)                
                logger.info(f"✅ Análisis de la tabla '{table_name}' completado.")
                stats["analyzed_tables"] += 1
                
                # Si hay un directorio de salida, guarda el resultado en un archivo JSON
                if json_file:
                    analyzed_table.save(json_file)
                    logger.info(f"📒 Resultado del análisis semántico de {table_name} guardado en {json_file}")
                
                # Sino, imprime el resultado del análisis semántico en la consola
                else:
                    analyzed_table.print()

            except Exception as e:

                logger.error(f"❌ No se pudo analizar la tabla '{table_name}'", e)
                stats["errors"] += [{
                    "table": table_name,
                    "error": str(e)
                }]

        logger.info(f"\n🔍 Análisis semántico de la base de datos '{database.name}' completado:")
        logger.info(f"- Total de tablas analizadas: {stats['total_tables']}")
        logger.info(f"- Tablas analizadas correctamente: {stats['analyzed_tables']}")
        logger.info(f"- Tablas omitidas: {stats['skipped_tables']}")
        logger.info(f"- Errores encontrados: {len(stats['errors'])}")

        if stats["errors"]:
            logger.info("\n🔴 Errores encontrados durante el análisis:")
            for error in stats["errors"]:
                logger.info(f"\t- Tabla '{error['table']}': {error['error']}")
        else:
            logger.info("✅ No se encontraron errores durante el análisis 🕺🕺🕺.")


    ellapsed_time = time.time() - start
    print(f"Tiempo de ejecución: {ellapsed_time:.2f} segundos")

if __name__ == "__main__":
    main()
