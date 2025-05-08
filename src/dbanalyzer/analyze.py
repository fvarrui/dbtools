import sys
import json
import io
from openai import OpenAI

from dbschema.schema import Schema

def analyze(apikey: str, schema: Schema) -> str:

    # Inicializar el cliente de OpenAI
    client = OpenAI(api_key=apikey)

    # Recupera el asistente especializado en bases de datos y SQL
    assistant = client.beta.assistants.retrieve(
        assistant_id="asst_cNhjPcFXhk0jLPmkW7LienS7"
    )
    print("🤖 Asistente especializado en bases de datos y SQL recuperado:", assistant.name)

    # Crea un hilo de conversación
    thread = client.beta.threads.create()
    print("🗣️ Hilo de conversación creado:", thread.id)

    # Sube el esquema de la base de datos
    schema_reduced = schema.reduce()

    print(json.dumps(schema_reduced, indent=None, separators=(",", ":")))
    sys.exit(1)

    schema_json = io.BytesIO(json.dumps(schema_reduced, indent=None, separators=(",", ":")).encode('utf-8'))
    schema_json.name = "schema.json"
    uploaded_schema = client.files.create(
        file=schema_json,       # archivo JSON del esquema de la base de datos
        purpose="assistants",   # contexto para el asistente,
    )
    print("📄 Esquema subido:", uploaded_schema.id)

    # Añadir un mensaje del usuario
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Se adjunta fichero JSON con el esquema de la base de datos para su análisis.",
        attachments=[
            { 
                "file_id": uploaded_schema.id, 
                "tools": [{"type": "file_search"}]
            }
        ],
    )
    print("📤 Mensaje enviado pidiendo que utilice los adjuntos:", message.id)

    print("😀 Iniciando análisis del esquema de la base de datos...")
    for table in schema.tables:

        print("\n📤 Enviando petición de análisis para la tabla:", table.name)

        # Añadir un mensaje del usuario para analizar la tabla
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Realiza análisis semántico de la tabla {table.name} en el esquema de la base de datos y devuelve el JSON.",
        )

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
                    output_file = f"schemas/pec_{table.name}_analysis.json"
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

