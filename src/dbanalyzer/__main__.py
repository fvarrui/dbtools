import sys
import json
import lmstudio as lms
import tiktoken
from pprint import pprint
from time import time
from openai import OpenAI

from dbschema.schema import Schema
from dbutils.config import Config

def test():
    
    # Cargar la configuración y obtener la API key
    config = Config()
    apikey = config.get_value("openai.apikey")

    # Inicializar el cliente de OpenAI
    client = OpenAI(api_key=apikey)

    # Recupera el asistente especializado en bases de datos y SQL
    assistant = client.beta.assistants.retrieve(
        assistant_id="asst_cNhjPcFXhk0jLPmkW7LienS7"
    )
    print("Usando asistente:", assistant.name)

    # Crea un hilo de conversación
    thread = client.beta.threads.create()
    print("Hilo de conversación creado:", thread.id)

    # Sube el esquema de la base de datos
    schema = client.files.create(
        file=open("schemas/pec.json", "rb"),
        purpose="assistants",
    )
    print("Esquema subido:", schema.id)

    # Hacer una pregunta al asistente
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    print("Ejecución iniciada:", run.id)

    # Elimina el hilo de conversación
    client.beta.threads.delete(thread_id=thread.id)
    print("Hilo de conversación eliminado:", thread.id)

def openai():
    try:

        # Cargar la configuración y obtener la API key
        config = Config()
        apikey = config.get_value("openai.apikey")

        # Inicializar el cliente de OpenAI
        client = OpenAI(api_key=apikey)

        # Indicar el modelo a utilizar
        model = "gpt-4-1106-preview"

        # Crear el tokenizador para el modelo
        tokenizer = tiktoken.encoding_for_model(model) 

        #Listar modelos soportados
        #models = client.models.list()
        #print("Modelos soportados:")
        #for model in models.data:
        #    print(f"- {model.id}")

        # Cargar el esquema desde un archivo JSON
        schema = Schema.from_json("schemas/pec.json")

        reduced_schema = schema.reduce()

        json_minimizado = json.dumps(reduced_schema, indent=None, separators=(",", ":"))
        print(f"Longitud del JSON minimizado: {len(json_minimizado)}")  

        # Generar un mensaje simplificado por cada tabla
        messages = [
            {
                "type": "input_text",
                "text": json_minimizado,
            } 
            ,{
                "type": "input_text",
                "text": """
                    Usa inferencia para que me des comentarios sobre todas 
                    las tablas y columnas que te he pasado como un esquema,
                    indican la información que contienen y su relación con otras tablas.
                    La base de datos es el Plan de Estudios de Canarias.
                """,
            }
        ]

        # Crear el historial de mensajes
        conversation = [
            {
                "role": "user",
                "content": messages
            }
        ]

        #if len(tokens) > 30000:
        #    print("El mensaje es demasiado largo para el modelo.")
        #    return

        # Enviar la solicitud inicial
        response = client.responses.create(
            model= model,
            instructions="Eres un experto en bases de datos y JSON.",
            input=conversation
        )

        # Mostrar la respuesta inicial
        print(response.output_text)

        # Continuar la conversación
        while True:
            
            # Contar los tokens del mensaje
            print(f"Tokens: {len(tokenizer.encode(json.dumps(conversation)))}")

            user_input = input("\n----------> Tu mensaje (o 'salir' para terminar): ")
            if user_input.lower() == "salir":
                break

            # Agregar el mensaje del usuario al historial
            conversation.append({
                "role": "user",
                "content": user_input
            })

            # Enviar la solicitud con el historial actualizado
            response = client.responses.create(
                model=model,
                instructions="Eres un experto en bases de datos y JSON.",
                input=conversation
            )

            # Agregar la respuesta del modelo al historial
            conversation.append({
                "role": "assistant",
                "content": response.output_text
            })

            # Mostrar la respuesta del modelo
            print(response.output_text)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        e.print(f"Traceback: {sys.exc_info()[2]}", file=sys.stderr)
        return
    
def main():
    start = time()

    #model = lms.llm("meta-llama-3.1-8b-instruct")
    #chat = lms.Chat("Eres un experto en bases de datos y JSON.")
    #chat.add_user_message

    #result = model.respond("Cuál es el sentido de la vida?")
    #print(result)

    openai()

    ellapsed_time = time() - start
    print(f"Tiempo de ejecución: {ellapsed_time:.2f} segundos")

if __name__ == "__main__":
    #main()
    test()
