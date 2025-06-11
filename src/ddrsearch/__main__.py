import os
import argparse
import json
import sys

from dbutils import __module_name__, __module_description__, __module_version__
from dbutils.customhelp import CustomHelpFormatter
from ddrsearch.ddr import schema_from_ddr, table_from_ddr, get_table_names

def table(table_name: str, ddr_report_dir: str = None, json_file: str = None):
    table_name = table_name.strip()
    print(f"Buscando la tabla '{table_name}' en el Data Dictionary Report...")
    if not ddr_report_dir:
        print("No se ha especificado un directorio para el Data Dictionary Report.")
        return
    if not os.path.exists(ddr_report_dir):
        print(f"El directorio especificado no existe: {ddr_report_dir}")
        return
    print(f"Directorio del Data Dictionary Report: {ddr_report_dir}")
    file_path = os.path.join(ddr_report_dir, table_name + '.html')
    if not os.path.exists(file_path):
        print(f"No se encontró la tabla: {table_name}")
        return
    print(f"Procesando archivo: {file_path}")
    table = table_from_ddr(file_path)
    if not table:
        print(f"No se pudo procesar la tabla: {table_name}", file=sys.stderr)
        return  
    if json_file is not None:
        json_output = json.dumps(table.model_dump(), indent=4, ensure_ascii=False)
        with open(json_file, 'w', encoding='utf-8') if json_file else sys.stdout as output_file:
            output_file.write(json_output)
    else:
        table.print()
        print("Primary keys:", table.primary_keys)
        print("Foreign keys:", table.foreign_keys)


def list_tables(filter: str = r'.*', ddr_report_dir: str = None, json_file: str = None):
    print("Listando las tablas del Data Dictionary Report...")
    if not ddr_report_dir:
        print("No se ha especificado un directorio para el Data Dictionary Report.")
        return
    if not os.path.exists(ddr_report_dir):
        print(f"El directorio especificado no existe: {ddr_report_dir}")
        return
    print(f"Directorio del Data Dictionary Report: {ddr_report_dir} (filtro: {filter})")
    table_names = get_table_names(ddr_report_dir, filter)
    if not table_names:
        print("No se encontraron tablas en el Data Dictionary Report.")
    if json_file is not None:
        json_output = json.dumps(table_names, indent=4, ensure_ascii=False)
        with open(json_file, 'w', encoding='utf-8') if json_file else sys.stdout as output_file:
            output_file.write(json_output)
    else:
        print(f"Tablas encontradas (filtro: {filter}):")
        for table in table_names:
            print(f"- {table}")


def schema(filter: str = r'.*', ddr_report_dir: str = None, json_file: str = None):
    print("Generando esquema para las tablas del Data Dictionary Report...")
    if not ddr_report_dir:
        print("No se ha especificado un directorio para el Data Dictionary Report.")
        return
    if not os.path.exists(ddr_report_dir):
        print(f"El directorio especificado no existe: {ddr_report_dir}")
        return
    ddr_report_dir = ddr_report_dir.strip()
    print(f"Directorio del Data Dictionary Report: {ddr_report_dir}")
    print(f"Filtro de tablas: {filter}")
    schema = schema_from_ddr(ddr_report_dir, filter)
    json_output = json.dumps(schema.model_dump(), indent=4, ensure_ascii=False)
    with open(json_file, 'w', encoding='utf-8') if json_file else sys.stdout as output_file:
        output_file.write(json_output)            


def main():

    # define el parser
    parser = argparse.ArgumentParser(
        prog=__module_name__, 
        description=f"{__module_description__} (v{__module_version__})", 
        epilog='¡Todo por Doramas!', 
        add_help=False, 
        formatter_class=CustomHelpFormatter
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('--schema', metavar='TABLE_FILTER', nargs='?', const='.*', help=f'Genera el esquema de la base de datos de las tablas del Data Dictionary Report. El filtro es una expresión regular que se aplica a los nombres de las tablas. Por defecto, se incluyen todas las tablas.')
    commands.add_argument('--table', metavar='TABLE_NAME', help=f'Muestra información de la tabla indicada del Data Dictionary Report. El nombre de la tabla debe coincidir con el nombre del archivo HTML sin la extensión.')
    commands.add_argument('--list-tables', metavar='TABLE_FILTER', nargs='?', const='^.*$', help=f'Lista los nombres de las tablas del Data Dictionary Report. El filtro es una expresión regular que se aplica a los nombres de las tablas. Si no se especifica, se listan todas las tablas.')
    
    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--ddr-report', metavar='DIR', help=f'Directorio del Data Dictionary Report')
    options.add_argument('--json', metavar='OUTPUT_FILE', nargs='?', const='', help='Exporta el resultado en formato JSON. Si no se especifica un archivo, se imprime en la salida estándar.')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return

    if args.schema is not None:
        schema(args.schema, args.ddr_report, args.json)

    if args.list_tables:
        list_tables(args.list_tables, args.ddr_report, args.json)
    
    if args.table is not None:
        table(args.table, args.ddr_report, args.json)

if __name__ == '__main__':
    main()