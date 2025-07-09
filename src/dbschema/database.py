from urllib.parse import urlparse
from sqlalchemy import create_engine, inspect, MetaData, Select, text
from sqlalchemy.engine import Connection, CursorResult

from dbschema.table import Table
from dbschema.schema import Schema
from utils.encoding import serializable_dict

class Database:

    connection : Connection = None

    def __init__(self, dburl: str):
        parsedurl = urlparse(dburl)
        self.dburl = dburl
        self.server = parsedurl.hostname
        self.port = parsedurl.port
        self.name = parsedurl.path[1:]
        self.type = parsedurl.scheme.split("+")[0]
    
    def connect(self):
        """
        Conecta a la base de datos y recupera el inspector
        """
        self.engine = create_engine(self.dburl)
        self.connection = self.engine.connect()
        self.inspector = inspect(self.engine)

    def get_schema(self, prefix=None) -> Schema:
        """
        Recupera el esquema de la base de datos
            :param prefix: Prefijo para las tablas a incluir
            :returns: Esquema de la base de datos
        """

        # Recuperando la lista de tablas de la base de datos con el prefijo indicado
        table_names = self.list_tables(filter=prefix) if prefix else None

        if not table_names:
            print(f"- Tablas a incluir: ❌ No se han encontrado tablas con el prefijo '{prefix}'")
            return None

        # Cargar la estructura de la base de datos existente
        print("- Tablas a incluir: ✅", table_names or "Todas")
        metadata = MetaData()
        metadata.reflect(bind=self.engine, only=table_names)

        # Generar el esquema de la base de datos
        return Schema.from_metadata(metadata, table_names)
    
    def get_table(self, name: str) -> Table:
        """
        Recupera el esquema de una tabla específica en la base de datos
            :param name: Nombre de la tabla a recuperar
            :returns: Esquema de la tabla
        """
        metadata = MetaData()
        metadata.reflect(bind=self.engine, only=[name])
        for table_name, table_metadata in metadata.tables.items():
            if table_name.lower() == name.lower():
                return Table.from_metadata(table_metadata)
        return None
    
    def table_exists(self, name: str) -> bool:
        """
        Verifica si una tabla existe en la base de datos
            :param name: Nombre de la tabla a verificar
            :returns: True si la tabla existe, False en caso contrario
        """
        return name in self.inspector.get_table_names()

    def list_tables(self, filter=None) -> list[str]:
        """
        Recupera la lista de tablas de la base de datos
            :param filter: Filtro para las tablas
            :returns: Lista de nombres de tablas
        """
        tables = []
        for table_name in self.inspector.get_table_names():
            if filter and not filter in table_name:
                continue
            tables.append(table_name)
        return tables

    def list_views(self, filter=None) -> list[str]:
        """
        Recupera la lista de vistas de la base de datos
            :param filter: Filtro para las vistas
            :returns: Lista de nombres de vistas
        """
        views = []
        for view_name in self.inspector.get_view_names():
            if filter and not filter in view_name:
                continue
            views.append(view_name)
        return views

    def __dict__(self) -> dict:
        return {
            "type": self.type,
            "name": self.name,
            "server": self.server,
            "port": self.port
        }
    
    def count_rows(self, table_name: str) -> int:
        """
        Cuenta el número de filas de una tabla
            :param table_name: Nombre de la tabla a contar
            :returns: Número de filas de la tabla
        """
        query = text(f"SELECT COUNT(*) as total FROM {table_name}")
        result = self.execute(query)
        return result[0]['total'] if result else 0
    
    def execute(self, query : Select | str) -> list[dict]:
        """
        Ejecuta una consulta SQL en la base de datos
            :param query: Consulta SQL a ejecutar
            :returns: Resultado de la consulta
        """
        result : CursorResult = self.connection.execute(query)
        result = result.mappings().all()
        result = [ serializable_dict(dict(row)) for row in result ]
        return result
