
from difflib import SequenceMatcher
from dbmapper.match_result import MatchResult
from dbmapper.matcher import Matcher
from dbmapper.score import Score

from dbschema.column import Column
from dbschema.schema import Schema
from dbschema.table import Table


class Mapper:

    src_schema: Schema
    dst_schema: Schema

    def __init__(self, src_schema: Schema, dst_schema: Schema):
        self.src_schema = src_schema
        self.dst_schema = dst_schema

    @staticmethod
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

    @staticmethod
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
        result = Matcher.match(src_table.columns, dst_table.columns, Mapper.score_columns, threshold=threshold)
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

    @staticmethod
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

    @staticmethod
    def as_matched_tables_dict(score: Score) -> dict:
        return { 
            "src": score.src.name,
            "dst": score.dst.name,
            "ratio": round(score.ratio, 2),
            "columns": {
                "matched": [ Mapper.as_matched_columns_dict(column_score) for column_score in score.data["columns_result"].matched ],
                "unmatched": {
                    "srcs": sorted([ column.name for column in score.data["columns_result"].unmatched_srcs ]),
                    "dsts": sorted([ column.name for column in score.data["columns_result"].unmatched_dsts ])
                }
            }
        }

    @staticmethod
    def as_matched_schemas_dict(result: MatchResult) -> dict:
        return {
            "matched": [ Mapper.as_matched_tables_dict(match) for match in result.matched ],
            "unmatched": {
                "srcs": sorted([ table.name for table in result.unmatched_srcs ]),
                "dsts": sorted([ table.name for table in result.unmatched_dsts ])
            }
        }

    def match(self, threshold=0.7) -> MatchResult:
        """
        Empareja los esquemas de dos bases de datos.
        Args:
            threshold: Umbral de similitud para considerar un emparejamiento válido.
        Returns:
            MatchResult: Resultado del emparejamiento.
        """
        src_tables = sorted(self.src_schema.tables)
        dst_tables = sorted(self.dst_schema.tables)
        return Matcher.match(src_tables, dst_tables, Mapper.score_tables, threshold=threshold)