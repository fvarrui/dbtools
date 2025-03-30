# dbmapper

Genera el mapeo de dos esquemas de bases de datos para traducir sentencias SQL de un esquema a otro o realizar migraciones de datos entre las bases de datos.

## ¿Cómo se usa?

Para saber cómo se usa `dbmapper` lo mejor es consulta la ayuda:

```bash
$ dbmapper --help

Uso: dbmapper (-h | -v | --map) [--src-schema FILE] [--dst-schema FILE] [--threshold THRESHOLD] [--json FILE]

Genera el mapeo entre dos esquemas de bases de datos (v0.0.1)

Comandos:
  -h, --help            Muestra esta ayuda
  -v, --version         Mostrar versión
  --map                 Genera el mapa de emparejamiento

Opciones:
  --src-schema FILE     Esquema de la base de datos origen
  --dst-schema FILE     Esquema de la base de datos destino
  --threshold THRESHOLD
                        Umbral de similitud para considerar un emparejamiento válido (default: 0.7)
  --json FILE           Exporta el resultado en un fichero JSON

A mapear tus esquemitas
```

### Algunos ejemplos

Aquí tienes también algunos ejemplos de como se usa el comando `dbmapper`.

Para generar el mapeo entre dos esquemas de bases de datos, por ejemplo `src-schema.json` y `dst-schema.json`, y exportar el resultado a un fichero JSON:

```bash
dbmapper --map --src-schema src-schema.json --dst-schema dst-schema.json --json result.json
```