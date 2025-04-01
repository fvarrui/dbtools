import time
import json
import argparse

from tabulate import tabulate

from dbmapper import __module_name__, __module_description__, __module_version__
from dbmapper.mapper import Mapper

from dbschema.schema import Schema

from dbutils.customhelp import CustomHelpFormatter

def main():

    # define el parser
    parser = argparse.ArgumentParser(prog=__module_name__, description=f"{__module_description__} (v{__module_version__})", epilog='A mapear tus esquemitas', add_help=False, formatter_class=CustomHelpFormatter)

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('--map', action='store_true', help='Genera el mapa de emparejamiento')

    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--src-schema', metavar='FILE', help='Esquema de la base de datos origen')
    options.add_argument('--dst-schema', metavar='FILE', help='Esquema de la base de datos destino')
    options.add_argument('--threshold', metavar='THRESHOLD', type=float, default=0.7, help='Umbral de similitud para considerar un emparejamiento válido (default: 0.7)')
    options.add_argument('--json', metavar='FILE', help='Exporta el resultado en un fichero JSON')

    # Parsea los argumentos
    args = parser.parse_args()

    # Muestra la ayuda
    if args.help:
        parser.print_help()
        return

    start_time = time.time()

    print("Comparando esquemas de base de datos...")
    print(f"- Esquema origen  : {args.src_schema}")
    print(f"- Esquema destino : {args.dst_schema}")

    mapper = Mapper(
        src_schema=Schema.from_json(args.src_schema),
        dst_schema=Schema.from_json(args.dst_schema)
    )
    map = mapper.match(threshold=args.threshold)

    # Convertir el diccionario del resultado en JSON
    map_json = json.dumps(
        Mapper.as_matched_schemas_dict(map), 
        indent=4
    )

    # Guarda el resultado en un fichero JSON si se especifica desde la línea de comandos
    if args.json is not None and len(args.json) > 0:
        with open(args.json, "w") as f:
            f.write(map_json)
        print(f"\nMapa guardado en: {args.json}")

    # Muestra las tablas emparejadas en la consola
    print(f"\nTablas emparejadas ({len(map.matched)}):")
    print(tabulate(
        [[ table.src.name, table.dst.name, table.ratio ] for table in map.matched],
        headers=["TABLA ORIGEN", "TABLA DESTINO", "RATIO"],
        tablefmt="grid"
    ))
    
    # Muestra las tablas no emparejadas del origen en la consola
    print(f"\nTablas no emparejadas del esquema origen {args.src_schema} ({len(map.unmatched_srcs)}):")
    print(tabulate(
        [[ table.name ] for table in map.unmatched_srcs],
        headers=["TABLA ORIGEN"],
        tablefmt="grid"
    ))

    # Muestra las tablas no emparejadas del destino en la consola
    print(f"\nTablas no emparejadas del esquema destino {args.dst_schema} ({len(map.unmatched_dsts)}):")
    print(tabulate(
        [[ table.name ] for table in map.unmatched_dsts],
        headers=["TABLA DESTINO"],
        tablefmt="grid"
    ))

    print("\nEmparejamiento de columnas entre las tablas:")
    for matched_table in map.matched:
        # Empareja las columnas de las tablas
        src_table = matched_table.src
        dst_table = matched_table.dst
        columns_result = matched_table.data["columns_result"]
        # Imprime el resultado del emparejamiento de columnas
        print("\n")
        print("-" * 80)
        print(f"\n ")
        print(f"\nColumnas emparejadas entre las tablas {src_table.name} -> {dst_table.name} ({len(columns_result.matched)}):")
        print(tabulate(
            [ [ column.src.name, column.dst.name, column.ratio ] for column in columns_result.matched ],
            headers=["COLUMNA ORIGEN", "COLUMNA DESTINO", "RATIO"],
            tablefmt="grid"
        ))
        # Muestra las columnas no emparejadas del origen en la consola
        if len(columns_result.unmatched_srcs) > 0:
            print(f"\nColumnas no emparejadas de la tabla origen {src_table.name} ({len(columns_result.unmatched_srcs)})")
            print(tabulate(
                [ [ column.name ] for column in columns_result.unmatched_srcs ],
                headers=["COLUMNA ORIGEN"],
                tablefmt="grid"
            ))
        # Muestra las columnas no emparejadas del destino en la consola
        if len(columns_result.unmatched_dsts) > 0:
            print(f"\nColumnas no emparejadas de la tabla destino {dst_table.name} ({len(columns_result.unmatched_dsts)})")
            print(tabulate(
                [ [ column.name ] for column in columns_result.unmatched_dsts ],
                headers=["COLUMNA DESTINO"],
                tablefmt="grid"
            ))

    # Muestra en una tabla la cantidad de tablas emparejadas y no emparejadas
    print("\n\nResumen del emparejamiento:")
    print(tabulate(
        [
            [ "Tablas emparejadas", "", len(map.matched) ],
            [ "Tablas NO emparejadas", "ORIGEN", len(map.unmatched_srcs) ],
            [ "Tablas NO emparejadas", "DESTINO", len(map.unmatched_dsts) ]
        ],
        headers=["DESCRIPCIÓN", "", "TOTAL"],
        tablefmt="grid"
    ))

    # Muestra el tiempo de ejecución
    ellapsed_time = time.time() - start_time
    print(f"\n\nTiempo de ejecución: {ellapsed_time:.2f} segundos")

if __name__ == "__main__":
    main()