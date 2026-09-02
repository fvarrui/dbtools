import time
import logging
import sys

__module_name__ = "dbanalyzer"
__module_description__ = "Analizador de esquemas de bases de datos con IA"

# Configura el logger
timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
logger = logging.getLogger(__module_name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(f"{__module_name__}_{timestamp}.log", mode='w', encoding='utf-8'))
