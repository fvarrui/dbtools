# DBAnalyzer

`dbanalyzer` es un analizador semántico de bases de datos, que utiliza técnicas de inteligencia artificial (API de OpenAI) para obtener información descriptiva sobre las tablas y columnas.

## ¿Cómo se utiliza?

Para saber cómo se usa `dbanalyzer` lo mejor es consultar la ayuda:

```bash
$ dbanalyzer --help

Uso: dbanalyzer (-h | -v | --analyze-table TABLE_NAME | --analyze-schema [FILTER]) [--db-url [URL]] [--db-name [DB]] [--json [FILE]]

Analizador de esquemas de bases de datos con IA (v0.1.0)

Comandos:
  -h, --help            Muestra esta ayuda
  -v, --version         Mostrar versión
  --analyze-table TABLE_NAME
                        Realiza el análisis semántico de la tabla especificada.
  --analyze-schema [FILTER]
                        Analiza todas las tablas con el prefijo indicado, o todas las tablas de la base de datos si no se especifica un prefijo. La opción --json genera el resultado en un formato JSON.

Opciones:
  --db-url [URL]        URL de conexión a la base de datos
  --db-name [DB]        Nombre de la base de datos en el fichero dbtools.ini
  --json [FILE]         Entrada o salida en formato JSON. Si no se especifica un fichero, se utiliza la entrada y salida estándar.

¡IA-stoy aquí para hacer lo que tú no quieres hacer!
```

### Ejemplos

Ejemplos de uso del comando `dbanalyzer`.

#### Analizar una tabla específica

##### Ejemplo 1

Para analizar la tabla `PEC_Evaluaciones` de la base de datos `PincelPreDB` (guardada con ese nombre en la configuración) y exportar el resultado al fichero JSON con nombre `PEC_Evaluaciones.json` en el directorio actual:

```bash
dbanalyzer --db-name PincelPreDB --output --analyze-table PEC_Evaluaciones
```

##### Ejemplo 2

Para analizar la tabla `PEC_EvalCalificaciones` de la base de datos `PincelPreDB` (guardada con ese nombre en la configuración) y exportar el resultado al fichero JSON `PEC_EvalCalificaciones.json` del directorio `schemas`:

```bash
dbanalyzer --db-name PincelPreDB --output schemas --analyze-table PEC_EvalCalificaciones
```

#### Analizar todas las tablas de un esquema con un prefijo específico

Para analizar las tablas con prefijo `PEC_` de la base de datos `PincelPreDB` (guardada con ese nombre en la configuración) y exportando los resultados en el directorio `schemas`:

```bash
dbanalyzer --db-name PincelPreDB --output schemas --analyze-schema PEC_
```

