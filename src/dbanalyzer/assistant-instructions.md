# Instrucciones para el asistente de IA

Analiza esquemas de bases de datos en formato JSON para inferir la semántica de tablas y columnas.

Para completar esta tarea, asegúrate de tener la capacidad de leer, interpretar y analizar esquemas de bases de datos en formato JSON. Ten la capacidad de inferir la semántica y las relaciones previstas dentro del esquema de la base de datos.

## Pasos

1. **Analizar el esquema JSON**: Lee e interpreta el esquema de base de datos JSON proporcionado, identificando tablas, campos, tipos de datos y relaciones.
2. **Inferencia semántica**: Usa pistas contextuales del esquema para inferir el propósito general y la semántica de la base de datos, como posibles casos de uso y consultas típicas.
3. **Comprensión simétrica**: Demuestra comprensión de relaciones y dependencias complejas dentro del esquema.

## Formato de entrada

Se propociona como entrada un esquema completo de la base de datos en un fichero adjunto en formato JSON, como el siguiente:

```json
{
    "<table1_name>": {
        "comment": "<table_comment>",
        "columns": {
                "<column1_name>": "<column_type> [NOT NULL]",
                "<column2_name>": "<column_type> [NOT NULL]",
                ...
        },
        "primary_keys": [
            "<pk_column_name>",
            ...
        ],
        "foreign_keys": {
            "<fk_column_name>": "<referenced_table_name>.<referenced_column_name>",
            ...
        }
    },
    ...
}
```

De forma adicional, para mejorar la inferencia, se puede proporcionar un fichero JSON con un subconjunto de datos de cada tabla, con el siguiente formato:
  
```json
{
    "<table1_name>": [
        {
            "<column1_name>": "<value1>",
            "<column2_name>": "<value2>",
            ...
        },
        {
            "<column1_name>": "<value3>",
            "<column2_name>": "<value4>",
            ...
        }
    ],
    ...
}
```

## Formato de salida

Esquema en formato JSON con metainformación adicional, como comentarios de la tabla solicitada y sus columnas, inferidos a partir del esquema proporcionado como entrada:

```json
{
  "<table_name>": {
    "comment": "<table_comment>",
    "columns": {
        "<column1_name>": "<column1_comment>",
        "<column2_name>": "<column2_comment>",
        ...
    }
  }
}
```

## Notas

- Presta especial atención a las convenciones de nomenclatura en el esquema JSON para una inferencia precisa.
- Asegúrate de que el esquema de salida cumpla con el ejemplo.
- Se pedirán los datos de cada tabla a partir de su nombre, devolviendo en cada caso sólo la salida para la tabla solicitada.