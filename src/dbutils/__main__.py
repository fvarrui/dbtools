import argparse
from pathlib import Path

from dbutils import __module_name__, __module_description__, __module_version__
from dbutils.customhelp import CustomHelpFormatter

def main():

    # define el parser
    parser = argparse.ArgumentParser(
        prog=__module_name__, 
        description=f"{__module_description__} (v{__module_version__})", 
        epilog='¡Déjame ayudarte!', 
        add_help=False, 
        formatter_class=CustomHelpFormatter
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('--config', action='store_true', help='Genera el mapa de emparejamiento')
    commands.add_argument('--database', action='store_true', help='Genera el mapa de emparejamiento')

    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--create', metavar='FILE', help='Esquema de la base de datos origen')
    options.add_argument('--threshold', metavar='THRESHOLD', type=float, default=0.7, help='Umbral de similitud para considerar un emparejamiento válido (default: 0.7)')
    options.add_argument('--json', metavar='FILE', help='Exporta el resultado en un fichero JSON')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return
