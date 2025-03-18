import os
import sys
import json
import argparse

from dbschema import __module_name__, __module_description__, __module_version__
from dbconn.dbini import get_connection_url, has_undefined_password, replace_password_placeholder

from sqlalchemy import create_engine, MetaData, inspect
from urllib.parse import urlparse
from tabulate import tabulate
from getpass import getpass

CONFIG_FILE = "dbtools.ini"

def generate_schema(metadata, prefix=None):
    schema = {}
    for table_name, table in metadata.tables.items():
        if prefix and not table_name.startswith(prefix):
            continue
        schema[table_name] = {
            "comment": table.comment,  # Comentario de la tabla
            "columns": {
                col.name: {
                    "type": str(col.type),
                    "comment": col.comment  # Comentario de la columna
                }
                for col in table.columns
            },
            "primary_key": [col.name for col in table.primary_key.columns],
            "foreign_keys": {
                fk.parent.name: {"references": fk.column.table.name, "column": fk.column.name}
                for fk in table.foreign_keys
            },
        }
    return schema

def list_tables(metadata, prefix=None):
    tables = []
    for table_name in metadata.tables.keys():
        if prefix and not table_name.startswith(prefix):
            continue
        tables.append({
            "name": table_name,
            "comment": metadata.tables[table_name].comment or ""
        })
    return tables

def list_views(engine, prefix=None):
    inspector = inspect(engine)
    views = []
    for view_name in inspector.get_view_names():
        if prefix and not view_name.startswith(prefix):
            continue
        views.append(view_name)
    return views

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
    commands.add_argument('--schema', metavar='PREFIX', nargs='?', const='', help='Genera el esquema de la base de datos')
    commands.add_argument('--list-tables', metavar='PREFIX', nargs='?', const='', help='Listar todas las tablas')
    commands.add_argument('--list-views', metavar='PREFIX', nargs='?', const='', help='Listar todas las vistas')
    commands.add_argument('--show-table', metavar='TABLE', help='Mostrar estructura de la tabla', type=str)
    commands.add_argument('--show-view', metavar='VIEW', help='Mostrar estructura de la vista', type=str)

    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--dburl', metavar='URL', nargs='?', help='URL de conexión a la base de datos')
    options.add_argument('--db', metavar='DB', nargs='?', help=f"Nombre de la base de datos en el fichero {CONFIG_FILE}")
    options.add_argument('--password', metavar='PASSWORD', nargs='?', help=f"Contraseña de la base de datos")
    options.add_argument('--json', action='store_true', help='Devuelve el resultado en formato JSON')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return

    # Si no se ha especificado una URL de conexión a la base de datos, intenta obtenerla de las variables de entorno
    dburl = args.dburl or os.getenv("DBTOOLS_CONNECTION_URL")

    if not dburl:
        # Si no se ha especificado una URL de conexión a la base de datos, intenta obtenerla del fichero de configuración
        try:
            dburl = get_connection_url(CONFIG_FILE, args.db)
            if has_undefined_password(dburl):
                password = args.password or getpass("Introduce la contraseña: ")
                dburl = replace_password_placeholder(dburl, password)
        except Exception as e:
            print("No se ha podido obtener la URL de conexión a la base de datos:", e, file=sys.stderr)
            sys.exit(1)

    # Comprueba que se ha especificado una URL de conexión a la base de datos
    if not dburl:
        print(f"Debe especificar una URL de conexión a la base de datos o una configuración en {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)  

    # Conecta a la base de datos
    try:
        engine = create_engine(dburl)
        engine.connect()
    except Exception as e:
        print("No se ha podido conectar a la base de datos:", e, file=sys.stderr)
        sys.exit(1)

    # Listar las vistas
    if args.list_views is not None:
        views = list_views(engine, prefix=args.list_views)
        print("\n".join(views))
        return

    # Cargar la estructura de la base de datos existente
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Listar las tablas
    if args.list_tables is not None:
        tables = list_tables(metadata, prefix=args.list_tables)
        if args.json:
            print(json.dumps(tables, indent=4))
        else:
            headers = [ "TABLE_NAME", "COMMENT" ]
            data = [ [ table["name"], table["comment"] ] for table in tables]
            print(tabulate(data, headers=headers, tablefmt="grid"))
        return

    # Generar el esquema
    if args.schema is not None:
        # Generar el esquema de la base de datos
        db_schema = generate_schema(metadata, prefix=args.schema)

        # Añade información de la conexión a la base de datos
        parsedurl = urlparse(dburl)
        db_schema = {
            "database": {
                "server": parsedurl.hostname,
                "port": parsedurl.port,
                "database": parsedurl.path[1:]
            },
            "tables": db_schema
        }

        # Convertirlo en JSON
        schema_json = json.dumps(db_schema, indent=4)
        print(schema_json)
        return
    
    print(args)

if __name__ == "__main__":
    main()