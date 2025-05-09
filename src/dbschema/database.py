from urllib.parse import urlparse
from sqlalchemy import create_engine, inspect, MetaData

from dbschema.schema import Schema

class Database:

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
        self.engine.connect()
        self.inspector = inspect(self.engine)

    def get_schema(self, prefix=None) -> Schema:
        """
        Recupera el esquema de la base de datos
        Args:
            prefix: Prefijo para las tablas a incluir
        Returns:
            Esquema de la base de datos
        """

        # Recuperando la lista de tablas de la base de datos con el prefijo indicado
        table_names = self.list_tables(filter=prefix) if prefix else None

        # Cargar la estructura de la base de datos existente
        print("- Tablas a incluir:", table_names or "Todas")
        metadata = MetaData()
        metadata.reflect(bind=self.engine, only=table_names)

        # Generar el esquema de la base de datos
        return Schema.from_metadata(metadata, table_names)

    def list_tables(self, filter=None) -> list[str]:
        """
        Recupera la lista de tablas de la base de datos
        Args:
            filter: Filtro para las tablas
        Returns:
            Lista de nombres de tablas
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
        Args:
            filter: Filtro para las vistas
        Returns:
            Lista de nombres de vistas
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
