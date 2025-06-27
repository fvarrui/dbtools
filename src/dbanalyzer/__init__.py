import logging
import sys

__module_name__ = "dbanalyzer"
__module_description__ = "Analizador de esquemas de bases de datos con IA"
__module_version__ = "0.2.0"

# Configura el logger
logger = logging.getLogger(__module_name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(f"{__module_name__}.log", mode='w', encoding='utf-8'))