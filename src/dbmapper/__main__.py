import sys
import json
from difflib import get_close_matches, SequenceMatcher

from dbschema.schema import Schema
from dbmapper.score import Score

def remove_prefix(text):
    return text.split("_", 1)[1]

def load_schema(json_path) -> Schema: 
    with open(json_path, "r", encoding="utf-8") as f:
        schema_json = json.load(f)
    return Schema.model_validate(schema_json['schema'])

def get_table_map(source_tables, tgt_table_names, cutoff=0.0):
    mapping = {}
    src_table_names = [t["name"] for t in source_tables]
    tgt_table_names = [t["name"] for t in tgt_table_names]
    print(src_table_names)
    print(tgt_table_names)
    for src_table_name in src_table_names:
        match = get_close_matches(
            src_table_name,
            tgt_table_names,
            n=1, cutoff=cutoff
        )
        if match:
            mapping[src_table_name] = match[0]
            tgt_table_names.remove(match[0])
    return mapping

def get_column_map(src_columns, tgt_columns, cutoff=0.6):
    src_names = [c["name"] for c in src_columns]
    tgt_names = [c["name"] for c in tgt_columns]

    mapping = {}
    for s in src_names:
        match = get_close_matches(s, tgt_names, n=1, cutoff=cutoff)
        mapping[s] = match[0] if match else None
    return mapping

def generate_mapping(source_path, target_path, output_path):
    src_schema = load_schema(source_path)
    dst_schema = load_schema(target_path)

    source_tables = src_schema["schema"]["tables"]
    target_tables = dst_schema["schema"]["tables"]

    table_matches = get_table_map(source_tables, target_tables)

    print(table_matches)

    sys.exit()

    mappings = []
    used_source = set()
    used_target = set()

    for src_table, tgt_table in table_matches.items():
        src_cols = source_tables[src_table]["columns"]
        tgt_cols = target_tables[tgt_table]["columns"]
        col_map = get_column_map(src_cols, tgt_cols)

        src_col_names = {c["name"] for c in src_cols}
        tgt_col_names = {c["name"] for c in tgt_cols}
        used_source.update([src_table])
        used_target.update([tgt_table])

        mapped_cols = {v: k for k, v in col_map.items() if v}
        unmatched = {
            "source_only": sorted(tgt_col_names - set(mapped_cols.keys())),
            "target_only": sorted(src_col_names - set(col_map.keys()))
        }

        mappings.append({
            "source_table": src_table,
            "target_table": tgt_table,
            #"column_mapping": mapped_cols,
            #"unmatched_columns": unmatched
        })

    result = {
        "table_mappings": mappings,
        "summary": {
            "source_only": sorted(set(target_tables) - used_target),
            "target_only": sorted(set(source_tables) - used_source)
        }
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"📄 Mapa generado en: {output_path}")

def match_tables(src_table, dst_table):
    # TODO mejorar el match entre tablas para considerar también nombres y tipos de columnas
    return Score(
        name=dst_table,
        ratio=SequenceMatcher(None, src_table, dst_table).ratio()
    )

    """
    cols1 = {col["name"]: col["type"] for col in src_table["columns"]}
    cols2 = {col["name"]: col["type"] for col in dst_table["columns"]}

    matched = 0
    tipo_correcto = 0

    for c1 in cols1:
        match = max(cols2, key=lambda c2: SequenceMatcher(None, c1, c2).ratio(), default=None)
        ratio = SequenceMatcher(None, c1, match).ratio() if match else 0

        if ratio >= 0.8:  # consideramos el nombre como similar
            matched += 1
            if cols1[c1] == cols2[match]:
                tipo_correcto += 1

    total_columnas = max(len(cols1), len(cols2))
    if total_columnas == 0:
        return 0.0

    # Ponderar similitud de nombres y tipos
    similitud_nombre = matched / total_columnas
    similitud_tipo = tipo_correcto / total_columnas

    score = (1 - peso_tipo) * similitud_nombre + peso_tipo * similitud_tipo
    return round(score, 3)

    score = [ {
        "name": dst_table, 
        "ratio": SequenceMatcher(None, src_table, dst_table).ratio() 
    } ]
    scores.sort(key=lambda t: t['ratio'], reverse=True)
    best_score = scores[0] if scores and scores[0]['ratio'] > 0.7 else None
    matches.append({
        "src_table": src_table,
        "best_ratio": best_score['ratio'] if best_score else 0,
        "scores": best_score if best_score else None
    })

    return result"
    """

def match_columns(src_table, dst_table):
    pass



def match_schemas(src_schema, dst_schema, threshold=0.7):
    src_tables = [ table['name'] for table in src_schema["schema"]["tables"] ]
    dst_tables = [ table['name'] for table in dst_schema["schema"]["tables"] ]
    unmatched_src = []
    best_matches = []
    while src_tables:
        matches = []
        for src_table in src_tables:
            # Calcula el score de similitud entre la tabla origen y todas las tablas destino
            scores = [ match_tables(src_table, dst_table) for dst_table in dst_tables]
            # Ordena los scores de mayor a menor
            scores.sort(key=lambda t: t['ratio'], reverse=True)
            # Obtiene el mejor score si es mayor al umbral
            best_score = scores[0] if scores and scores[0]['ratio'] > threshold else None
            # Guarda el mejor score
            matches.append({
                "src_table": src_table,
                "best_ratio": best_score['ratio'] if best_score else 0,
                "scores": best_score if best_score else None
            })
        matches = sorted(matches, key=lambda match: match["best_ratio"], reverse=True)
        src_tables.remove(matches[0]["src_table"])
        if matches[0]["scores"]:
            best_matches.append({
                "src_table": matches[0]["src_table"],
                "dst_table": matches[0]["scores"]["name"] if matches[0]["scores"] else None,
                "ratio": matches[0]["best_ratio"]
            })
            dst_tables.remove(matches[0]["scores"]["name"])
        else:
            unmatched_src.append(matches[0]["src_table"])
    unmatched_dst = dst_tables
    best_matches = sorted(best_matches, key=lambda match: match["src_table"])
    return {
        "best_matches": best_matches,
        "unmatched_src": unmatched_src,
        "unmatched_dst": unmatched_dst
    }

def main():
    #generate_mapping("schemas/pec_schema.json", "schemas/xes_schema.json", "schemas/mapa_migracion_pec_a_xes.json")

    src_schema = load_schema("schemas/xes_schema.json")
    for table in src_schema.tables:
        table.print()


    #src_schema = load_schema("schemas/pec_schema.json")
    #dst_schema = load_schema("schemas/xes_schema.json")
    #result = match_schemas(src_schema, dst_schema, threshold=0.7)
    #json.dump(result, sys.stdout, indent=4)


if __name__ == "__main__":
    main()