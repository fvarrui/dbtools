import os
import re

from dbutils import __module_name__, __module_description__, __module_version__
from dbschema.table import Table
from dbschema.column import Column
from dbschema.foreign_key import ForeignKey
from dbschema.reference import Reference
from dbschema.schema import Schema

from urllib.parse import unquote
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
    :param filter: Filtro opcional para los nombres de las tablas (expresión regular).
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
            default=unquote(column['data_default']) if column['data_default'] != 'null' else None,
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
