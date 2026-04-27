from sqlalchemy import text

from dbschema.database import Database
from dbcode.routine import Routine


# Consultas para extraer rutinas (procedimientos/funciones) por dialecto.
# Cada query devuelve filas con: name, type, schema, language, return_type, definition.

_QUERY_POSTGRESQL = """
SELECT
    p.proname AS name,
    CASE p.prokind WHEN 'p' THEN 'PROCEDURE' ELSE 'FUNCTION' END AS type,
    n.nspname AS schema_name,
    l.lanname AS language,
    pg_get_function_result(p.oid) AS return_type,
    pg_get_functiondef(p.oid) AS definition
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
LEFT JOIN pg_language l ON p.prolang = l.oid
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
"""

_QUERY_MYSQL = """
SELECT
    ROUTINE_NAME AS name,
    ROUTINE_TYPE AS type,
    ROUTINE_SCHEMA AS schema_name,
    EXTERNAL_LANGUAGE AS language,
    DATA_TYPE AS return_type,
    ROUTINE_DEFINITION AS definition
FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA = DATABASE()
"""

_QUERY_MSSQL = """
SELECT
    o.name AS name,
    CASE o.type
        WHEN 'P' THEN 'PROCEDURE'
        ELSE 'FUNCTION'
    END AS type,
    s.name AS schema_name,
    'T-SQL' AS language,
    NULL AS return_type,
    m.definition AS definition
FROM sys.sql_modules m
JOIN sys.objects o ON m.object_id = o.object_id
JOIN sys.schemas s ON o.schema_id = s.schema_id
WHERE o.type IN ('P', 'FN', 'IF', 'TF')
"""

_QUERIES = {
    "postgresql": _QUERY_POSTGRESQL,
    "mysql": _QUERY_MYSQL,
    "mssql": _QUERY_MSSQL,
}


class CodeRepository:
    """
    Repositorio que extrae procedimientos y funciones de la base de datos.
    Soporta PostgreSQL, MySQL y SQL Server.
    """

    def __init__(self, database: Database):
        self.database = database
        self.dialect = database.type
        if self.dialect not in _QUERIES:
            raise ValueError(
                f"Dialecto no soportado para extraer procedimientos/funciones: {self.dialect}"
            )

    def list_routines(
        self,
        type_filter: str | None = None,
        name_filter: str | None = None,
    ) -> list[Routine]:
        """
        Lista los procedimientos y/o funciones de la base de datos.
            :param type_filter: 'PROCEDURE', 'FUNCTION' o None para ambos
            :param name_filter: Filtro por nombre (substring, case-insensitive)
            :returns: Lista de Routine
        """
        query = _QUERIES[self.dialect]
        rows = self.database.execute(text(query))
        routines = [Routine(**row) for row in rows]

        if type_filter:
            type_filter = type_filter.upper()
            routines = [r for r in routines if r.type == type_filter]

        if name_filter:
            needle = name_filter.lower()
            routines = [r for r in routines if needle in r.name.lower()]

        return sorted(routines)

    def search_routines(self, term: str) -> list[Routine]:
        """
        Busca rutinas cuyo nombre o definición contengan el término.
            :param term: Término de búsqueda (case-insensitive)
            :returns: Lista de Routine que coinciden
        """
        needle = term.lower()
        results = []
        for routine in self.list_routines():
            in_name = needle in routine.name.lower()
            in_body = needle in (routine.definition or "").lower()
            if in_name or in_body:
                results.append(routine)
        return results
