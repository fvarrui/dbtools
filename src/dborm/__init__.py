import sys
import time
import logging

__module_name__ = "dborm"
__module_description__ = "Generador de clases ORM a partir del esquema de la base de datos"
__module_version__ = "0.1.0"

# Configura el logger
timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
logger = logging.getLogger(__module_name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(f"{__module_name__}_{timestamp}.log", mode='w', encoding='utf-8'))
