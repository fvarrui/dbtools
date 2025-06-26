import json
from openai import OpenAI

from dbschema.database import Database
from dbschema.table import Table
from dbutils.config import Config
from dbutils.dbini import DBIni

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
    temperature = 0.4 if model.startswith("gpt") else None

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
                Si necesitas información de tablas relacionadas, puedes ir encadenando más llamadas a funciones,
                de modo que puedas ir recabando información de tablas relacionadas si la necesitas. Los campos 
                que ya tengan comentarios en la tabla, deben dejarse como están, añadiendo tu interpretación entre 
                paréntesis. Recuerda que puedes obtener el esquema y datos de cualquier tabla relacionada para 
                ayudarte a interpretar los campos de '{table_name}'.
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
    result = json.loads(response.output_text)    
    print("✅ Análisis semántico completado con éxito.")
    table = Table.model_validate(result)
    table.schemaName = database.name
    return table

#dburl = DBIni.load().get_url("PincelPreDB")

#print(f"⚙️ Conectando a la base de datos: {dburl}...")
#database = Database(dburl)
#database.connect()
#print("✅ Conexión establecida!")

#table = get_table_schema(database, "PEC_EstudiosGeneral")
#json = table.model_dump_json(indent=4, exclude_none=True)
#print(json)

#data = get_table_data(database, "GEN_TEspDocentes", limit=5)
#print(json.dumps(data, indent=4))

#print(database.list_tables())

#table_name = "PEC_TAsignas"
#result_table = analyze_table(apikey, database, table_name)
#output = f"schemas/{table_name}.json"
#print(f"📒 Guardando el resultado del análisis semántico de {table_name} en {output}")
#with open(output, "w", encoding="utf-8") as f:
#    json.dump(result_table.model_dump(), f, indent=4, ensure_ascii=False)
#result_table.print()
