# dbschema

Extrae esquemas de bases de datos a partir de los metadatos y permite exportarlos en JSON, de manera que puedan ser utilizados para su posterior análisis o para la generación de documentación.

## ¿Cómo se usa?

Para saber cómo se usa `dbschema` lo mejor es consulta la ayuda:

```bash
$ dbschema --help

Uso: dbschema (-h | -v | --schema [FILTER] | --list-tables [FILTER] | --list-views [FILTER]) [--db-url [URL]] [--db-name [DB]] [--json [FILE]] [--password [PASSWORD]]

Genera un esquema de la base de datos para su posterior análisis (v0.0.1)

Comandos:
  -h, --help            Muestra esta ayuda
  -v, --version         Mostrar versión
  --schema [FILTER]     Genera el esquema de la base de datos
  --list-tables [FILTER]
                        Listar todas las tablas
  --list-views [FILTER]
                        Listar todas las vistas

Opciones:
  --db-url [URL]        URL de conexión a la base de datos
  --db-name [DB]        Nombre de la base de datos en el fichero dbtools.ini
  --json [FILE]         Guarda el resultado en un fichero JSON
  --password [PASSWORD]
                        Contraseña de la base de datos

¡Un gran esquema conlleva una gran responsabilidad!
```

### Algunos ejemplos

Aquí tienes también algunos ejemplos de como se usa el comando `dbschema`.

Para generar el esquema de la base de datos `mydb` en formato JSON en el fichero `mydb-schema.json`:

```bash
dbschema --db mydb --schema --json mydb-schema.json
```

> :warning: `mydb` debe estar definido en el fichero `dbtools.ini`.

Si quieres generar el esquema de la base de datos `mydb` en formato JSON en consola para las tablas que contengan `tbl` en su nombre:

```bash
dbschema --db mydb --schema tbl --json
```

O si lo que quieres es mostrar el esquema completo de la base de datos `mydb` en formato tablas en consola:

```bash
dbschema --db mydb --schema
```
