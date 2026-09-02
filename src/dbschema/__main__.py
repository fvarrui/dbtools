import os
import sys
import json
import argparse

from tabulate import tabulate

from dbschema import __module_name__, __module_description__
from dbschema.database import Database
from dbutils.customhelp import CustomHelpFormatter
from dbutils.dbini import DB_INIFILE, DBIni

def main():

    # define el parser
    parser = argparse.ArgumentParser(
        prog=__module_name__,
        description=__module_description__,
        epilog='¡Un gran esquema conlleva una gran responsabilidad!',
        add_help=False,
        formatter_class=CustomHelpFormatter
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('--schema', metavar='FILTER', nargs='?', const='', help='Genera el esquema de la base de datos. Si se especifica un prefijo, sólo se incluirán las tablas que empiecen por ese prefijo. La opción --json genera el resultado en un formato JSON.')
    commands.add_argument('--list-tables', metavar='FILTER', nargs='?', const='', help='Listar todas las tablas')
    commands.add_argument('--list-views', metavar='FILTER', nargs='?', const='', help='Listar todas las vistas')
    commands.add_argument('--search', metavar='TERM', help='Buscar tablas o columnas que contengan el término de búsqueda en el esquema especificado con la opción --json.')
    
    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--db-url', metavar='URL', help='URL de conexión a la base de datos')
    options.add_argument('--db-name', metavar='DB', help=f"Nombre de la base de datos en el fichero {DB_INIFILE}")
    options.add_argument('--json', metavar='FILE', nargs='?', const='', help='Entrada o salida en formato JSON. Si no se especifica un fichero, se utiliza la entrada y salida estándar.')
    options.add_argument('--output', metavar='DIR', nargs='?', const='.', help='Directorio de salida para los ficheros generados. Por defecto, el directorio actual. Combinado con --schema --json (sin fichero), genera un JSON por cada tabla.')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return

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

    # Listar las vistas
    if args.list_views is not None:
        if database is None:
            print("No se ha especificado una base de datos. Por favor, utiliza --db-url o --db-name para conectarte a una base de datos.")
            sys.exit(1)
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
        if database is None:
            print("No se ha especificado una base de datos. Por favor, utiliza --db-url o --db-name para conectarte a una base de datos.")
            sys.exit(1)
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

    # Generar el esquema de la base de datos
    if args.schema is not None:

        # Si no se ha especificado una base de datos, muestra un mensaje de error
        if database is None:
            print("❌ No se ha especificado una base de datos. Por favor, utiliza --db-url o --db-name para conectarte a una base de datos.")
            sys.exit(1)

        prefix = args.schema

        print(f"⚙️ Generando esquema de la base de datos...")
        if prefix:
            print(f"\t- Incluyendo sólo tablas con prefijo: {prefix}")
        else:
            print(f"\t- Incluyendo todas las tablas")

        schema = database.get_schema(prefix=prefix)

        if schema is None:
            print("❌ No se ha podido generar el esquema de la base de datos. Por favor, comprueba que la base de datos contiene tablas.", file=sys.stderr)
            sys.exit(1)

        # Guardar en un fichero o mostrar por pantalla
        if args.json is not None:

            # Caso 1: --json FILE → un único fichero con database + schema
            if len(args.json) > 0:
                result = {
                    "database": database.__dict__(),
                    "schema": schema.model_dump()
                }
                with open(args.json, "w") as f:
                    f.write(json.dumps(result, indent=4))
                print(f"\n✅ Esquema guardado en: {args.json}")

            # Caso 2: --json (sin fichero) + --output DIR → un JSON por tabla
            elif args.output is not None:
                os.makedirs(args.output, exist_ok=True)
                for table in schema.tables:
                    file_path = os.path.join(args.output, f"{table.name}.json")
                    with open(file_path, "w") as f:
                        f.write(json.dumps(table.model_dump(), indent=4))
                    print(f"  ✅ {file_path}")
                print(f"\n✅ {len(schema.tables)} tablas exportadas a: {args.output}")

            # Caso 3: --json sin fichero ni --output → stdout
            else:
                result = {
                    "database": database.__dict__(),
                    "schema": schema.model_dump()
                }
                print(f"\n{json.dumps(result, indent=4)}")

        else:

            # Mostrar tablas del esquema en la consola
            for table in schema.tables:
                print()
                table.print()

    if args.search is not None:
        print(f"Pendiente de implementar la búsqueda de '{args.search}' en el esquema (proximamente) ... ⚠️")

if __name__ == "__main__":
    main()