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

DBTools is a Python 3.12+ suite of CLI database utilities, all exposed through a **single entry point**: the `dbtools` command. Every module is a subpackage of `dbtools` (`src/dbtools/schema/`, `src/dbtools/analyzer/`, ...) — only `dbtools` itself is registered in `pyproject.toml`'s `[project.scripts]`; the old standalone commands (`dbschema`, `dbanalyzer`, etc.) no longer exist, and neither do the old flat top-level packages.

`src/dbtools/__main__.py` is a thin dispatcher: `SUBCOMMANDS` maps a subcommand name to whether it's pending (not implemented) — the subcommand name always equals its subpackage name (`dbtools schema` ↔ `dbtools.schema`). For a real subcommand it lazily imports only `dbtools.<subcommand>.__main__` and delegates `sys.argv` to that module's own `main()` — each subpackage's argparse setup is untouched, and unrelated subpackages' import-time side effects never fire (e.g. `analyzer`/`orm` used to create a log file just by being imported; that init now lives in `configure_logging()`, called explicitly from their own `main()`, specifically so `dbtools --help` can safely import every subpackage's `__init__.py` to read its description without side effects — see below). It also monkeypatches the target subpackage's `__module_name__` to `"dbtools <subcommand>"` before importing `__main__`, so that subcommand's own `--help` shows the real invocation as its `prog`.

`dbtools --help` builds its subcommand listing by importing each subpackage and reading `__module_description__` live — there is no separate copy of the descriptions to keep in sync. When adding a new module: give it `__module_name__`/`__module_description__` in its own `__init__.py` (avoid any I/O or heavy work at import time — only cheap, side-effect-free code belongs there, since it runs on every `dbtools --help`), and register it in `SUBCOMMANDS` rather than adding a new `[project.scripts]` entry.

### Module Overview

| Subcommand | Subpackage | Purpose | Status |
|--------|--------|---------|--------|
| `schema` | `dbtools.schema` | Extract database schemas to Pydantic models / JSON | Stable |
| `config` | `dbtools.config` | Manage `config.ini`/`dbtools.ini`, connection testing | Stable |
| `analyzer` | `dbtools.analyzer` | AI-powered semantic analysis of tables/columns via OpenAI | Stable |
| `mapper` | `dbtools.mapper` | Similarity-based schema matching between two databases | Stable |
| `orm` | `dbtools.orm` | SQLAlchemy ORM class generation via sqlacodegen | Stable |
| `code` | `dbtools.code` | Lists, searches and extracts stored procedures/functions (SQL or JSON) | Stable |
| `query` | `dbtools.query` | Runs direct/file SQL and shows or saves the result. `--nat-lang` (NL → SQL via an LLM) exists but is not wired up yet — it ignores the given text/schema | Stable (nat-lang: WIP) |
| `ddrsearch` | `dbtools.ddrsearch` | Parse Oracle Data Dictionary Report HTML files | Stable |
| `checker` | `dbtools.checker` | Data integrity / missing-relationship checks | Stub — `dbtools checker` prints a "not implemented" notice; underlying script is hardcoded to `schemas/pec.json`, not yet a real CLI |

### Dependency Flow

Most tools depend on the foundation subpackages:

```
dbtools.schema  ←  database/schema/table/column Pydantic models + SQLAlchemy extraction
dbtools.config  ←  config.ini / dbtools.ini loading, DB connection pools, connection testing
dbtools.utils   ←  domain-agnostic helpers with no CLI of their own: CustomHelpFormatter, JSON serialization

dbtools.analyzer   →  schema + config + utils + OpenAI API (GPT-4.1-mini, tool_use pattern)
dbtools.mapper     →  schema + utils + SequenceMatcher similarity scoring
dbtools.orm        →  schema + config + utils + sqlacodegen
dbtools.code       →  schema + config + utils (routine listing/extraction, no schema dependency for the routines themselves)
dbtools.query      →  schema + config + utils + OpenAI API (natural language → SQL via natlang.py)
dbtools.ddrsearch  →  BeautifulSoup4 + utils → produces dbtools.schema-compatible models
dbtools.checker    →  schema + networkx (graph-based FK/cycle analysis)
```

`dbtools.utils` is pure shared library code (no `__main__.py`, no `__module_name__`/`__module_description__` — it isn't a `SUBCOMMANDS` entry). `dbtools.config` is both a subcommand (`dbtools config`) and a library other subpackages import for `dbtools.ini`/`config.ini` access.

### Pydantic Schema Models (`src/dbtools/schema/`)

`Database` → `Schema` → `Table` → `Column` / `ForeignKey` / `Reference`

All models are `pydantic.BaseModel` and support JSON round-trip serialization. Factory class methods (`from_metadata()`, `from_json()`) decouple extraction from storage. Pass schema data between tools as JSON files.

### Configuration (`src/dbtools/config/`)

Two INI files are read from `$HOME/.dbtools/`:

- `config.ini` (`settings.py`'s `Config` class) — global settings (e.g., OpenAI API key)
- `dbtools.ini` (`dbini.py`'s `DBIni` class, `dbconfig.py`'s `DBConfig` value object) — named database connections (one INI section per DB)

CLI commands accept `--db-name <name>` (looks up `dbtools.ini`) or `--db-url <url>` (direct SQLAlchemy URL) — both require a value; the bare flag with nothing after it is a parse error, not "unset". Supported databases: PostgreSQL (`psycopg2`), MySQL (`pymysql`), SQL Server (`pyodbc`, including named instances `host\instance`).

`dbtools config` manages `dbtools.ini` directly: `--list`/`--show NAME` read it (resolved via `DBIni.load()`, checking the current directory before `~/.dbtools/`); `--add NAME` always writes to the user's `~/.dbtools/dbtools.ini`, filling in from `--type`/`--host`/`--port`/`--database`/`--username`/`--driver`/`--trusted-connection` and prompting interactively (`input_db_config()`) for whatever is still missing — the password is never a CLI argument, only ever a `getpass` prompt.

### AI Integration (`src/dbtools/analyzer/`, `src/dbtools/query/`)

Uses the OpenAI tool_use (function calling) pattern. `analyzer` defines a structured prompt in `prompt.md` with tools (`get_table_schema`, `get_table_data`) that the model calls iteratively to gather context before producing semantic descriptions. `query`'s `natlang.py` follows the same prompt-driven pattern but its `--nat-lang` CLI wiring is incomplete (see Module Overview). Both require `OPENAI_API_KEY` in `config.ini`.

### CLI Pattern

Every subpackage uses a custom `CustomHelpFormatter` (`dbtools/utils/customhelp.py`) and mutually exclusive argument groups to enforce exactly one action per invocation, with `-h/--help` defined manually inside that group (`add_help=False`) rather than argparse's default. No subcommand has its own `-v/--version` — only `dbtools --version` exists, reading `dbtools/__init__.py`'s `__module_version__`.

Each parser is built with `prog=__module_name__`, read from the subpackage's own `__init__.py`; the dispatcher monkeypatches that attribute to `"dbtools <subcommand>"` right before importing `__main__`, so `--help`/usage output shows the real invocation.
