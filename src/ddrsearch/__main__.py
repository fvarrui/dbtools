import os
import re
import argparse
import json
import sys

from dbutils import __module_name__, __module_description__, __module_version__
from dbutils.customhelp import CustomHelpFormatter
from dbschema.table import Table
from dbschema.column import Column
from dbschema.foreign_key import ForeignKey
from dbschema.reference import Reference
from dbschema.schema import Schema

from pathlib import Path
from bs4 import BeautifulSoup

def normalize_text(text: str) -> str:
    if not text:
        return None
    return text.replace('\xa0', ' ')  # Reemplaza los espacios no rompibles

def get_ddr_table(soup : BeautifulSoup, index: int) -> list[dict]:
    """
    Obtiene una tabla del Data Dictionary Report a partir de su índice.
    :param soup: Objeto BeautifulSoup que representa el contenido del Data Dictionary Report.
    :param index: Índice de la tabla a obtener (0 para columnas, 1 para restricciones, etc.).
    :return: Lista de diccionarios con los datos de la tabla.
    """
    html_div = soup.find('div', {'id': f'Master.{index}'})
    if not html_div:
        return []
    html_table = html_div.find('table')
    html_rows = html_table.find_all('tr')
    headers = [ th.get_text(strip=True).lower() for th in html_table.find_all('th') ]
    data = []
    for row in html_rows[1:]: # Ignora la primera fila (encabezados)
        cols = [ td.get_text(strip=True) for td in row.find_all('td') ]
        register = {}
        for i, header in enumerate(headers):
            if i < len(cols):
                register[header] = normalize_text(cols[i])
            else:
                register[header] = None
        data.append(register)
    return data

def get_table_names(ddr_report_dir, filter=None):
    """
    Obtiene los nombres de las tablas del Data Dictionary Report.
    
    :param ddr_report_dir: Directorio donde se encuentra el Data Dictionary Report.
    :return: Lista de nombres de tablas.
    """
    table_names = []
    if os.path.exists(ddr_report_dir):
        for filename in os.listdir(ddr_report_dir):
            if filename.endswith('.html') and (filter is None or re.match(filter, filename)):
                table_name = Path(filename).stem
                table_names.append(table_name)  # Elimina la extensión del archivo de la tabla
    return table_names

def find_columns(soup : BeautifulSoup) -> list[ForeignKey]:
    columns = get_ddr_table(soup, 0)
    cols = []
    for column in columns:
        col = Column(
            name=column['column_name'],
            type=column['data_type'],
            nullable=column['nullable'] == 'Yes',
            comment=normalize_text(column['comments']) if column['comments'] != 'null' else None,
            default=column['data_default'] if column['data_default'] != 'null' else None,
        )
        cols.append(col)
    return cols

def find_primary_keys(soup : BeautifulSoup) -> list[ForeignKey]:
    """
    Encuentra las claves primarias de la tabla a partir del Data Dictionary Report.
    :param soup: Objeto BeautifulSoup que representa el contenido del Data Dictionary Report.
    :return: Lista de claves primarias encontradas.
    """
    constraints = get_ddr_table(soup, 1)
    indices = get_ddr_table(soup, 8)
    pkConstraints = [constraint for constraint in constraints if constraint['constraint_type'] == 'Primary_Key']
    pks = []
    for pkConstraint in pkConstraints:
        # Busca el índice asociado a la clave primaria
        index = next((indice for indice in indices if indice['index_name'] == pkConstraint['constraint_name']), None)
        if index:
            pks.append(index['columns'])
    return pks

def find_foreign_keys(soup : BeautifulSoup) -> list[ForeignKey]:
    """
    Encuentra las claves foráneas de la tabla a partir del Data Dictionary Report.
    :param soup: Objeto BeautifulSoup que representa el contenido del Data Dictionary Report.
    :return: Lista de claves foráneas encontradas.
    """
    foreignKeys = get_ddr_table(soup, 9)
    fks = []
    for foreignKey in foreignKeys:
        fk = ForeignKey(
            column=foreignKey['columnas_propias'],
            reference=Reference(
                table=foreignKey['tabla_apuntada'],
                column=foreignKey['columnas_ajenas'],
            )
        )
        fks.append(fk)
    return fks

def table_from_ddr(table_file) -> Table:
    """
    Crea un objeto de tabla a partir del archivo del Data Dictionary Report.
    
    :param table_file: Ruta al archivo del Data Dictionary Report.
    :return: Objeto de tabla con la información extraída.
    """
    table_name = Path(table_file).stem
    print(f"Procesando tabla: {table_name}")

    with open(table_file, 'r', encoding='cp1252') as f:
        soup = BeautifulSoup(f, 'html.parser')

    details = get_ddr_table(soup, 6)
    if not details:
        return None
    comment = next((detail['value'] for detail in details if detail['name'] == 'COMMENTS'), None) 
    return Table(
        name=table_name,
        comment=normalize_text(comment) if comment != 'null' else None,
        columns=find_columns(soup),
        primary_keys=find_primary_keys(soup),
        foreign_keys=find_foreign_keys(soup),
    )

def schema_from_ddr(ddr_report_dir, filter = None) -> Schema:
    """
    Crea una lista de objetos de tabla a partir del Data Dictionary Report.
    
    :param ddr_report_dir: Directorio donde se encuentra el Data Dictionary Report.
    :return: Lista de objetos de tabla con la información extraída.
    """
    tables = []
    table_names = get_table_names(ddr_report_dir, filter)
    for table_name in table_names:
        file_path = os.path.join(ddr_report_dir, table_name + '.html')
        if os.path.exists(file_path):
            table = table_from_ddr(file_path)
            if table:
                tables.append(table)
    return Schema(tables=tables)

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
    commands.add_argument('--schema', metavar='TABLE_FILTER', nargs='?', const='.*', help=f'Expresión regulra de las tablas del Data Dictionary Report')
    commands.add_argument('--table', metavar='TABLE_NAME', nargs='?', const='', help=f'Nombre de la tabla a buscar en el Data Dictionary Report')
    commands.add_argument('--list-tables', action='store_true', help=f'Lista los nombres de las tablas del Data Dictionary Report')
    
    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--ddr-report', metavar='DIR', nargs='?', const='', help=f'Directorio del Data Dictionary Report')
    options.add_argument('-fk', '--foreign-keys', action='store_true', help='Busca sólo las claves foráneas')
    options.add_argument('--filter', metavar='REGEXP', nargs='?', const='', help='Filtra los resultados que contengan el texto especificado')
    options.add_argument('--json', metavar='OUTPUT_FILE', nargs='?', const='', help='Exporta el resultado en formato JSON')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return

    if args.schema is not None:
        print("Generando esquema para las tablas del Data Dictionary Report...")
        if args.ddr_report:
            ddr_report_dir = args.ddr_report
            filter = args.schema
            print(f"Directorio del Data Dictionary Report: {ddr_report_dir}")
            print(f"Filtro de tablas: {filter}")
            schema = schema_from_ddr(args.ddr_report, filter)
            json_output = json.dumps(schema.model_dump(), indent=4, ensure_ascii=False)
            with open(args.json, 'w', encoding='utf-8') if args.json else sys.stdout as output_file:
                output_file.write(json_output)

    if args.list_tables:
        print("Listando las tablas del Data Dictionary Report...")
        if args.ddr_report:
            print(f"Directorio del Data Dictionary Report: {args.ddr_report}")
            filter = rf"{args.filter}" if args.filter else None
            table_names = get_table_names(args.ddr_report, filter)
            if table_names:
                print(f"Tablas encontradas (filtro: {filter}):")
                for table in table_names:
                    print(f"- {table}")
            else:
                print("No se encontraron tablas en el Data Dictionary Report.")
        else:
            print("No se ha especificado un directorio para el Data Dictionary Report.")
    
    if args.table is not None:
        table_name = args.table.strip()
        print(f"Buscando la tabla '{table_name}' en el Data Dictionary Report...")
        if args.ddr_report:
            file_path = os.path.join(args.ddr_report, table_name + '.html')
            if not os.path.exists(file_path):
                print(f"No se encontró la tabla: {table_name}")
                return
            print(f"Procesando archivo: {file_path}")
            table = table_from_ddr(file_path)
            if table:

                if args.json is not None:
                    json_output = json.dumps(table.model_dump(), indent=4, ensure_ascii=False)
                    with open(args.json, 'w', encoding='utf-8') if args.json else sys.stdout as output_file:
                        output_file.write(json_output)
                else:
                    table.print()
                    print("Primary keys:", table.primary_keys)
                    print("Foreign keys:", table.foreign_keys)

            else:
                print(f"No se pudo procesar la tabla: {table_name}", file=sys.stderr)

        else:
            print("No se ha especificado un directorio para el Data Dictionary Report.")
        if args.foreign_keys:
            print("Buscando sólo claves foráneas.")

if __name__ == '__main__':
    main()