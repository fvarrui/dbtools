import os
import re
import sys

from dbutils import __module_name__, __module_description__, __module_version__
from dbschema.table import Table
from dbschema.column import Column
from dbschema.foreign_key import ForeignKey
from dbschema.reference import Reference
from dbschema.schema import Schema

from urllib.parse import unquote
from pathlib import Path
from bs4 import BeautifulSoup
from pptree import Node

CACHED_TABLES = {}

def normalize_text(text: str) -> str:
    if not text:
        return None
    return text.replace('\xa0', ' ')  # Reemplaza los espacios no rompibles

def get_ddr_data(soup : BeautifulSoup, tabIndex: int) -> list[dict]:
    """
    Obtiene una tabla del Data Dictionary Report a partir de su índice.
    :param soup: Objeto BeautifulSoup que representa el contenido del Data Dictionary Report.
    :param index: Índice de la tabla a obtener (0 para columnas, 1 para restricciones, etc.).
    :return: Lista de diccionarios con los datos de la tabla.
    """
    html_div = soup.find('div', {'id': f'Master.{tabIndex}'})
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

def get_table_names(ddr_report_dir, filter=None) -> list[str]:
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

def get_tables(ddr_report_dir, filter=None) -> list[dict]:
    tables = []
    if os.path.exists(ddr_report_dir):
        for filename in os.listdir(ddr_report_dir):
            if filename.endswith('.html') and (filter is None or re.match(filter, filename)):
                table_name = Path(filename).stem
                table_file = os.path.join(ddr_report_dir, filename)
                # Cargamos el archivo HTML de la tabla y lo parseamos con BeautifulSoup
                with open(table_file, 'r', encoding='cp1252') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                # Obtenemos los detalles de la tabla
                details = get_ddr_data(soup, 6)
                if not details:
                    continue
                # Extraemos el comentario y propietario (esquema)
                comment = next((detail['value'] for detail in details if detail['name'] == 'COMMENTS'), None)
                tables.append({
                    'name': table_name,
                    'comment': normalize_text(comment) if comment != 'null' else None,
                })
    return tables

def find_columns(soup : BeautifulSoup) -> list[ForeignKey]:
    columns = get_ddr_data(soup, 0)
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
    constraints = get_ddr_data(soup, 1)
    indices = get_ddr_data(soup, 8)
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
    foreignKeys = get_ddr_data(soup, 9)
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

def table_from_ddr(table_file, quiet=False) -> Table:
    """
    Crea un objeto de tabla a partir del archivo del Data Dictionary Report.
    
    :param table_file: Ruta al archivo del Data Dictionary Report.
    :return: Objeto de tabla con la información extraída.
    """
    table_name = Path(table_file).stem
    # Si la tabla ya está en caché, la retornamos directamente
    if table_name in CACHED_TABLES:
        return CACHED_TABLES[table_name]
    # Modo silencioso: no imprime mensajes de procesamiento
    if not quiet:
        print(f"Procesando tabla: {table_name}") 
    # Cargamos el archivo HTML de la tabla y lo parseamos con BeautifulSoup
    with open(table_file, 'r', encoding='cp1252') as f:
        soup = BeautifulSoup(f, 'html.parser')
    # Obtenemos los detalles de la tabla
    details = get_ddr_data(soup, 6)
    if not details:
        return None
    # Extraemos el comentario y propietario (esquema)
    comment = next((detail['value'] for detail in details if detail['name'] == 'COMMENTS'), None) 
    owner = next((detail['value'] for detail in details if detail['name'] == 'OWNER'), None)
    table = Table(
        name=table_name,
        comment=normalize_text(comment) if comment != 'null' else None,
        columns=find_columns(soup),
        primary_keys=find_primary_keys(soup),
        foreign_keys=find_foreign_keys(soup),
        schemaName=owner if owner != 'null' else None
    )
    # Guardamos la tabla en caché
    CACHED_TABLES[table_name] = table
    # Devolvemos el objeto de tabla
    return table

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


def table_uses_tables(table_name, ddr_report_dir, level=0, visited=[], parent=None, foreignKey=None) -> Node:
    """
    Crea un nodo de árbol que representa una tabla y sus relaciones con otras tablas.
    :param table_name: Nombre de la tabla a procesar.
    :param ddr_report_dir: Directorio donde se encuentra el Data Dictionary Report.
    :param level: Nivel de profundidad en el árbol (para propósitos de indentación).
    :param visited: Lista de tablas ya visitadas para evitar ciclos infinitos.
    :param parent: Nodo padre en el árbol (para construir la jerarquía).
    :param foreignKey: Clave foránea que relaciona esta tabla con otra (opcional).
    :return: Nodo de árbol que representa la tabla y sus relaciones.
    """
    # Si no se especifica un foreignKey, creamos un nodo para la tabla directamente (nodo raíz)
    if not foreignKey:
        table_node = Node(table_name, parent=parent)
    else:
        table_node = Node(f".{foreignKey.column} → {foreignKey.reference.table}", parent=parent)

    # Evitamos ciclos infinitos
    if table_name in visited:
        return table_node
    visited.append(table_name)

    # Extraemos información de la tabla del Data Dictionary Report
    table_file = os.path.join(ddr_report_dir, table_name + '.html')
    table = table_from_ddr(table_file, True)

    # Si no se pudo procesar la tabla, retornamos el nodo sin hijos
    if not table:
        return table_node

    # Recorremos las claves foráneas de la tabla y creamos nodos para las tablas referenciadas
    for fk in table.foreign_keys:
        referenced_table = fk.reference.table
        table_uses_tables(
            table_name=referenced_table,
            ddr_report_dir=ddr_report_dir,
            level=level + 1,
            visited=visited,
            parent=table_node,
            foreignKey=fk
        )

    return table_node

def tables_used_by_table(table_name, ddr_report_dir, level=0, visited=[], parent=None, schema=None, limit=sys.maxsize) -> Node:
    
    if not schema:
        table_node = Node(table_name, parent=parent)
    else:
        table_node = Node(f"[{schema}].{table_name}", parent=parent)

    # Evitamos ciclos infinitos
    if table_name in visited:
        return table_node    
    visited.append(table_name)

    if level >= limit:
        return table_node

    # Extraemos información de la tabla del Data Dictionary Report
    table_file = os.path.join(ddr_report_dir, table_name + '.html')

    if not os.path.exists(table_file):
        return table_node
    
    table = table_from_ddr(table_file, True)

    if not schema:
        schema = table.schemaName

    # Si no se pudo procesar la tabla, retornamos el nodo sin hijos
    if not table:
        return table_node

    # Obtiene las tablas usadas por la tabla actual
    with open(table_file, 'r', encoding='cp1252') as f:
        soup = BeautifulSoup(f, 'html.parser')
    data = get_ddr_data(soup, 10)
    
    for used_table in data:
        pointedTable = used_table['tabla_ajena']
        outterSchema = used_table['esquema_ajeno']
        tables_used_by_table(
            table_name=pointedTable,
            ddr_report_dir=ddr_report_dir,
            level=level + 1,
            visited=visited,
            parent=table_node,
            schema=outterSchema if outterSchema != schema else None,
            limit=limit
        )

    return table_node

