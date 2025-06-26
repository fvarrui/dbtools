import sys
import json
import io
from openai import OpenAI
from os import path

from dbschema.schema import Schema
from dbschema.table import Table
from dbschema.database import Database
from sqlalchemy import MetaData

def analyze(apikey: str, schema: Schema):

    # Inicializar el cliente de OpenAI
    client = OpenAI(api_key=apikey)

    # Recupera el asistente especializado en bases de datos y SQL
    assistant = client.beta.assistants.retrieve(
        assistant_id="asst_cNhjPcFXhk0jLPmkW7LienS7"
    )
    print("🤖 Asistente especializado en bases de datos y SQL recuperado:", assistant.name)

    # Sube el esquema de la base de datos
    schema_reduced = schema.reduce()
    schema_json = io.BytesIO(json.dumps(schema_reduced, indent=None, separators=(",", ":")).encode('utf-8'))
    schema_json.name = "schema.json"
    uploaded_schema = client.files.create(
        file=schema_json,       # archivo JSON del esquema de la base de datos
        purpose="assistants",   # contexto para el asistente,
    )
    print("📄 Esquema subido:", uploaded_schema.id)

    print("😀 Iniciando análisis del esquema de la base de datos...")
    for table in schema.tables:

        # Comienza el análisis de la tabla
        print("\n📤 Iniciando análisis de la tabla:", table.name)

        output_file = f"schemas/pec_{table.name}_analysis.json"
        if path.exists(output_file):
            print(f"\t⚠️ El archivo {output_file} ya existe. Se omitirá el análisis de la tabla {table.name}.")
            continue

        # Crea un hilo de conversación
        thread = client.beta.threads.create()
        print(f"\t🗣️ Hilo de conversación creado para analizar tabla {table.name}:", thread.id)

        # Añadir un mensaje del usuario al hilo para analizar la tabla
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Realiza análisis semántico de la tabla {table.name} en el esquema de la base de datos y devuelve el JSON.",
            attachments=[
                { 
                    "file_id": uploaded_schema.id, 
                    "tools": [{"type": "file_search"}]
                }
            ],
        )
        print(f"\t📤 Mensaje creado solicitando análisis de la tabla {table.name}:", message.id)

        # Intenta ejecutar el hilo de conversación con el asistente hasta 3 veces
        MAX_TRIES = 3
        tries = 1
        run = None
        while tries <= MAX_TRIES and (run is None or run.status != "completed"):
            # Ejecutar el hilo de conversación con el asistente
            print(f"\t🎲 Ejecución del asistente {assistant.name} para la tabla {table.name}... (intento {tries} de {MAX_TRIES})")
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id, 
                assistant_id=assistant.id
            )
            tries += 1
        
        if run.status == "completed":
            print("\t✅ Ejecución completada con éxito")
            # Recuperar el mensaje del asistente
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            # prints last message
            for message in messages.data:
                if message.role == "assistant":
                    table_analysis = message.content[0].text.value
                    print(f"\t📥 Recibida respuesta del asistente {assistant.name} acerca de la tabla {table.name}:", message.id)
                    # print(table_analysis.strip())
                    table_json = json.loads(table_analysis)
                    with open(output_file, "w", encoding='utf-8') as f:
                        json.dump(table_json, f, indent=4, ensure_ascii=False)
                        print(f"\t💾 Resultado guardado en {output_file}")
                    break
        else:
            print("\t❌ Error en la ejecución:", run.status)
            

    # Elimina el archivo y el hilo de conversación
    client.files.delete(file_id=uploaded_schema.id)
    client.beta.threads.delete(thread_id=thread.id)
    print("\nHilo de conversación y adjuntos eliminados:", thread.id)

