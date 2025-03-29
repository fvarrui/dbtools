# dbmapper

Genera el mapeo de dos esquemas de bases de datos para traducir sentencias SQL de un esquema a otro o realizar migraciones de datos entre las bases de datos.

## ¿Cómo se usa?

Para saber cómo se usa `dbmapper` lo mejor es consulta la ayuda:

```bash
$ dbmapper --help

```

### Algunos ejemplos

Aquí  tienes también algunos ejemplos de como se usa el comando `dbmapper`.

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
