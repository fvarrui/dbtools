from networkx import DiGraph, simple_cycles

from dbchecker import __module_name__, __module_description__, __module_name__, __module_version__
from dbschema.schema import Schema

def find_missing_relationships(schema):
    """
    Busca posibles relaciones faltantes en las tablas del esquema.
    Args:
        schema (Schema): El esquema de la base de datos.
    Returns:
        list[tuple]: Lista de posibles relaciones faltantes en formato (tabla_origen, columna, tabla_destino).
    """
    missing_relationships = []

    # Crear un diccionario de claves primarias por tabla
    primary_keys = {table.name: table.primary_keys for table in schema.tables}

    # Iterar sobre las tablas para buscar columnas que podrían ser claves foráneas
    for table in schema.tables:
        for column in table.columns:
            # Ignorar columnas que ya son claves foráneas
            if any(fk.column == column.name for fk in table.foreign_keys):
                continue

            # Buscar si el nombre de la columna coincide con una clave primaria de otra tabla
            for target_table, pk_columns in primary_keys.items():
                if column.name in pk_columns and table.name != target_table:
                    missing_relationships.append((table.name, column.name, target_table))

    return missing_relationships


def main():
    # Cargar el esquema de la base de datos desde un archivo JSON
    schema = Schema.from_json("schemas/pec.json")

    # Crea un grafo dirigido
    graph = DiGraph()

    # Agregar las tablas como nodos del grafo
    graph.add_nodes_from([table.name for table in schema.tables])

    # Agregar las relaciones foráneas como aristas del grafo
    for table in schema.tables:
        for fk in table.foreign_keys:
            graph.add_edge(table.name, fk.reference.table, relation=f"{table.name}.{fk.column} -> {fk.reference}")

    print(graph)

    print("\nTablas:\n")
    for node in sorted(graph.nodes):
        print(node)

    print("\nRelaciones:\n")
    for u, v, data in graph.edges(data=True):
        print(f"{u} → {v}")  # , nombre: {data.get('relation')")

    print("\nCiclos:\n")
    cycles = simple_cycles(graph)
    for cycle in cycles:
        print(cycle)

    # Buscar relaciones faltantes
    missing_relationships = find_missing_relationships(schema)

    """
    # Mostrar las relaciones faltantes
    print("\nRelaciones faltantes:\n")
    if missing_relationships:
        for source_table, column, target_table in missing_relationships:
            print(f"Posible relación faltante: {source_table}.{column} → {target_table}")
    else:
        print("No se encontraron relaciones faltantes.")"
    """

    print("\n¡Proceso finalizado!")

if __name__ == "__main__":
    main()
