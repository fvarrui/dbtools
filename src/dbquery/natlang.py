import os
import sys
import json
from openai import OpenAI, RateLimitError

from dbschema.table import Table

from dbanalyzer.functions import tools, call_function

tools = [
    {
        "type": "function",
        "name": "index_schema",
        "description": "Genera un índice de las tablas a partir del esquema en el directorio especificado.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_table_by_name",
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
        "name": "ask_for_help",
        "description": "Solicita ayuda al usuario para resolver dudas sobre el esquema de la base de datos.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Pregunta que se desea hacer al usuario para aclarar dudas sobre el esquema de la base de datos.",
                },
            },
            "required": ["question"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]

def call_function(fn_name, schema_dir, args):
    print(f"⚙️ Invocando la función '{fn_name}' con los argumentos: {args}")
    if fn_name == "index_schema":
        return index_schema(schema_dir, **args)
    if fn_name == "list_tables":
        return get_table_by_name(schema_dir, **args)
    if fn_name == "ask_for_help":
        return ask_for_help(**args)

def ask_for_help(question: str) -> str:
    """
    Solicita ayuda al usuario para resolver dudas sobre el esquema de la base de datos.
    
    :param question: Pregunta que se desea hacer al usuario para aclarar dudas sobre el esquema de la base de datos.
    :return: Respuesta del usuario a la pregunta formulada.
    """
    print(f"❓ Pregunta al usuario: {question}")
    response = input(f"Por favor, responde a la pregunta '{question}': ")
    return response

def index_schema(schema_dir: str) -> list[dict]:
    index = {}
    for table_file in os.listdir(schema_dir):
        table = Table.load(os.path.join(schema_dir, table_file))
        index[table.name] = table.comment
    print(f"🗒️ Índice de esquemas generado con las tablas:", json.dumps(index, indent=4))
    return index


def get_table_by_name(schema_dir: str, table_name: str) -> Table:
    table_path = os.path.join(schema_dir, f"{table_name}.json")
    if not os.path.exists(table_path):
        raise FileNotFoundError(f"La tabla '{table_name}' no existe en el directorio '{schema_dir}'.")    
    return Table.load(table_path)


def generate_query(apikey: str, schema_dir: str, prompt: str) -> Table:
    print(f"🔍 Generando consulta para el prompt '{prompt}'...")

    client = OpenAI(api_key=apikey)
    model = "gpt-4o-mini" 
    temperature = 0.15 if model.startswith("gpt") else None

    with open("src/dbquery/prompt.md", "r", encoding="utf-8") as file:
        instructions = file.read()

    input_messages = [
        {
            "role": "developer", 
            "content": instructions
        },
        {
            "role": "user", 
            "content": f"Necesito la consulta SQL pra obtener la siguiente información: {prompt}"
        },
    ]

    response = None
    while True:

        try:
            print(f"➡️ Enviando mensaje al modelo...")
            response = client.responses.create(
                model=model,
                input=input_messages,
                tools=tools,
                tool_choice="auto",  # o "required" si quieres forzar tools
                temperature=temperature,
            )
        except RateLimitError as e:
            print(f"⚠️ Se ha excedido el límite de tokens por minuto. Esperando 1 minuto para reintentar... ({e})", file=sys.stderr)
            break
        except Exception as e:
            print(f"❌ Error al enviar el mensaje al modelo: {e}", file=sys.stderr)
            raise e
            
        # Comprueba si la respuesta contiene tool calls
        tool_calls = [tc for tc in response.output if getattr(tc, "type", None) == "function_call"]

        print(f"⬅️ Respuesta recibida (outputs: {len(response.output)}, output_text: {"✅" if response.output_text else "❌"}, tool_calls: {len(tool_calls)} )")

        # Procesa tool calls si existen (nos quedamos sólo con los que son de tipo function_call)
        if not tool_calls:
            break   # Si no hay tool calls, salimos

        for tool_call in tool_calls:
            name = tool_call.name
            args = json.loads(tool_call.arguments)
            result = json.dumps(call_function(name, schema_dir, args))
            print(f"\t✅ Llamada a función {name} con argumentos {args} completada con éxito.")
            # Añade el resultado como function_call_output
            input_messages.append(tool_call)
            input_messages.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(result),
            })

    # Cuando ya no hay tool calls, procesa la respuesta final
    try:        
        # Coge sólo la última respuesta
        print("✅ Generación de la consulta SQL completada con éxito.")
        sql = response.output_text
    except json.JSONDecodeError as e:
        print(f"❌ Error al procesar la respuesta del modelo: {e}", file=sys.stderr)
        print(response.output_text)
        raise e
    
    return sql
