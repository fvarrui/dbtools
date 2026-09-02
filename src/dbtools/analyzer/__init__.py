import logging

__module_name__ = "analyzer"
__module_description__ = "Analizador de esquemas de bases de datos con IA"

# dbtools/__main__.py monkeypatcha __module_name__ a "dbtools analyzer" para el prog= de argparse;
# el logger usa este nombre fijo, capturado antes de esa modificación, para no acabar con un
# espacio en el nombre del logger o del fichero de log.
_logger_name = __module_name__
logger = logging.getLogger(_logger_name)


def configure_logging():
    """
    Configura el logger para escribir en la consola y en un fichero de log con marca de tiempo.
    Se llama explícitamente desde main() para no crear el fichero de log con solo importar el paquete.
    """
    import sys
    import time
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    logger.addHandler(logging.FileHandler(f"{_logger_name}_{timestamp}.log", mode='w', encoding='utf-8'))
