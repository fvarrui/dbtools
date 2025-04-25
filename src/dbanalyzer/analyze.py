import json
import io
from openai import OpenAI

from dbschema.schema import Schema

def analyze(apikey: str, schema_file: Schema):

    # Inicializar el cliente de OpenAI
    client = OpenAI(api_key=apikey)

    # Recupera el asistente especializado en bases de datos y SQL
    assistant = client.beta.assistants.retrieve(
        assistant_id="asst_cNhjPcFXhk0jLPmkW7LienS7"
    )

    # Crea un hilo de conversación
    thread = client.beta.threads.create()
    print("Hilo de conversación creado:", thread.id)

    # Sube el esquema de la base de datos
    schema_reduced = schema_file.reduce()
    schema_json = json.dumps(schema_reduced, indent=None, separators=(",", ":"))
    schema_file = client.files.create(
        file=schema_json.encode('utf-8'),
        purpose="assistants", # contexto para el asistente
    )
    print("Esquema subido:", schema_file.id)

    # Añadir un mensaje del usuario
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Devuélveme el mismo esquema pero añadiendo comentarios a cada tabla y cada columna",
        attachments=[{"file_id": schema_file.id, "tools": [{"type": "file_search"}]}],
    )
    print("Mensaje del usuario añadido al hilo de conversación")

    # Ejecutar el hilo de conversación con el asistente
    print("Ejecución iniciada:", run.id)
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        # prints last message
        for message in reversed(messages.data):
            if message.role == "assistant":
                print(f"Respuesta del asistente {assistant.name}:\n")
                print(message.content[0].text.value)
                break
    else:
        print(run.status)

    # Elimina el archivo y el hilo de conversación
    client.files.delete(file_id=schema_file.id)
    client.beta.threads.delete(thread_id=thread.id)
    print("\nHilo de conversación y adjuntos eliminados:", thread.id)
