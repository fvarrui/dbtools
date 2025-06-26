from urllib.parse import urlparse
from sqlalchemy import create_engine, inspect, MetaData, Select
from sqlalchemy.engine import Connection, CursorResult

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
