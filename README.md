# DBTools

Conjunto de comandos implementados en Python para facilitar tareas relacionadas con bases de datos relacionales, accesibles todos a través de un único comando `dbtools`:

- [`dbtools analyzer`](#dbtools-analyzer): Analiza la estructura de una base de datos usando IA, obteniendo información semántica de las tablas y columnas.
- [`dbtools checker`](#dbtools-checker): Verifica la integridad de una base de datos. [Próximamente]
- [`dbtools code`](#dbtools-code): Lista, busca y extrae procedimientos y funciones almacenadas en formato SQL o JSON.
- [`dbtools config`](#dbtools-config): Crea y gestiona los ficheros de configuración con las conexiones a las bases de datos.
- [`dbtools ddrsearch`](#dbtools-ddrsearch): Extrae información de un DDR (Data Dictionary Report) de una base de datos Oracle.
- [`dbtools mapper`](#dbtools-mapper): Crea mapas entre esquemas de bases de datos para facilitar la migración de datos.
- [`dbtools orm`](#dbtools-orm): Genera clases ORM (SQLAlchemy) a partir del esquema de la base de datos.
- [`dbtools query`](#dbtools-query): Ejecuta consultas SQL directas o generadas a partir de lenguaje natural con IA.
- [`dbtools schema`](#dbtools-schema): Genera un esquema de la base de datos en formato JSON.

> 😱 Útil para no amargarte la vida.

## ¿Cómo se instala?

Para instalar **dbtools** en tu sistema, puedes hacerlo desde el repositorio de GitHub con el comando `pip` (debes ejecutarlo como Administrador en Windows o con `sudo` en Linux):

```bash
pip install git+https://github.com/fvarrui/dbtools.git
```

> 🐍 Por supuesto, debes tener Python instalado en tu sistema.

Si ya has instalado alguna versión de `dbtools`, puedes actualizarlo con el siguiente comando:

```bash
pip install --upgrade --force-reinstall --no-cache-dir git+https://github.com/fvarrui/dbtools.git
```

## ¿Cómo se usa?

Todos los comandos cuelgan de `dbtools`, en forma de subcomandos. Ejecuta `dbtools --help` para ver el listado completo, y `dbtools <subcomando> --help` para la ayuda de cada uno.

```bash
dbtools --help
dbtools {subcomando} --help
```

> ℹ️ Remplaza `{subcomando}` por el subcomando que quieras usar, por ejemplo `schema`, `analyzer`, etc.

Para obtener más información sobre cada subcomando, consultar la documentación correspondiente.

Las conexiones a la base de datos se configuran en el archivo de configuración `$HOME/.dbtools/dbtools.ini` y usando la opción `--db-name`, o bien proporcionando la cadena de conexión con la opción `--db-url` en la línea de comandos.

Ejemplo de archivo de configuración `dbtools.ini`:

```ini
[database]
type=<mysql|postgresql|mssql>
host=<server>
port=<port>
username=<username>
password=<password>
database=<database name>
driver=<driver>
trusted_connection=<yes|no>
```

> [!WARNING]
> - Si no se proporciona `port`, se usará el puerto por defecto para el tipo de base de datos especificado.
> - Si no se proporciona `password` en el archivo de configuración, se solicitará al usuario.
> - Las opciones `driver` y `trusted_connection` son específicas de SQL Server.

```bash
dbtools {subcomando} --db-name database <opciones>
```

ó 

```bash
dbtools {subcomando} --db-url postgresql://user:password@host:port/database <opciones>
```

Siendo `database` el nombre de la sección en el archivo de configuración.

### Cadenas de conexión

Cadenas de conexión para los distintos sistemas gestores de bases de datos soportados:

| Sistema                                        | Cadena de conexión                                                         |
| ---------------------------------------------- | -------------------------------------------------------------------------- |
| **PostgreSQL**                                 | `postgresql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB_NAME}`                 |
| **MySQL**                                      | `mysql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB_NAME}`                      |
| **SQL Server (SQL Server Authentication)**     | `mssql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB_NAME}?driver={DRIVER}`      |
| **SQL Server (Windows Authentication) [SSPI]** | `mssql://{SERVER}:{PORT}/{DB_NAME}?driver={DRIVER}&trusted_connection=yes` |


## Subcomandos

Detalle y ejemplos de cada subcomando de `dbtools`. Para el listado completo de opciones de cada uno, usa `dbtools <subcomando> --help`.

### `dbtools analyzer`

Analizador semántico de bases de datos: utiliza la API de OpenAI para obtener información descriptiva sobre las tablas y columnas.

Analizar una tabla específica y exportar el resultado a un fichero JSON:

```bash
dbtools analyzer --db-name PincelPreDB --output schemas --analyze-table PEC_EvalCalificaciones
```

Analizar todas las tablas con prefijo `PEC_` y exportar los resultados al directorio `schemas`:

```bash
dbtools analyzer --db-name PincelPreDB --output schemas --analyze-schema PEC_
```

### `dbtools checker`

> ⚠️ Próximamente. Comprobará la integridad de una base de datos relacional: ciclos en las relaciones entre tablas y tablas sin relaciones.

### `dbtools code`

Lista, busca y extrae procedimientos y funciones almacenadas en una base de datos relacional. Pensado para inventariar el código que vive dentro del SGBD y exportarlo como ficheros `.sql` o JSON, de manera que pueda versionarse, revisarse o usarse como entrada de otras herramientas.

Soporta los siguientes dialectos:

- PostgreSQL
- MySQL / MariaDB
- SQL Server (T-SQL)

Los argumentos `[FILTER]` filtran por **substring** del nombre de la rutina (case-insensitive). Si no se indican, se muestran todas.

Combinaciones de salida:

| Comando      | `--json FILE` | `--json` (sin fichero) | `--output DIR` | sin opciones                |
|--------------|---------------|-------------------------|-----------------|-----------------------------|
| `--list-*`   | JSON a fichero| JSON a stdout            | `.sql` por rutina | Tabla resumen              |
| `--extract`  | JSON a fichero| JSON a stdout            | `.sql` por rutina | Tabla + SQL en stdout      |
| `--search`   | JSON a fichero| JSON a stdout            | `.sql` por rutina | Tabla + SQL en stdout      |

> ℹ️ Si se combina `--json` (sin fichero) con `--output DIR`, prevalece `--output` (genera ficheros `.sql`).

Ejemplos:

```bash
# Listar todos los procedimientos de la base de datos mydb
dbtools code --db-name mydb --list-procedures

# Listar funciones cuyo nombre contenga "audit"
dbtools code --db-name mydb --list-functions audit

# Extraer todos los procedimientos y funciones a un directorio (un .sql por cada uno)
dbtools code --db-name mydb --extract --output ./routines

# Extraer sólo las rutinas cuyo nombre contenga "usr_" y guardarlas como JSON
dbtools code --db-name mydb --extract usr_ --json routines.json

# Buscar todas las rutinas que mencionen una tabla concreta en su cuerpo
dbtools code --db-name mydb --search "TBL_USUARIOS"
```

Formato JSON de cada rutina:

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

Origen de los datos por dialecto:

| SGBD       | Origen de los datos                                              |
|------------|--------------------------------------------------------------------|
| PostgreSQL | `pg_proc` + `pg_get_functiondef()` (incluye CREATE OR REPLACE)   |
| MySQL      | `information_schema.ROUTINES` (sólo cuerpo, sin `CREATE`)        |
| SQL Server | `sys.sql_modules` + `sys.objects` (definición tal cual creada)   |

> ⚠️ En MySQL la columna `ROUTINE_DEFINITION` contiene únicamente el cuerpo (sin la cabecera `CREATE PROCEDURE …`). Si necesitas la sentencia completa, usa `SHOW CREATE PROCEDURE name` desde un cliente MySQL.

### `dbtools config`

Crea y gestiona los ficheros de configuración de `dbtools` (`config.ini` y `dbtools.ini`) y las conexiones a bases de datos que contiene este último.

```bash
# Crea el fichero de configuración global (config.ini, API keys, etc.)
dbtools config --create-config

# Crea/gestiona interactivamente el fichero de conexiones (dbtools.ini)
dbtools config --create-db-config

# Añade una nueva conexión a ~/.dbtools/dbtools.ini; los datos que falten se piden por consola
dbtools config --add mydb --type mysql --host localhost --port 3306 --database mydb --username admin

# Lista las conexiones configuradas
dbtools config --list

# Muestra la configuración completa de una conexión (contraseña censurada)
dbtools config --show mydb

# Prueba una conexión
dbtools config --test-connection --db-name mydb

# Devuelve la URL de conexión resuelta para una conexión
dbtools config --get-url --db-name mydb
```

> 🔒 La contraseña nunca se acepta por línea de comandos (ni en `--add` ni en ningún otro subcomando): siempre se solicita de forma interactiva.

### `dbtools ddrsearch`

Extrae información de un DDR (Data Dictionary Report) exportado de una base de datos Oracle: esquema, tablas, columnas y relaciones.

```bash
# Extraer el esquema de la base de datos en formato JSON
dbtools ddrsearch --ddr-dir path/to/ddr/tables --schema --json mydb-schema.json

# Mostrar el detalle de una tabla
dbtools ddrsearch --ddr-dir path/to/ddr/tables --table CENTROS

# Listar las tablas que contienen "CENTROS" en el nombre
dbtools ddrsearch --ddr-dir path/to/ddr/tables --list-tables ^.*CENTROS.*$

# Tablas referenciadas por CENTROS (recursivo hasta 2 niveles)
dbtools ddrsearch --ddr-dir path/to/ddr/tables --used-by CENTROS --limit 2

# Tablas que referencian a CENTROS (recursivo hasta 2 niveles)
dbtools ddrsearch --ddr-dir path/to/ddr/tables --uses CENTROS --limit 2
```

### `dbtools mapper`

Genera el mapeo entre dos esquemas de bases de datos (previamente extraídos con `dbtools schema`), útil para traducir sentencias SQL de un esquema a otro o para migraciones de datos.

```bash
dbtools mapper --map --src-schema src-schema.json --dst-schema dst-schema.json --json result.json
```

### `dbtools orm`

Genera clases ORM de SQLAlchemy (vía `sqlacodegen`) a partir del esquema de una base de datos.

```bash
# Generar las clases ORM de toda la base de datos en el directorio actual
dbtools orm --db-name mydb --gen-classes

# Generar sólo las clases de las tablas con prefijo "usr_" en un directorio concreto
dbtools orm --db-name mydb --gen-classes usr_ --output ./models
```

### `dbtools query`

Ejecuta consultas SQL directas o desde un fichero, y muestra o guarda el resultado.

```bash
# Ejecutar una consulta SQL directa
dbtools query --db-name mydb --sql "SELECT * FROM usuarios WHERE activo = 1"

# Ejecutar una consulta SQL desde un fichero y guardar el resultado en JSON
dbtools query --db-name mydb --sql-file consulta.sql --json resultado.json
```

> ⚠️ `--nat-lang` (generar la consulta a partir de una petición en lenguaje natural con IA) está en desarrollo: por ahora no usa el texto ni el esquema indicados por línea de comandos.

### `dbtools schema`

Extrae esquemas de bases de datos a partir de sus metadatos y permite exportarlos en JSON, de manera que puedan usarse para su posterior análisis, documentación o como entrada de otros subcomandos (`mapper`, `query`, `orm`...).

```bash
# Generar el esquema completo de mydb en un fichero JSON
dbtools schema --db-name mydb --schema --json mydb-schema.json

# Generar en JSON (por consola) sólo las tablas que contengan "tbl" en el nombre
dbtools schema --db-name mydb --schema tbl --json

# Mostrar el esquema completo en formato de tablas por consola
dbtools schema --db-name mydb --schema

# Listar los nombres de las tablas
dbtools schema --db-name mydb --list-tables
```

## Para desarrolladores

Si quieres colaborar en el desarrollo de **dbtools**, puedes hacerlo de la siguiente manera.

Clonar el repositorio y entrar en el directorio:

```bash
git clone https://github.com/fvarrui/dbtools.git
cd dbtools
```

Crear un entorno virtual:

```bash
python -m venv venv
```

Activar el entorno virtual:

```bash
venv\Scripts\activate
```

Instalar el paquete en modo de edición, de modo que se crearán los scripts del paquete y se instalarán las dependencias en el entorno virtual:

```bash
pip install -e .
```

¡Y a programar!

```bash
code .
```

## ¿Cómo contribuir?

¡Tus PRs son bienvenidos!

--- 

Made with ❤️ by [fvarrui](https://github.com/fvarrui)