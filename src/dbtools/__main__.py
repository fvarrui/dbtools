import importlib
import sys

from dbtools import __module_name__, __module_description__, __module_version__

# subcomando -> (paquete, descripción, pendiente de implementar)
SUBCOMMANDS = {
    "analyzer":  ("dbanalyzer", "Analizador de esquemas de bases de datos con IA", False),
    "checker":   ("dbchecker",  "Analiza el esquema de una base de datos en busca de inconsistencias", True),
    "code":      ("dbcode",     "Lista, busca y extrae procedimientos y funciones almacenadas", False),
    "config":    ("dbutils",    "Gestión de ficheros de configuración y conexiones de dbtools", False),
    "ddrsearch": ("ddrsearch",  "Extrae información de un DDR (Data Dictionary Report) de Oracle", False),
    "mapper":    ("dbmapper",   "Crea mapas entre esquemas de bases de datos para facilitar la migración", False),
    "orm":       ("dborm",      "Genera clases ORM (SQLAlchemy) a partir del esquema de la base de datos", False),
    "query":     ("dbquery",    "Genera consultas SQL en lenguaje natural utilizando IA", False),
    "schema":    ("dbschema",   "Genera el esquema de la base de datos en formato JSON", False),
}


def print_help():
    print(f"{__module_description__} (v{__module_version__})\n")
    print("Uso: dbtools <subcomando> [opciones]\n")
    print("Subcomandos:")
    width = max(len(name) for name in SUBCOMMANDS)
    for name in sorted(SUBCOMMANDS):
        _, description, pending = SUBCOMMANDS[name]
        suffix = " [próximamente]" if pending else ""
        print(f"  {name:<{width}}  {description}{suffix}")
    print("\nOpciones:")
    print("  -h, --help     Muestra esta ayuda")
    print("  -v, --version  Muestra la versión")
    print("\nEjecuta 'dbtools <subcomando> --help' para más información sobre cada subcomando.")


def main():
    argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        print_help()
        return

    if argv[0] in ("-v", "--version"):
        print(f"{__module_name__} v{__module_version__}")
        return

    subcommand = argv[0]

    if subcommand not in SUBCOMMANDS:
        print(f"❌ Subcomando desconocido: '{subcommand}'\n", file=sys.stderr)
        print_help()
        sys.exit(1)

    package_name, description, pending = SUBCOMMANDS[subcommand]

    if pending:
        print(f"⚠️ '{subcommand}' todavía no está implementado. {description}.")
        return

    # Ajusta el nombre del programa mostrado en la ayuda del subcomando (p.ej. "dbtools schema")
    package = importlib.import_module(package_name)
    package.__module_name__ = f"dbtools {subcommand}"

    sys.argv = [package.__module_name__] + argv[1:]
    submodule = importlib.import_module(f"{package_name}.__main__")
    submodule.main()


if __name__ == "__main__":
    main()
