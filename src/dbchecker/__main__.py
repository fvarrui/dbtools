import json
import argparse
import sys

from dbchecker import __module_name__, __module_description__, __module_name__, __module_version__
from dbchecker.database import Database

def main():

    # declara un HelpFormatter personalizado para reemplazar el texto 'usage:' por 'Uso:'
    class CustomHelpFormatter(argparse.HelpFormatter):
        def add_usage(self, usage, actions, groups, prefix='Uso: '):
            if usage is not argparse.SUPPRESS:
                args = usage, actions, groups, prefix
                self._add_item(self._format_usage, args)

    # define el parser
    parser = argparse.ArgumentParser(prog=__module_name__, description=f"{__module_description__} (v{__module_version__})", epilog='¡Soy la solución a tu amargura!', add_help=False, formatter_class=CustomHelpFormatter)

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda y termina')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('--list-tables', metavar='PREFIX', nargs='?', const='', help='Listar todas las tablas (con o sin prefijo)')
    commands.add_argument('--list-views', metavar='PREFIX', nargs='?', const='', help='Listar todas las vistas (con o sin prefijo)')
    commands.add_argument('--show-table', metavar='TABLE', help='Mostrar estructura de la tabla', type=str)
    commands.add_argument('--show-view', metavar='VIEW', help='Mostrar estructura de la vista', type=str)
    commands.add_argument('--check', metavar='PREFIX', nargs='?', const='', help='Busca inconsistencias en la base de datos')

    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--json', action='store_true', help='Devuelve el resultado en formato JSON')
    #options.add_argument('--location', metavar='LOCATION', help='Ubicación para la búsqueda de empresas (p.ej. "Santa Cruz de Tenerife, España")', type=str)
    #options.add_argument('--latlng', metavar='LATLNG', help='Ubicación para la búsqueda de empresas en formato "latitud,longitud"', type=str)
    #options.add_argument('--radius', metavar='RADIUS', help='Radio en kilómetros para la búsqueda', default=5.0, type=float)
    #options.add_argument('--csv', metavar='OUTPUT', nargs='?', const="output.csv", help='Fichero de salida en formato CSV', type=str)
    #options.add_argument('--excel', metavar='OUTPUT', nargs='?', const="output.xlsx", help='Fichero de salida en formato XLSX', type=str)
    #options.add_argument('--apikey', metavar='KEY', help='Clave de API de Google Places (si no se especifica, se buscará en las variables de entorno)', type=str)

    # parsea los argumentos
    args = parser.parse_args()

    # lógica según las opciones
    if args.help:
        parser.print_help()
        return

    # connect to sql server database
    db = Database(DRIVER, SERVER, DB_NAME)
    db.connect()

    if args.show_table:

        table_name = args.show_table
        
        if not db.is_table(table_name):
            print(f"La tabla '{table_name}' no existe", file=sys.stderr)
            sys.exit(1)

        table = db.get_table(table_name)

        # print in json format
        if args.json:
            print(json.dumps(table, default=lambda o: o.__dict__, indent=4))
        else:
            table.print()

    elif args.show_view:

        view_name = args.show_view

        if not db.is_view(view_name):
            print(f"La vista'{view_name}' no existe", file=sys.stderr)
            sys.exit(1)

        view = db.get_view(view_name)

        if args.json:
            print(json.dumps(view, default=lambda o: o.__dict__, indent=4))
        else:
            view.print()

    elif not args.list_tables is None:
        
        prefix = args.list_tables
        views = db.list_tables(prefix)
        for table in views:
            print(table)
        print("\nSe han encontrado", len(views), "tablas")

    elif not args.list_views is None:
        
        prefix = args.list_views
        views = db.list_views(prefix)
        for table in views:
            print(table)
        print("\nSe han encontrado", len(views), "vistas")

    elif not args.check is None:

        prefix = args.check
        print(f"buscando inconsistencias en la base de datos usando prefijo {prefix}...")
        # TODO implementar la lógica de chequeo de la base de datos

    db.disconnect()

if __name__ == "__main__":
    main()
