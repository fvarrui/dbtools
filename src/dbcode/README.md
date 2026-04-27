# dbcode

Lista, busca y extrae procedimientos y funciones almacenadas en una base de datos relacional. Pensado para inventariar el código que vive dentro del SGBD y exportarlo como ficheros `.sql` o JSON, de manera que pueda versionarse, revisarse o usarse como entrada de otras herramientas.

Soporta los siguientes dialectos:

- PostgreSQL
- MySQL / MariaDB
- SQL Server (T-SQL)

## ¿Cómo se usa?

Como el resto de comandos de `dbtools`, lo más cómodo es consultar la ayuda integrada:

```bash
$ dbcode --help

Uso: dbcode (-h | -v | --list-procedures [FILTER] | --list-functions [FILTER] | --list [FILTER] | --extract [FILTER] | --search TERM) [--db-url [URL]] [--db-name [DB]] [--json [FILE]] [--output [DIR]]

Lista, busca y extrae procedimientos y funciones almacenadas en la base de datos (v0.1.0)

Comandos:
  -h, --help              Muestra esta ayuda
  -v, --version           Mostrar versión
  --list-procedures [F]   Lista los procedimientos almacenados
  --list-functions [F]    Lista las funciones almacenadas
  --list [F]              Lista procedimientos y funciones
  --extract [F]           Extrae el SQL de procedimientos/funciones
  --search TERM           Busca el término en el nombre o cuerpo

Opciones:
  --db-url [URL]          URL de conexión a la base de datos
  --db-name [DB]          Nombre de la base de datos en dbtools.ini
  --json [FILE]           Salida en formato JSON
  --output [DIR]          Directorio de salida (.sql por rutina)
```

### Filtros

Los argumentos `[FILTER]` filtran por **substring** del nombre de la rutina (case-insensitive). Si no se indican, se muestran todas.

### Combinaciones de salida

| Comando      | `--json FILE` | `--json` (sin fichero) | `--output DIR` | sin opciones                |
|--------------|---------------|------------------------|----------------|-----------------------------|
| `--list-*`   | JSON a fichero| JSON a stdout          | `.sql` por rutina | Tabla resumen            |
| `--extract`  | JSON a fichero| JSON a stdout          | `.sql` por rutina | Tabla + SQL en stdout    |
| `--search`   | JSON a fichero| JSON a stdout          | `.sql` por rutina | Tabla + SQL en stdout    |

> ℹ️ Si se combina `--json` (sin fichero) con `--output DIR`, prevalece `--output` (genera ficheros `.sql`).

### Ejemplos

Listar todos los procedimientos de la base de datos `mydb`:

```bash
dbcode --db-name mydb --list-procedures
```

Listar funciones cuyo nombre contenga `audit`:

```bash
dbcode --db-name mydb --list-functions audit
```

Extraer todos los procedimientos y funciones a un directorio (un fichero `.sql` por cada uno):

```bash
dbcode --db-name mydb --extract --output ./routines
```

Extraer sólo las rutinas cuyo nombre empiece o contenga `usr_` y guardarlas como JSON:

```bash
dbcode --db-name mydb --extract usr_ --json routines.json
```

Buscar todas las rutinas que mencionen una tabla concreta en su cuerpo:

```bash
dbcode --db-name mydb --search "TBL_USUARIOS"
```

Mostrar el SQL completo de las funciones por consola:

```bash
dbcode --db-name mydb --extract
```

## Formato JSON

Cada rutina se serializa con esta estructura:

```json
{
    "name": "fn_calcular_total",
    "type": "FUNCTION",
    "schema_name": "public",
    "language": "plpgsql",
    "return_type": "numeric",
    "definition": "CREATE OR REPLACE FUNCTION ..."
}
```

- `type`: `"PROCEDURE"` o `"FUNCTION"`.
- `language` / `return_type`: dependen del SGBD; pueden ser `null`.
- `definition`: SQL completo del procedimiento o función.

## Detalles por dialecto

| SGBD       | Origen de los datos                                              |
|------------|------------------------------------------------------------------|
| PostgreSQL | `pg_proc` + `pg_get_functiondef()` (incluye CREATE OR REPLACE)   |
| MySQL      | `information_schema.ROUTINES` (sólo cuerpo, sin `CREATE`)        |
| SQL Server | `sys.sql_modules` + `sys.objects` (definición tal cual creada)   |

> ⚠️ En MySQL la columna `ROUTINE_DEFINITION` contiene únicamente el cuerpo (sin la cabecera `CREATE PROCEDURE …`). Si necesitas la sentencia completa, usa `SHOW CREATE PROCEDURE name` desde un cliente MySQL.
