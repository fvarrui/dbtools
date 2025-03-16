# DBTools

Conjunto de comandos implementados en Python para facilitar tareas relacionadas con bases de datos relacionales:

- `dbanalyzer`: Analiza la estructura de una base de datos usando IA, obteniendo información semántica de las tablas y columnas.
- `dbchecker`: Verifica la integridad de una base de datos.
- `dbmapper`: Crea mapas de entre esquemas de bases de datos para facilitar la migración de datos.
- `dbsequel`: ...
- [`dbschema`](src/dbschema/README.md): Genera un esquema de la base de datos en formato JSON.

> Útil para no amargarte la vida.

## ¿Cómo se instala?

Para instalar **dbtools** en tu sistema, puedes hacerlo desde el repositorio de GitHub con el comando `pip` (debes ejecutarlo como Administrador en Windows o con `sudo` en Linux):

```bash
pip install git+https://github.com/fvarrui/dbtools.git
```

> Por supuesto, debes tener Python instalado en tu sistema.

Si ya has instalado alguna versión de `dbtools`, puedes actualizarlo con el siguiente comando:

```bash
pip install --upgrade --force-reinstall --no-cache-dir git+https://github.com/fvarrui/dbtools.git
```

## ¿Cómo se usa?

Cada comando tiene su propia ayuda, que se puede obtener ejecutando el comando con la opción `--help`.

Por ejemplo:

```bash
$ dbanalyzer --help
```

Para obtener más información sobre cada comando, consultar la documentación correspondiente.

Las conexiones a la base de datos se configuran mediante una cadena de conexión que se debe especificar en el archivo de configuración `dbtools.ini` o por como una opción en la línea de comandos.

```ini
[database]
dburl = postgresql+psycopg2://user:password@host:port/database
```

```bash
$ dbanalyzer --db database <opciones>
```

ó 

```bash
$ dbanalyzer --dburl postgresql://user:password@host:port/database <opciones>
```

> Siendo `database` el nombre de la sección en el archivo de configuración.

### Cadenas de conexión

Las cadenas de conexión para los distintos sistemas gestores de bases de datos soportados se muestran a continuación:

| Sistema | Cadena de conexión |
|---------|---------------------|
| PostgreSQL | `postgresql+psycopg2://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB_NAME}` |
| MySQL | `mysql+pymysql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB_NAME}` |
| SQL Server (SQL Server Authentication) | `mssql+pyodbc://{USER}:{PASSWORD}@{SERVER}}:{PORT}}/{DB_NAME}` |
| SQL Server (Windows Authentication) | `mssql+pyodbc://{USER}:{PASSWORD}@{SERVER}}:{PORT}}/{DB_NAME}` |


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