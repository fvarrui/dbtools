import lmstudio as lms

# FIX: no se está usando (ejemplo de uso de lmstudio)
def llm():
    model = lms.llm("meta-llama-3.1-8b-instruct")
    chat = lms.Chat("Eres un experto en bases de datos y JSON.")
    chat.add_user_message
    result = model.respond("Cuál es el sentido de la vida?")
    print(result)