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

# Run any CLI tool
dbschema --help
dbanalyzer --help
dbmapper --help
dborm --help
dbcode --help
dbquery --help
dbutils --help
ddrsearch --help
```

There is no test suite currently. Development dependencies (pytest, black, isort, bumpver, pip-tools) are listed in `pyproject.toml` but tests have not been written.

## Architecture

DBTools is a Python 3.12+ suite of CLI database utilities. All modules live under `src/` and are registered as entry points in `pyproject.toml`.

### Module Overview

| Module | Purpose | Status |
|--------|---------|--------|
| `dbschema` | Extract database schemas to Pydantic models / JSON | Stable |
| `dbutils` | Shared config, logging, connection pooling, CLI helpers | Stable |
| `dbanalyzer` | AI-powered semantic analysis of tables/columns via OpenAI | Stable |
| `dbmapper` | Similarity-based schema matching between two databases | Stable |
| `dborm` | SQLAlchemy ORM class generation via sqlacodegen | Stable |
| `dbcode` | Lists, searches and extracts stored procedures/functions (SQL or JSON) | Stable |
| `dbquery` | Natural language → SQL, using an LLM against the extracted schema | Stable |
| `ddrsearch` | Parse Oracle Data Dictionary Report HTML files | Stable |
| `dbchecker` | Data integrity / missing-relationship checks | Stub — hardcoded to `schemas/pec.json`, not yet a real CLI |

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

Every module uses a custom `CustomHelpFormatter` (`dbutils/customhelp.py`) and mutually exclusive argument groups to enforce exactly one action per invocation. This pattern is consistent across all `__main__.py` files.
