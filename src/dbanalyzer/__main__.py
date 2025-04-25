import lmstudio as lms
import time

from dbanalyzer.analyze import analyze
from dbschema.schema import Schema
from dbutils.config import Config

# FIX: no se está usando (ejemplo de uso de lmstudio)
def llm():
    model = lms.llm("meta-llama-3.1-8b-instruct")
    chat = lms.Chat("Eres un experto en bases de datos y JSON.")
    chat.add_user_message
    result = model.respond("Cuál es el sentido de la vida?")
    print(result)
    
def main():
    start = time.time()

    # Cargar la configuración y obtener la API key
    config = Config()
    apikey = config.get_value("openai.apikey")

    # Cargar el esquema de la base de datos desde un archivo JSON
    schema = Schema.from_json("schemas/pec.json")

    # Análisis del esquema de la base de datos
    analyze(apikey, schema)

    ellapsed_time = time.time() - start
    print(f"Tiempo de ejecución: {ellapsed_time:.2f} segundos")

if __name__ == "__main__":
    main()
