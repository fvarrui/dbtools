import sys
import json
from openai import OpenAI

from dbschema.schema import Schema
from dbutils.config import Config

def main():
    try:
        # Cargar el esquema desde un archivo JSON
        schema = Schema.from_json("schemas/pec.json")

        # Cargar la configuración y obtener la API key
        config = Config()
        apikey = config.get_value("openai.apikey")

        # Inicializar el cliente de OpenAI
        client = OpenAI(api_key=apikey)

        #Listar modelos soportados
        #models = client.models.list()
        #print("Modelos soportados:")
        #for model in models.data:
        #    print(f"- {model.id}")

        schema = Schema.from_json("schemas/pec.json")

        # Generar un mensaje simplificado por cada tabla
        messages = [
            {
                "type": "input_text",
                "text": json.dumps({
                    "table_name": table.name,
                    "columns": [{"name": col.name, "type": col.type} for col in table.columns]
                }),
            } for table in schema.tables
        ]
        messages.append({
            "type": "input_text",
            "text": """
                Usa inferencia para determinar que me des los comentarios sobre todas 
                las tablas y columnas que te he pasado como un esquema,
                indican la información que contienen y su relación con otras tablas.
                Es necesario que la salida sea un JSON válido. La base de datos es el 
                Plan de Estudios de Canarias.
            """,
        })

        # Crear el historial de mensajes
        conversation = [
            {
                "role": "user",
                "content": messages
            }
        ]

        # Enviar la solicitud inicial
        response = client.responses.create(
            model= "gpt-4o",
            instructions="Eres un experto en bases de datos y JSON.",
            input=conversation
        )

        # Mostrar la respuesta inicial
        print(response.output_text)

        # Continuar la conversación
        while True:
            user_input = input("\nTu mensaje (o 'salir' para terminar): ")
            if user_input.lower() == "salir":
                break

            # Agregar el mensaje del usuario al historial
            conversation.append({
                "role": "user",
                "content": user_input
            })

            # Enviar la solicitud con el historial actualizado
            response = client.responses.create(
                model="gpt-4o",
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
        return

if __name__ == "__main__":
    main()
