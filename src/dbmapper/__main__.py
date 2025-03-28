import sys
import json
from difflib import get_close_matches, SequenceMatcher

from dbmapper.match_result import MatchResult
from dbschema.column import Column
from dbschema.schema import Schema
from dbmapper.score import Score
from dbschema.table import Table

def score_columns(src_column: Column, dst_column: Column) -> Score: 
    src = src_column.name + " " + src_column.type
    dst = dst_column.name + " " + dst_column.type
    return Score.create(
        src=src_column,
        dst=dst_column,
        ratio=SequenceMatcher(None, src, dst).ratio()
    )

def score_tables(src_table: Table, dst_table: Table) -> Score:


    # Calcula los scores de similitud entre todas las columnas de ambas tablas
    result = match(src_table.columns, dst_table.columns, score_columns, threshold=0.7)

    # Calcula el ratio de similitud entre las columnas
    columns_ratio = sum([ score.ratio for score in result.matches ]) / len(src_table.columns + dst_table.columns)

    # Calcula el ratio de similitud entre los nombres de las tablas
    tables_ratio = SequenceMatcher(None, src_table.name, dst_table.name).ratio()

    print(f"Ratio de similitud entre {src_table.name} y {dst_table.name} -> {tables_ratio}")

    # Pondera la similitud entre los nombres de las tablas
    return Score.create(
        src=src_table,
        dst=dst_table,
        ratio= tables_ratio + columns_ratio
    )

def match(srcs: list, dsts: list, score_func , threshold=0.7) -> MatchResult:
    srcs = [ s for s in srcs ].sort()
    dsts = [ d for d in dsts ].sort()
    best_scores = []
    while srcs:
        best_score :Score = None
        for src in srcs:
            # Calcula el score de similitud entre la tabla origen y todas las tablas destino
            scores = [ score_func(src, dst) for dst in dsts]
            # Ordena los scores de mayor a menor
            scores.sort(key=lambda score: score.ratio, reverse=True)
            # Obtiene el mayor score si es mayor al umbral
            higher_score = scores[0] if scores[0].ratio > threshold else None
            # Guarda el mejor score
            if higher_score and (not best_score or higher_score.ratio > best_score.ratio):
                best_score = higher_score
        # Si no hay un mejor score, termina el ciclo
        if not best_score:
            break
        # Si hay un mejor score, lo agrega a la lista de mejores scores y elimina las tablas de origen y destino
        srcs.remove(best_score.src)
        if best_score:
            best_scores.append(best_score)
            dsts.remove(best_score.dst)
    best_scores = sorted(best_scores, key=lambda score: str(score.src))
    return MatchResult.create(
        matches = best_scores,
        unmatched_srcs = srcs,
        unmatched_dsts = dsts
    )


def main():
    #generate_mapping("schemas/pec_schema.json", "schemas/xes_schema.json", "schemas/mapa_migracion_pec_a_xes.json")

    src_schema = Schema.from_json("schemas/pec.json")
    dst_schema = Schema.from_json("schemas/xes.json")
    result = match(src_schema.tables, dst_schema.tables, score_tables, threshold=0.7)
    json.dump({
        "matches": [ str(match) for match in result.matches ],
        "unmatched_srcs": [ table.name for table in result.unmatched_srcs ],
        "unmatched_dsts": [ table.name for table in result.unmatched_dsts ]
    }, sys.stdout, indent=4)


if __name__ == "__main__":
    main()