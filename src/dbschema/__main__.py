import sys
import json
import argparse

from tabulate import tabulate

from dbschema import __module_name__, __module_description__, __module_version__
from dbschema.database import Database

from dbutils.customhelp import CustomHelpFormatter

from dbutils.dbini import DB_INIFILE, DBIni

def main():

    # define el parser
    parser = argparse.ArgumentParser(
        prog=__module_name__, 
        description=f"{__module_description__} (v{__module_version__})", 
        epilog='¡Un gran esquema conlleva una gran responsabilidad!', 
        add_help=False, 
        formatter_class=CustomHelpFormatter
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('--schema', metavar='FILTER', nargs='?', const='', help='Genera el esquema de la base de datos')
    commands.add_argument('--list-tables', metavar='FILTER', nargs='?', const='', help='Listar todas las tablas')
    commands.add_argument('--list-views', metavar='FILTER', nargs='?', const='', help='Listar todas las vistas')

    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--db-url', metavar='URL', nargs='?', help='URL de conexión a la base de datos')
    options.add_argument('--db-name', metavar='DB', nargs='?', help=f"Nombre de la base de datos en el fichero {DB_INIFILE}")
    options.add_argument('--json', metavar='FILE', nargs='?', const='', help='Guarda el resultado en un fichero JSON')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return

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
        print("Conectado a la base de datos...")
    except Exception as e:
        print(f"¡No se ha podido conectar a la base de datos!", e, file=sys.stderr)
        sys.exit(1)

    # Listar las vistas
    if args.list_views is not None:
        print("Listando vistas ...")
        if args.list_views:
            print(f"- Filtrado vistas que contengan: {args.list_views}\n")
        view_names = database.list_views(filter=args.list_views)
        if args.json:
            with open(args.json, "w") as f:
                f.write(json.dumps(view_names, indent=4))
        else:
            headers = [ "VIEW_NAME" ]
            data = [ [ view_name ] for view_name in view_names ]
            print(tabulate(data, headers=headers, tablefmt="grid"))
        print(f"\n{len(view_names)} vistas encontradas")
        return

    # Listar las tablas
    if args.list_tables is not None:
        print("Listando tablas ...")
        if args.list_tables:
            print(f"- Filtrado tablas que contengan: {args.list_tables}\n")
        table_names = database.list_tables(filter=args.list_tables)
        if args.json:
            with open(args.json, "w") as f:
                f.write(json.dumps(table_names, indent=4))
        else:
            headers = [ "TABLE_NAME" ]
            data = [ [ table_name ] for table_name in table_names ]
            print(tabulate(data, headers=headers, tablefmt="grid"))
        print(f"\n{len(table_names)} tablas encontradas")
        return

    # Generar el esquema
    if args.schema is not None:

        prefix = args.schema

        # Generar el esquema de la base de datos

        print(f"Generando esquema de la base de datos ...")
        if prefix:
            print(f"- Incluyendo sólo tablas con prefijo: {prefix}")
        else:
            print(f"- Incluyendo todas las tablas")

        schema = database.get_schema(prefix=prefix)

        # Guardar en un fichero o mostrar por pantalla
        if args.json is not None:

            # Añade información de la base de datos junto con el esquema
            result = {
                "database": database.__dict__(),
                "schema": schema.model_dump()
            }
         
            # Convertir el resultado en JSON
            result_json = json.dumps(result, indent=4)

            # Guardar el resultado en un fichero
            if len(args.json) > 0:
                with open(args.json, "w") as f:
                    f.write(result_json)
                print(f"\nEsquema guardado en: {args.json}")
            # Mostrar el resultado en formato JSON en la consola
            else:
                print(f"\n{result_json}")

        else:

            # Mostrar tablas del esquema en la consola
            for table in schema.tables:
                print()
                table.print()

if __name__ == "__main__":
    main()