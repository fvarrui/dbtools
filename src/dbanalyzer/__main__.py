import sys
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

        # Subir el archivo JSON al servidor
        file = client.files.create(
            file=open("schemas/pec.json", "rb"),
            purpose="user_data"
        )

        # Crear el historial de mensajes
        conversation = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": file.id,
                    },
                    {
                        "type": "input_text",
                        "text": """
                            Quiero que me des el mismo esquema pero con los comentarios de tablas y columnas.
                            Es necesario que la salida sea un JSON válido. Usa la inferencia, en función
                            de las relaciones y los nombres y tipos de datos. La base de datos es el 
                            Plan de Estudios de Canarias. Si necesitas datos de las tablas, dímelo.
                        """,
                    },
                ]
            }
        ]

        # Enviar la solicitud inicial
        response = client.responses.create(
            model="gpt-4o",
            instructions="Eres un experto en bases de datos y JSON.",
            response_format="json",
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
