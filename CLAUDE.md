# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac
pip install -e .
```

## Common Commands

```bash
# Reinstall after code changes (editable mode picks them up automatically, but use this after pyproject.toml changes)
pip install -e .

# Install from GitHub
pip install git+https://github.com/fvarrui/dbtools.git

# Single entry point: every tool is a `dbtools` subcommand
dbtools --help
dbtools schema --help
dbtools analyzer --help
dbtools mapper --help
dbtools orm --help
dbtools code --help
dbtools query --help
dbtools config --help
dbtools ddrsearch --help
```

There is no test suite currently. Development dependencies (pytest, black, isort, bumpver, pip-tools) are listed in `pyproject.toml` but tests have not been written.

## Architecture

DBTools is a Python 3.12+ suite of CLI database utilities, all exposed through a **single entry point**: the `dbtools` command. `src/dbtools/__main__.py` is a thin dispatcher — it maps a subcommand name (`schema`, `analyzer`, ...) to a module package and delegates `sys.argv` to that module's own `main()`, imported lazily (only the invoked subcommand's package is imported, so unrelated modules' import-time side effects — e.g. log file creation in `dbanalyzer`/`dborm` — never fire). Each module still lives under `src/` as its own package with its own `__main__.py`/argparse parser; only `dbtools` is registered in `pyproject.toml`'s `[project.scripts]` — the old standalone commands (`dbschema`, `dbanalyzer`, etc.) no longer exist.

### Module Overview

| Subcommand | Module | Purpose | Status |
|--------|--------|---------|--------|
| `schema` | `dbschema` | Extract database schemas to Pydantic models / JSON | Stable |
| `config` | `dbutils` | Shared config, logging, connection pooling, CLI helpers | Stable |
| `analyzer` | `dbanalyzer` | AI-powered semantic analysis of tables/columns via OpenAI | Stable |
| `mapper` | `dbmapper` | Similarity-based schema matching between two databases | Stable |
| `orm` | `dborm` | SQLAlchemy ORM class generation via sqlacodegen | Stable |
| `code` | `dbcode` | Lists, searches and extracts stored procedures/functions (SQL or JSON) | Stable |
| `query` | `dbquery` | Natural language → SQL, using an LLM against the extracted schema | Stable |
| `ddrsearch` | `ddrsearch` | Parse Oracle Data Dictionary Report HTML files | Stable |
| `checker` | `dbchecker` | Data integrity / missing-relationship checks | Stub — `dbtools checker` prints a "not implemented" notice; underlying script is hardcoded to `schemas/pec.json`, not yet a real CLI |

### Dependency Flow

Most tools depend on the two foundation modules:

```
dbschema  ←  database/schema/table/column Pydantic models + SQLAlchemy extraction
dbutils   ←  config.ini / dbtools.ini loading, DB connection pools, CLI helpers

dbanalyzer  →  dbschema + dbutils + OpenAI API (GPT-4.1-mini, tool_use pattern)
dbmapper    →  dbschema + dbutils + SequenceMatcher similarity scoring
dborm       →  dbschema + dbutils + sqlacodegen
dbcode      →  dbschema + dbutils (routine listing/extraction, no schema dependency for the routines themselves)
dbquery     →  dbschema + dbutils + OpenAI API (natural language → SQL via natlang.py)
ddrsearch   →  BeautifulSoup4 → produces dbschema-compatible models
dbchecker   →  dbschema + networkx (graph-based FK/cycle analysis)
```

### Pydantic Schema Models (`src/dbschema/`)

`Database` → `Schema` → `Table` → `Column` / `ForeignKey` / `Reference`

All models are `pydantic.BaseModel` and support JSON round-trip serialization. Factory class methods (`from_metadata()`, `from_json()`) decouple extraction from storage. Pass schema data between tools as JSON files.

### Configuration (`src/dbutils/`)

Two INI files are read from `$HOME/.dbtools/`:

- `config.ini` — global settings (e.g., OpenAI API key)
- `dbtools.ini` — named database connections (one INI section per DB)

CLI commands accept `--db-name <name>` (looks up `dbtools.ini`) or `--db-url <url>` (direct SQLAlchemy URL). Supported databases: PostgreSQL (`psycopg2`), MySQL (`pymysql`), SQL Server (`pyodbc`).

### AI Integration (`src/dbanalyzer/`, `src/dbquery/`)

Uses the OpenAI tool_use (function calling) pattern. `dbanalyzer` defines a structured prompt in `prompt.md` with tools (`get_table_schema`, `get_table_data`) that the model calls iteratively to gather context before producing semantic descriptions. `dbquery` follows the same prompt-driven pattern (`natlang.py` + `prompt.md`) to translate natural language into SQL against a loaded schema. Both require `OPENAI_API_KEY` in `config.ini`.

### CLI Pattern

Every module uses a custom `CustomHelpFormatter` (`dbutils/customhelp.py`) and mutually exclusive argument groups to enforce exactly one action per invocation, with `-h/--help` defined manually inside that group (`add_help=False`) rather than argparse's default. Each parser is built with `prog=__module_name__`, read from the module's own `__init__.py`; `dbtools/__main__.py` monkeypatches that package attribute to `"dbtools <subcommand>"` before importing the submodule so `--help`/usage output shows the real invocation. This pattern is consistent across all `__main__.py` files — when adding a new module, follow it and register the subcommand in `dbtools/__main__.py`'s `SUBCOMMANDS` dict rather than adding a new `[project.scripts]` entry.
