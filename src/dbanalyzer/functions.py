import inspect
import json
from typing import get_type_hints

from sqlalchemy import MetaData, text
from dbschema.database import Database
from dbschema.table import Table

tools = [
    #{
    #    "type": "function",
    #    "name": "list_tables",
    #    "description": "Lista los nombres de las tablas en la base de datos.",
    #    "parameters": {
    #        "type": "object",
    #        "properties": {},
    #        "additionalProperties": False,
    #    },
    #    "strict": True,
    #},
    {
        "type": "function",
        "name": "get_table_schema",
        "description": "Obtiene el esquema de una tabla específica en la base de datos.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Nombre de la tabla para la cual se desea obtener el esquema.",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_table_data",
        "description": "Obtiene un subconjunto de datos de una tabla específica en la base de datos.",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Nombre de la tabla de la cual se desean obtener los datos.",
                },
            },
            "required": ["table_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def list_tables(database: Database) -> list[str]:
    """
    Lista los nombres de las tablas en la base de datos.
        :param database: Objeto Database que representa la base de datos.
        :return: Lista de nombres de tablas.
    """
    print("🗒️ Listando tablas en la base de datos...")
    return database.list_tables()


def get_table_schema(database: Database, name: str) -> Table:
    """
    Obtiene el esquema de una tabla específica en la base de datos.
        :param database: Objeto Database que representa la base de datos.
        :param name: Nombre de la tabla para la cual se desea obtener el esquema.
        :return: Objeto Table que representa el esquema de la tabla.
    """
    try:
        print(f"🗒️ Obteniendo esquema de la tabla '{name}'...")
        metadata = MetaData()
        metadata.reflect(bind=database.engine, only=[name])
        for table_name, table_metadata in metadata.tables.items():
            if table_name.lower() == name.lower():
                return Table.from_metadata(table_metadata)
        return None
    except Exception as e:
        print(f"❌ Error al obtener el esquema de la tabla '{name}': {e}")
        return None


def get_table_data(database: Database, table_name: str, limit: int = 10) -> list[dict]:
    """
    Obtiene los datos de una tabla específica en la base de datos.
        :param database: Objeto Database que representa la base de datos.
        :param table_name: Nombre de la tabla de la cual se desean obtener los datos.
        :param limit: Número máximo de filas a recuperar (opcional, por defecto 10).
        :return: Lista de diccionarios representando las filas de la tabla.
    """
    print(f"🗒️ Obteniendo datos de la tabla '{table_name}' con un límite de {limit} filas...")
    stmt = text(
        f"""
        SELECT TOP {limit} *
        FROM {table_name}
        WHERE 0.10 >= CAST(CHECKSUM(NEWID(), TMS) & 0x7fffffff AS float) / CAST (0x7fffffff AS int)
        ORDER BY NEWID()
        """
    )
    return database.execute(stmt)


def generar_tool_schema(func):
    sig = inspect.signature(func)
    hints = get_type_hints(func)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        tipo = hints.get(name, str)
        json_type = python_type_to_json_type(tipo)
        properties[name] = {"type": json_type}
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "function",
        "name": func.__name__,
        "description": func.__doc__ or "Sin descripción.",
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required
        },
        "strict": True
    }

def python_type_to_json_type(t):
    if t == str:
        return "string"
    elif t == int:
        return "integer"
    elif t == float:
        return "number"
    elif t == bool:
        return "boolean"
    elif t == list:
        return "array"
    elif t == dict:
        return "object"
    else:
        return "object"

# 🧪 Ejemplo de función
def get_user_info(user_id: int, verbose: bool = False):
    """Devuelve la información de un usuario dado su ID."""

# 🔧 Generar tool schema automáticamente
#print(json.dumps(generar_tool_schema(get_user_info), indent=2))
#print(json.dumps(generar_tool_schema(list_tables), indent=2))
#print(json.dumps(generar_tool_schema(get_table_data), indent=2))
#print(json.dumps(generar_tool_schema(get_table_schema), indent=2))

