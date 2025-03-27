import os
import sys
import json
import argparse

from tabulate import tabulate
from getpass import getpass

from dbschema import __module_name__, __module_description__, __module_version__
from dbschema.database import Database

from dbconn.dbini import get_connection_url, has_undefined_password, replace_password_placeholder, DEFAULT_INI_FILE

def resolve_dburl(args):
    """
    Resuelve la URL de conexión a la base de datos a partir de los argumentos de línea de comandos y las variables de entorno.
    :args: Argumentos de línea de comandos
    :return: URL de conexión a la base de datos    
    """
    # Busca la URL de conexión a la base de datos en los argumentos de línea de comandos o en las variables de entorno
    dburl = args.dburl or os.getenv("DBTOOLS_CONNECTION_URL")
    
    # Si aún así no hay URL de conexión a la base de datos, intenta obtenerla del fichero de configuración
    if not dburl:
        # Si no se ha especificado una URL de conexión a la base de datos, intenta obtenerla del fichero de configuración
        try:
            dburl = get_connection_url(DEFAULT_INI_FILE, args.db)
            # Si la URL de conexión requiere una contraseña, se solicita al usuario
            if has_undefined_password(dburl):
                password = args.password or getpass("Introduce la contraseña: ")
                dburl = replace_password_placeholder(dburl, password)
        except Exception as e:
            print("No se ha podido obtener la URL de conexión a la base de datos:", e, file=sys.stderr)
            sys.exit(1)

    return dburl

def main():

        # declara un HelpFormatter personalizado para reemplazar el texto 'usage:' por 'Uso:'
    class CustomHelpFormatter(argparse.HelpFormatter):
        def add_usage(self, usage, actions, groups, prefix='Uso: '):
            if usage is not argparse.SUPPRESS:
                args = usage, actions, groups, prefix
                self._add_item(self._format_usage, args)

    # define el parser
    parser = argparse.ArgumentParser(prog=__module_name__, description=f"{__module_description__} (v{__module_version__})", epilog='¡Un gran esquema conlleva una gran responsabilidad!', add_help=False, formatter_class=CustomHelpFormatter)

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
    options.add_argument('--dburl', metavar='URL', nargs='?', help='URL de conexión a la base de datos')
    options.add_argument('--db', metavar='DB', nargs='?', help=f"Nombre de la base de datos en el fichero {DEFAULT_INI_FILE}")
    options.add_argument('--json', metavar='FILE', nargs='?', help='Guarda el resultado en un fichero JSON')
    options.add_argument('--password', metavar='PASSWORD', nargs='?', help=f"Contraseña de la base de datos")

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return

    # Si no se ha especificado una URL de conexión a la base de datos, intenta obtenerla de las variables de entorno
    dburl = resolve_dburl(args)  

    # Conecta a la base de datos
    try:
        database = Database(dburl)
        database.connect()
        print("Conectado a la base de datos:", dburl)
    except Exception as e:
        print(f"No se ha podido conectar a la base de datos {dburl}:", e, file=sys.stderr)
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
        if args.json:

            # Añade información de la base de datos junto con el esquema
            result = {
                "database": {
                    "name": database.name,
                    "server": database.server,
                    "port": database.port
                },
                "schema": schema.model_dump()
            }
         
            # Convertir el resultado en JSON
            print("Convirtiendo el resultado en JSON")
            schema_json = json.dumps(result, indent=4)

            # Guardar el resultado en un fichero
            if len(args.json) > 0:
                print(f"Guardando el resultado en el fichero: {args.json}")
                with open(args.json, "w") as f:
                    f.write(schema_json)
            # Mostrar el resultado en formato JSON en la consola
            else:
                print(schema_json)

        else:

            # Mostrar tablas del esquema en la consola
            for table in schema.tables:
                print()
                table.print()

if __name__ == "__main__":
    main()