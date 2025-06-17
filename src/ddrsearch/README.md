# ddrsearch

Extrae información de un DDR (Data Dictionary Report) de una base de datos Oracle.

## ¿Cómo se usa?

Para saber cómo se usa `ddrsearch` lo mejor es consultar la ayuda:

```bash
$ ddrsearch --help

Uso: ddrsearch (-h | -v | --schema [TABLE_FILTER] | --table TABLE_NAME | --list-tables [TABLE_FILTER] | --used-by TABLE_NAME | --uses TABLE_NAME | --search SEARCH_TERM) [--ddr-dir DIR] [--json [OUTPUT_FILE]]
               [--limit LIMIT] [--filter FILTER]

Analiza el Data Dictionary Report exportado de una base de datos Oracle para extraer información sobre tablas, columnas y relaciones. (v0.0.3)

Comandos:
  -h, --help            Muestra esta ayuda
  -v, --version         Mostrar versión
  --schema [TABLE_FILTER]
                        Genera el esquema de la base de datos de las tablas del Data Dictionary Report. El filtro es una expresión regular que se aplica a los nombres de las tablas. Por defecto, se incluyen
                        todas las tablas.
  --table TABLE_NAME    Muestra información de la tabla indicada del Data Dictionary Report. El nombre de la tabla debe coincidir con el nombre del archivo HTML sin la extensión.
  --list-tables [TABLE_FILTER]
                        Lista los nombres de las tablas del Data Dictionary Report. El filtro es una expresión regular que se aplica a los nombres de las tablas. Si no se especifica, se listan todas las
                        tablas.
  --used-by TABLE_NAME  Recorre las tablas referenciadas por la tabla indicada en el Data Dictionary Report. El nombre de la tabla debe coincidir con el nombre del archivo HTML sin la extensión. Esta opción
                        no está implementada en este momento.
  --uses TABLE_NAME     Recorre las tablas que referencian la tabla indicada en el Data Dictionary Report. El nombre de la tabla debe coincidir con el nombre del archivo HTML sin la extensión. Esta opción no
                        está implementada en este momento.
  --search SEARCH_TERM  Busca un término en el Data Dictionary Report, devolviendo las tablas y columnas que lo contienen (busca en nombres y comentarios de tablas y columnas).

Opciones:
  --ddr-dir DIR         Directorio del Data Dictionary Report
  --json [OUTPUT_FILE]  Exporta el resultado en formato JSON. Si no se especifica un archivo, se imprime en la salida estándar.
  --limit LIMIT         Límite de resultados a mostrar (por defecto: 9223372036854775807)
  --filter FILTER       Filtro utilizado por algunos comandos.

¡Todo por Doramas!
```

### Algunos ejemplos

Aquí  tienes también algunos ejemplos de como se usa el comando `ddrsearch`.

#### Extraer el esquema de la base de datos en formato JSON

```bash
ddrsearch --ddr-dir path/to/ddr/tables --schema --json mydb-schema.json
```

#### Mostrar el detalle de una tabla

```bash
ddrsearch --ddr-dir path/to/ddr/tables --table CENTROS
```

#### Listar las tablas de la base de datos con un filtro (que contienen la palabra `CENTROS`)

```bash
ddrsearch --ddr-dir path/to/ddr/tables --list-tables ^.*CENTROS.*$
```

#### Mostrar las tablas referenciadas por una tabla (recursivo hasta 2 niveles)

```bash
ddrsearch --ddr-dir path/to/ddr/tables --used-by CENTROS --limit 2
```

#### Mostrar las tablas que referencian una tabla (recursivo hasta 2 niveles)

```bash
ddrsearch --ddr-dir path/to/ddr/tables --uses CENTROS --limit 2
```