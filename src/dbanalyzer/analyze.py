import sys
import json
from openai import OpenAI

from dbschema.database import Database
from dbschema.table import Table

from dbanalyzer.functions import tools, list_tables, get_table_schema, get_table_data

def call_function(fn_name, database, args):
    print(f"⚙️ Invocando la función '{fn_name}' con los argumentos: {args}")
    if fn_name == "list_tables":
        return json.dumps(list_tables(database))
    if fn_name == "get_table_schema":
        return get_table_schema(database, **args).model_dump_json(exclude_none=True)
    if fn_name == "get_table_data":
        return json.dumps(get_table_data(database, **args))

def analyze_table(apikey: str, database: Database, table_name: str) -> Table:
    print(f"🔍 Iniciando análisis semántico de la tabla '{table_name}'...")

    client = OpenAI(api_key=apikey)
    model = "gpt-4.1-mini"
    temperature = 0.1 if model.startswith("gpt") else None

    with open("src/dbanalyzer/prompt.md", "r", encoding="utf-8") as file:
        instructions = file.read()

    input_messages = [
        {
            "role": "developer", 
            "content": instructions
        },
        {
            "role": "user", 
            "content": f"""
                Haz un análisis semántico de la tabla '{table_name}' y proporciona su esquema comentado. 
                Añade ejemplos significativos de datos a los comentarios de cada campo, si es posible,
                y en caso de que sean referencias a otras tablas, muestra algún campo relevante de la otra tabla,
                el valor de algún campo descriptivo. Si necesitas información de tablas relacionadas, puedes 
                ir encadenando más llamadas a funciones, de modo que puedas ir recabando información de tablas 
                relacionadas. Aprovecha los comentarios que  ya tengan tablas y columnas el esquema, mejorándolos. 
                Recuerda que puedes obtener el esquema y  datos de cualquier tabla relacionada para ayudarte a 
                interpretar los campos de '{table_name}'.
            """
        },
    ]

    response = None
    while True:
        print("➡️ Enviando mensaje al modelo...")
        response = client.responses.parse(
            model=model,
            input=input_messages,
            tools=tools,
            tool_choice="auto",  # o "required" si quieres forzar tools
            text_format=Table,
            temperature=temperature,
        )
        print(f"⬅️ Respuesta recibida (outputs: {len(response.output)}, output_text: {"✅" if response.output_text else "❌"})")

        # Procesa tool calls si existen (nos quedamos sólo con los que son de tipo function_call)
        tool_calls = [tc for tc in response.output if getattr(tc, "type", None) == "function_call"]
        if not tool_calls:
            # Si no hay tool calls, salimos
            break

        for tool_call in tool_calls:
            name = tool_call.name
            args = json.loads(tool_call.arguments)
            result = call_function(name, database, args)
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
        print("✅ Análisis semántico completado con éxito.")
        table = response.output_parsed
        table.schemaName = database.name
    except json.JSONDecodeError as e:
        print(f"❌ Error al procesar la respuesta del modelo: {e}", file=sys.stderr)
        print("🤖 La respuesta del modelo no es un JSON válido:")
        print(response.output_text)
        raise e
    
    return table
