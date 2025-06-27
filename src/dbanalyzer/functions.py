import sys
import inspect
import json
from typing import get_type_hints

from sqlalchemy import MetaData, text
from dbschema.database import Database
from dbschema.table import Table

tools = [
    #{
    #    "type": "function",
    #    "name": "table_exists",
    #    "description": "Verifica si una tabla específica existe en la base de datos.",
    #    "parameters": {
    #        "type": "object",
    #        "properties": {
    #            "name": {
    #                "type": "string",
    #                "description": "Nombre de la tabla a verificar.",
    #            },
    #        },
    #        "required": ["name"],
    #        "additionalProperties": False,
    #    },
    #    "strict": True,
    #},
    {
        "type": "function",
        "name": "list_tables",
        "description": "Lista los nombres de las tablas en la base de datos.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
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

def call_function(fn_name, database, args):
    print(f"⚙️ Invocando la función '{fn_name}' con los argumentos: {args}")
    if fn_name == "table_exists":
        return table_exists(database, **args)
    if fn_name == "list_tables":
        return json.dumps(list_tables(database))
    if fn_name == "get_table_schema":
        table = get_table_schema(database, **args)
        return table.model_dump_json(exclude_none=True) if table else None
    if fn_name == "get_table_data":
        data = get_table_data(database, **args)
        return json.dumps(data) if data else None

def table_exists(database: Database, name: str) -> bool:
    """
    Verifica si una tabla específica existe en la base de datos.
        :param database: Objeto Database que representa la base de datos.
        :param name: Nombre de la tabla a verificar.
        :return: True si la tabla existe, False en caso contrario.
    """
    print(f"🗒️ Verificando si la tabla '{name}' existe en la base de datos...")
    return database.table_exists(name)

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
        return database.get_table(name)
    except Exception as e:
        print(f"❌ Error al obtener el esquema de la tabla '{name}': {e}", file=sys.stderr)
        return None


def get_table_data(database: Database, table_name: str, limit: int = 10) -> list[dict]:
    """
    Obtiene los datos de una tabla específica en la base de datos.
        :param database: Objeto Database que representa la base de datos.
        :param table_name: Nombre de la tabla de la cual se desean obtener los datos.
        :param limit: Número máximo de filas a recuperar (opcional, por defecto 10).
        :return: Lista de diccionarios representando las filas de la tabla.
    """
    try:
        print(f"🗒️ Obteniendo datos de la tabla '{table_name}' con un límite de {limit} filas...")
        table = database.get_table(table_name)  # Verifica si la tabla existe
        columns_list = [ f"{col.name}" for col in table.columns ] if table else []
        columns_str = (", " + ", ".join(columns_list)) if columns_list else ""
        # Si la tabla tiene una columna TMS, la usamos para ordenar
        stmt = text(
            f"""
            SELECT TOP {limit} *
            FROM {table_name}
            WHERE 0.10 >= CAST(CHECKSUM(NEWID(){columns_str}) & 0x7fffffff AS float) / CAST (0x7fffffff AS int)
            ORDER BY NEWID()
            """
        )
        return database.execute(stmt)
    except Exception as e:
        print(f"❌ Error al obtener los datos de la tabla '{table_name}': {e}")
        return []

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

# 🔧 Generar tool schema automáticamente
#print(json.dumps(generar_tool_schema(list_tables), indent=2))
#print(json.dumps(generar_tool_schema(get_table_data), indent=2))
#print(json.dumps(generar_tool_schema(get_table_schema), indent=2))

