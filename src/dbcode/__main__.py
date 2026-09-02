import os
import sys
import json
import argparse

from tabulate import tabulate

from dbcode import __module_name__, __module_description__
from dbcode.code_repository import CodeRepository
from dbschema.database import Database
from dbutils.customhelp import CustomHelpFormatter
from dbutils.dbini import DB_INIFILE, DBIni


def _connect(args) -> Database | None:
    if not (args.db_url or args.db_name):
        return None
    try:
        db_url = args.db_url or DBIni.load().get_url(args.db_name)
    except Exception as e:
        print(f"No se ha podido obtener la URL de conexión a la base de datos: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        database = Database(db_url)
        database.connect()
        print(f"Conectado a la base de datos '{database.name}'")
        return database
    except Exception as e:
        print(f"¡No se ha podido conectar a la base de datos!", e, file=sys.stderr)
        sys.exit(1)


def _print_table(routines):
    headers = ["TYPE", "NAME", "SCHEMA", "LANGUAGE", "RETURNS"]
    data = [
        [r.type, r.name, r.schema_name or "", r.language or "", r.return_type or ""]
        for r in routines
    ]
    print(tabulate(data, headers=headers, tablefmt="grid"))


def _safe_filename(name: str, type_: str) -> str:
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
    suffix = "proc" if type_ == "PROCEDURE" else "func"
    return f"{safe}.{suffix}.sql"


def _dump_sql_files(routines, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for r in routines:
        file_path = os.path.join(output_dir, _safe_filename(r.name, r.type))
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(r.to_sql())
        print(f"  ✅ {file_path}")
    print(f"\n✅ {len(routines)} rutinas exportadas a: {output_dir}")


def _emit_routines(routines, args, *, sql_default: bool):
    """
    Emite las rutinas según las opciones --json y --output.
        sql_default: si True, cuando no hay --json ni --output se imprime también
                     el SQL en stdout (para --extract/--search). Si False, sólo tabla.
    """
    # --json FILE: un único JSON con todas las rutinas
    if args.json is not None and len(args.json) > 0:
        payload = [r.model_dump() for r in routines]
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, indent=4, ensure_ascii=False))
        print(f"\n✅ {len(routines)} rutinas guardadas en: {args.json}")
        return

    # --output DIR (con o sin --json sin fichero): un .sql por rutina
    if args.output is not None:
        _dump_sql_files(routines, args.output)
        return

    # --json sin fichero: JSON por stdout
    if args.json is not None:
        payload = [r.model_dump() for r in routines]
        print(f"\n{json.dumps(payload, indent=4, ensure_ascii=False)}")
        return

    # Sin opciones de salida: tabla resumen, y SQL si procede
    _print_table(routines)
    if sql_default:
        for r in routines:
            print(f"\n-- {r.type} {r.name}")
            print(r.to_sql())


def main():

    # define el parser
    parser = argparse.ArgumentParser(
        prog=__module_name__,
        description=__module_description__,
        epilog='El código almacenado también merece amor.',
        add_help=False,
        formatter_class=CustomHelpFormatter,
    )

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda')
    commands.add_argument('--list-procedures', metavar='FILTER', nargs='?', const='', help='Lista los procedimientos almacenados. Filtra por substring del nombre si se indica.')
    commands.add_argument('--list-functions', metavar='FILTER', nargs='?', const='', help='Lista las funciones almacenadas. Filtra por substring del nombre si se indica.')
    commands.add_argument('--list', metavar='FILTER', nargs='?', const='', help='Lista todos los procedimientos y funciones. Filtra por substring del nombre si se indica.')
    commands.add_argument('--extract', metavar='FILTER', nargs='?', const='', help='Extrae el SQL de los procedimientos/funciones. Filtra por substring del nombre si se indica.')
    commands.add_argument('--search', metavar='TERM', help='Busca el término en el nombre o cuerpo de los procedimientos/funciones.')

    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('--db-url', metavar='URL', help='URL de conexión a la base de datos')
    options.add_argument('--db-name', metavar='DB', help=f"Nombre de la base de datos en el fichero {DB_INIFILE}")
    options.add_argument('--json', metavar='FILE', nargs='?', const='', help='Salida en formato JSON. Si no se especifica un fichero, se utiliza la salida estándar.')
    options.add_argument('--output', metavar='DIR', nargs='?', const='.', help='Directorio de salida. Combinado con --extract o --search, genera un fichero .sql por rutina.')

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        return

    database = _connect(args)
    if database is None:
        print("❌ No se ha especificado una base de datos. Usa --db-url o --db-name.")
        sys.exit(1)

    repo = CodeRepository(database)

    # --list-procedures
    if args.list_procedures is not None:
        print("Listando procedimientos ...")
        if args.list_procedures:
            print(f"\t- Filtrando por nombre que contenga: {args.list_procedures}")
        routines = repo.list_routines(type_filter="PROCEDURE", name_filter=args.list_procedures)
        _emit_routines(routines, args, sql_default=False)
        print(f"\n{len(routines)} procedimientos encontrados")
        return

    # --list-functions
    if args.list_functions is not None:
        print("Listando funciones ...")
        if args.list_functions:
            print(f"\t- Filtrando por nombre que contenga: {args.list_functions}")
        routines = repo.list_routines(type_filter="FUNCTION", name_filter=args.list_functions)
        _emit_routines(routines, args, sql_default=False)
        print(f"\n{len(routines)} funciones encontradas")
        return

    # --list (procedimientos + funciones)
    if args.list is not None:
        print("Listando procedimientos y funciones ...")
        if args.list:
            print(f"\t- Filtrando por nombre que contenga: {args.list}")
        routines = repo.list_routines(name_filter=args.list)
        _emit_routines(routines, args, sql_default=False)
        print(f"\n{len(routines)} rutinas encontradas")
        return

    # --extract
    if args.extract is not None:
        print("Extrayendo procedimientos y funciones ...")
        if args.extract:
            print(f"\t- Filtrando por nombre que contenga: {args.extract}")
        routines = repo.list_routines(name_filter=args.extract)
        if not routines:
            print("❌ No se han encontrado rutinas que coincidan.")
            return
        _emit_routines(routines, args, sql_default=True)
        return

    # --search
    if args.search is not None:
        print(f"Buscando '{args.search}' en nombre y cuerpo de rutinas ...")
        routines = repo.search_routines(args.search)
        if not routines:
            print("❌ Ninguna coincidencia.")
            return
        _emit_routines(routines, args, sql_default=True)
        print(f"\n{len(routines)} coincidencias")
        return


if __name__ == "__main__":
    main()
