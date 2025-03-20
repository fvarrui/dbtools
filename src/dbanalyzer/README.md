# DBAnalyzer

`dbanalyzer` es un analizador semántico de bases de datos, que forma parte de la suite de herramientas de [DBTools](../..), y utiliza técnicas de inteligencia artificial para obtener información sobre las tablas y columnas de una base de datos.

## ¿Cómo se utiliza?

Para obtener información sobre una base de datos, simplemente ejecuta el comando `dbanalyzer` con la opción `--db` o `--dburl`:

```bash
dbanalyzer --dburl "mysql://user:password@localhost:3306/database"
```

ó

```bash
dbanalyzer --db database
```

> Siendo `database` el nombre de la sección en el archivo de configuración.
>
> Las conexiones a la base de datos se configuran en el archivo de configuración `dbtools.ini` y usando la opción `--db`, o bien proporcionando la cadena de conexión con la opción `--dburl` en la línea de comandos.

Para obtener más información sobre cada comando, consultar la documentación correspondiente.

