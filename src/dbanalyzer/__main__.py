from sqlalchemy import create_engine, MetaData, inspect
import pandas as pd

class DataExtractor:
    def __init__(self, db_url):
        """Inicializa el extractor con la conexión a la base de datos."""
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.inspector = inspect(self.engine)

    def get_foreign_keys(self, table_name):
        """Obtiene claves foráneas definidas explícitamente."""
        foreign_keys = self.inspector.get_foreign_keys(table_name)
        relations = {}
        for fk in foreign_keys:
            referenced_table = fk['referred_table']
            local_column = fk['constrained_columns'][0]
            foreign_column = fk['referred_columns'][0] if 'referred_columns' in fk else 'id'
            relations[referenced_table] = (local_column, foreign_column)
        return relations

    def detect_implicit_relations(self, table):
        """Detecta relaciones implícitas en la base de datos."""
        columns = self.inspector.get_columns(table)
        relations = {}

        for col in columns:
            col_name = col['name']
            if col_name.endswith("_id") or col_name in ["id_cliente", "id_producto", "id_pedido"]:
                potential_table = col_name.replace("_id", "")
                
                # Verificar si existe una tabla con ese nombre en plural o singular
                for t in self.metadata.tables:
                    if potential_table in t or potential_table.rstrip("s") in t:
                        relations[t] = (col_name, "id")  # Suponemos que el campo relacionado es 'id'
                        break

        return relations

    def extract_related_data(self, table, record_id, depth=2):
        """
        Extrae un registro y todos sus datos relacionados, detectando relaciones explícitas e implícitas.
        - table: Nombre de la tabla principal.
        - record_id: ID del registro principal.
        - depth: Niveles de relaciones a explorar (por defecto 2).
        """
        result = {}
        visited_tables = set()
        self._recursive_extraction(result, table, record_id, depth, visited_tables)
        return result

    def _recursive_extraction(self, result, table, record_id, depth, visited_tables):
        """Función recursiva que extrae datos relacionados a distintos niveles."""
        if depth == 0 or table in visited_tables:
            return

        visited_tables.add(table)
        conn = self.engine.connect()
        
        # Extraer el registro principal
        query = f"SELECT * FROM {table} WHERE id = :record_id"
        df = pd.read_sql(query, conn, params={"record_id": record_id})
        result[table] = df.to_dict(orient="records")

        # Buscar tablas relacionadas (explícitas + implícitas)
        explicit_relations = self.get_foreign_keys(table)
        implicit_relations = self.detect_implicit_relations(table)

        all_relations = {**explicit_relations, **implicit_relations}

        for related_table, (local_col, foreign_col) in all_relations.items():
            query = f"SELECT * FROM {related_table} WHERE {foreign_col} IN (SELECT {local_col} FROM {table} WHERE id = :record_id)"
            df_related = pd.read_sql(query, conn, params={"record_id": record_id})

            if not df_related.empty:
                result[related_table] = df_related.to_dict(orient="records")
                for rel_record in df_related[foreign_col]:
                    self._recursive_extraction(result, related_table, rel_record, depth-1, visited_tables)

        conn.close()

# 📌 Uso del extractor con detección automática de relaciones
db_url = "postgresql://usuario:password@localhost:5432/mi_base"
extractor = DataExtractor(db_url)

# Extraer datos de un cliente con ID 5 y sus relaciones (hasta 2 niveles de profundidad)
data = extractor.extract_related_data("clientes", 5, depth=2)

import json
print(json.dumps(data, indent=4))  # Muestra los datos en formato JSON
