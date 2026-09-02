import importlib
import sys

from dbtools import __module_name__, __module_description__, __module_version__

# subcomando -> (subpaquete de dbtools, pendiente de implementar)
SUBCOMMANDS = {
    "analyzer":  ("analyzer", False),
    "checker":   ("checker", True),
    "code":      ("code", False),
    "config":    ("utils", False),
    "ddrsearch": ("ddrsearch", False),
    "mapper":    ("mapper", False),
    "orm":       ("orm", False),
    "query":     ("query", False),
    "schema":    ("schema", False),
}


def print_help():
    print(f"{__module_description__} (v{__module_version__})\n")
    print("Uso: dbtools <subcomando> [opciones]\n")
    print("Subcomandos:")
    width = max(len(name) for name in SUBCOMMANDS)
    for name in sorted(SUBCOMMANDS):
        subpackage_name, pending = SUBCOMMANDS[name]
        # Sólo se importa el __init__ del subpaquete (barato, sin efectos secundarios) para
        # leer su __module_description__: es la única fuente de la descripción, así nunca
        # puede desincronizarse de la que muestra "dbtools <subcomando> --help".
        subpackage = importlib.import_module(f"dbtools.{subpackage_name}")
        description = subpackage.__module_description__
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

    subpackage_name, pending = SUBCOMMANDS[subcommand]
    subpackage = importlib.import_module(f"dbtools.{subpackage_name}")

    if pending:
        print(f"⚠️ '{subcommand}' todavía no está implementado. {subpackage.__module_description__}.")
        return

    # Ajusta el nombre del programa mostrado en la ayuda del subcomando (p.ej. "dbtools schema")
    subpackage.__module_name__ = f"dbtools {subcommand}"

    sys.argv = [subpackage.__module_name__] + argv[1:]
    submodule = importlib.import_module(f"dbtools.{subpackage_name}.__main__")
    submodule.main()


if __name__ == "__main__":
    main()
