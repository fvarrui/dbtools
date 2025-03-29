import time
import sys
import json
import argparse

from tabulate import tabulate
from difflib import SequenceMatcher

from dbmapper import __module_name__, __module_description__, __module_version__
from dbmapper.score import Score
from dbmapper.match_result import MatchResult

from dbschema.column import Column
from dbschema.schema import Schema
from dbschema.table import Table

def score_columns(src_column: Column, dst_column: Column, threshold = 0.5) -> Score:
    """
    Calcula el score de similitud entre dos columnas.
    Args:
        src_column: Columna origen.
        dst_column: Columna destino.
        threshold: Umbral de similitud para considerar un emparejamiento válido.
    Returns:
        Score: Score de similitud entre las columnas.
    """
    src = f"{src_column.name}[{src_column.type}]"
    dst = f"{dst_column.name}[{dst_column.type}]"
    type_ratio = SequenceMatcher(None, src_column.type, dst_column.type).ratio()
    if type_ratio > threshold:
        ratio = SequenceMatcher(None, src, dst).ratio()
    else:
        ratio = 0.0
    score = Score.create(
        src=src_column,
        dst=dst_column,
        ratio=ratio
    )
    # Añade el ratio de similitud entre los tipos al score
    score.data["type_ratio"] = type_ratio
    # Devuelve el score
    return score

def score_tables(src_table: Table, dst_table: Table, threshold = 0.7) -> Score:
    """
    Calcula el score de similitud entre dos tablas.
    Se basa en la similitud entre los nombres de las tablas y la similitud entre los nombres de las columnas.
    Args:
        src_table: Tabla origen.
        dst_table: Tabla destino.
    Returns:
        Score: Score de similitud entre las tablas.
    """ 
    # Calcula el ratio de similitud entre los nombres de las tablas
    tables_ratio = SequenceMatcher(None, src_table.name, dst_table.name).ratio()
    # Calcula el ratio de similitud entre las columnas
    columns_ratio = 0.0
    # Calcula los scores de similitud entre todas las columnas de ambas tablas
    result = match(src_table.columns, dst_table.columns, score_columns, threshold=threshold)
    # Calcula el ratio de similitud entre las columnas
    columns_ratio = sum([ score.ratio for score in result.matched ]) / len(src_table.columns + dst_table.columns)
    # Ratio total de similitud entre las tablas y las columnas
    total_ratio = (tables_ratio + columns_ratio)
    # Imprime el ratio de similitud entre las tablas y las columnas    
    #print(f"Ratio de similitud entre {src_table.name} y {dst_table.name} -> {total_ratio:.2f} ({tables_ratio:.2f} + {columns_ratio:.2f})")
    # Pondera la similitud entre los nombres de las tablas
    score = Score.create(
        src=src_table,
        dst=dst_table,
        ratio= total_ratio
    )
    # Añade el ratio de similitud entre las columnas al score
    score.data["columns_result"] = result
    # Devuelve el score
    return score

def match(srcs: list, dsts: list, score_func, threshold=0.7) -> MatchResult:
    """
    Empareja dos listas de objetos (srcs y dsts) utilizando una función de puntuación.
    Args:
        srcs: Lista de objetos origen.
        dsts: Lista de objetos destino.
        score_func: Función de puntuación que calcula la similitud entre dos objetos.
        threshold: Umbral de similitud para considerar un emparejamiento válido.
    Returns:
        MatchResult: Resultado del emparejamiento.
    """
    srcs = sorted([ s for s in srcs ])
    dsts = sorted([ d for d in dsts ])

    # Calcula scores de similitud entre todas las tablas origen y destino
    all_scores = []
    for src in srcs:
        # Calcula el score de similitud entre la tabla origen y todas las tablas destino
        scores = [ score_func(src, dst, threshold) for dst in dsts]
        # Elimina los scores que no superan el umbral
        scores = [ score for score in scores if score.ratio > threshold ]
        # Añade todos los scores a la lista de scores
        all_scores.extend(scores)

    # Ordena los scores por ratio de similitud
    all_scores.sort(key=lambda score: score.ratio, reverse=True)

    # Escoge los mejores scores y los considera matches
    matched = []
    while all_scores:
        # Extrae el primer src score (el mejor candidato)
        best_score = all_scores.pop(0)
        # Añade el score a los matches
        matched.append(best_score)
        # Elimina todos los scores con el mismo src o dst
        all_scores = [ score for score in all_scores if score.src != best_score.src and score.dst != best_score.dst ]

    # Marca los srcs y dsts que no han sido emparejados
    unmatched_srcs = set(srcs) - set([ score.src for score in matched ])
    unmatched_dsts = set(dsts) - set([ score.dst for score in matched ])

    # Devuelve el resultado
    return MatchResult.create(
        matched = matched,
        unmatched_srcs = unmatched_srcs,
        unmatched_dsts = unmatched_dsts
    )

def as_matched_columns_dict(score: Score) -> dict:    
    return { 
        "src": {
            "name": score.src.name,
            "type": score.src.type
        },
        "dst": {
            "name": score.dst.name,
            "type": score.dst.type
        },
        "name_ratio": round(score.ratio, 2),
        "type_ratio": score.data["type_ratio"]
    }

def as_matched_tables_dict(score: Score) -> dict:
    return { 
        "src": score.src.name,
        "dst": score.dst.name,
        "ratio": round(score.ratio, 2),
        "columns": {
            "matched": [ as_matched_columns_dict(column_score) for column_score in score.data["columns_result"].matched ],
            "unmatched": {
                "srcs": sorted([ column.name for column in score.data["columns_result"].unmatched_srcs ]),
                "dsts": sorted([ column.name for column in score.data["columns_result"].unmatched_dsts ])
            }
        }
    }

def as_matched_schemas_dict(result: MatchResult) -> dict:
    return {
        "matched": [ as_matched_tables_dict(match) for match in result.matched ],
        "unmatched": {
            "srcs": sorted([ table.name for table in result.unmatched_srcs ]),
            "dsts": sorted([ table.name for table in result.unmatched_dsts ])
        }
    }

def match_schemas(src_schema: Schema, dst_schema: Schema, threshold=0.7) -> MatchResult:
    """
    Empareja los esquemas de dos bases de datos.
    Args:
        src_schema: Esquema de la base de datos origen.
        dst_schema: Esquema de la base de datos destino.
        threshold: Umbral de similitud para considerar un emparejamiento válido.
    Returns:
        MatchResult: Resultado del emparejamiento.
    """
    src_tables = sorted(src_schema.tables)
    dst_tables = sorted(dst_schema.tables)
    return match(src_tables, dst_tables, score_tables, threshold=threshold)

def main():

    # declara un HelpFormatter personalizado para reemplazar el texto 'usage:' por 'Uso:'
    class CustomHelpFormatter(argparse.HelpFormatter):
        def add_usage(self, usage, actions, groups, prefix='Uso: '):
            if usage is not argparse.SUPPRESS:
                args = usage, actions, groups, prefix
                self._add_item(self._format_usage, args)

    # define el parser
    parser = argparse.ArgumentParser(prog=__module_name__, description=f"{__module_description__} (v{__module_version__})", epilog='¡Un gran esquema conlleva una gran responsabilidad!', add_help=False, formatter_class=CustomHelpFormatter)

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'{__module_name__} v{__module_version__}')
    commands.add_argument('-m', '--map', action='store_true', help='Genera el mapa de emparejamiento')

    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--src-schema', metavar='FILE', help='Esquema de la base de datos origen')
    options.add_argument('--dst-schema', metavar='FILE', help='Esquema de la base de datos destino')
    options.add_argument('--threshold', metavar='THRESHOLD', type=float, default=0.7, help='Umbral de similitud para considerar un emparejamiento válido (default: 0.7)')
    options.add_argument('--json', metavar='FILE', nargs='?', const='', help='Exporta el resultado en un fichero JSON (si no se especifica, se imprime en la salida estándar)')

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

    result = match_schemas(
        src_schema=Schema.from_json(args.src_schema),
        dst_schema=Schema.from_json(args.dst_schema),
        threshold=args.threshold
    )

    # Convierte el resultado en un diccionario
    result_dict = as_matched_schemas_dict(result)

    # Convertir el diccionario del resultado en JSON
    result_json = json.dumps(result_dict, indent=4)

    # Guarda el resultado en un fichero JSON si se especifica desde la línea de comandos
    if args.json is not None and len(args.json) > 0:
        with open(args.json, "w") as f:
            f.write(result_json)
        print(f"\nMapa guardado en: {args.json}")

    # Muestra las tablas emparejadas en la consola
    print(f"\nTablas emparejadas ({len(result.matched)}):")
    print(tabulate(
        [[ table.src.name, table.dst.name, table.ratio ] for table in result.matched],
        headers=["TABLA ORIGEN", "TABLA DESTINO", "RATIO"],
        tablefmt="grid"
    ))
    
    # Muestra las tablas no emparejadas del origen en la consola
    print(f"\nTablas no emparejadas del esquema origen {args.src_schema} ({len(result.unmatched_srcs)}):")
    print(tabulate(
        [[ table.name ] for table in result.unmatched_srcs],
        headers=["TABLA ORIGEN"],
        tablefmt="grid"
    ))

    # Muestra las tablas no emparejadas del destino en la consola
    print(f"\nTablas no emparejadas del esquema destino {args.dst_schema} ({len(result.unmatched_dsts)}):")
    print(tabulate(
        [[ table.name ] for table in result.unmatched_dsts],
        headers=["TABLA DESTINO"],
        tablefmt="grid"
    ))

    print("\nEmparejamiento de columnas entre las tablas:")
    for matched_table in result.matched:
        # Empareja las columnas de las tablas
        src_table = matched_table.src
        dst_table = matched_table.dst
        columns_result = matched_table.data["columns_result"]
        # Imprime el resultado del emparejamiento de columnas
        print("\n")
        print("-" * 80)
        print(f"\n{src_table.name} -> {dst_table.name} ({len(columns_result.matched)})")
        print(f"Ratio de similitud: {matched_table.ratio:.2f}")
        print(tabulate(
            [ [ column.src.name, column.dst.name, column.ratio ] for column in columns_result.matched ],
            headers=["COLUMNA ORIGEN", "COLUMNA DESTINO", "RATIO"],
            tablefmt="grid"
        ))
        # Muestra las columnas no emparejadas del origen en la consola
        if len(columns_result.unmatched_srcs) > 0:
            print(f"\nColumnas no emparejadas del esquema origen {src_table.name} ({len(columns_result.unmatched_srcs)})")
            print(tabulate(
                [ [ column.name ] for column in columns_result.unmatched_srcs ],
                headers=["COLUMNA ORIGEN"],
                tablefmt="grid"
            ))
        # Muestra las columnas no emparejadas del destino en la consola
        if len(columns_result.unmatched_dsts) > 0:
            print(f"\nColumnas no emparejadas del esquema destino {dst_table.name} ({len(columns_result.unmatched_dsts)})")
            print(tabulate(
                [ [ column.name ] for column in columns_result.unmatched_dsts ],
                headers=["COLUMNA DESTINO"],
                tablefmt="grid"
            ))

    # Muestra en una tabla la cantidad de tablas emparejadas y no emparejadas
    print("\n\nResumen del emparejamiento:")
    print(tabulate(
        [
            [ "Tablas emparejadas", "", len(result.matched) ],
            [ "Tablas NO emparejadas", "ORIGEN", len(result.unmatched_srcs) ],
            [ "Tablas NO emparejadas", "DESTINO", len(result.unmatched_dsts) ]
        ],
        headers=["DESCRIPCIÓN", "", "TOTAL"],
        tablefmt="grid"
    ))

    # Muestra el tiempo de ejecución
    ellapsed_time = time.time() - start_time
    print(f"\n\nTiempo de ejecución: {ellapsed_time:.2f} segundos")

if __name__ == "__main__":
    main()