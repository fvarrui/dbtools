# DBTools

Conjunto de comandos implementados en Python para facilitar tareas relacionadas con bases de datos relacionales:

- `dbanalyzer`: Analiza la estructura de una base de datos usando IA, obteniendo información semántica de las tablas y columnas.
- `dbchecker`: Verifica la integridad de una base de datos.
- [`dbmapper`](src/dbmapper/README.md): Crea mapas de entre esquemas de bases de datos para facilitar la migración de datos.
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
dbanalyzer --help
```

Para obtener más información sobre cada comando, consultar la documentación correspondiente.

Las conexiones a la base de datos se configuran en el archivo de configuración `dbtools.ini` y usando la opción `--db`, o bien proporcionando la cadena de conexión con la opción `--dburl` en la línea de comandos.

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
dbanalyzer --db database <opciones>
```

ó 

```bash
dbanalyzer --dburl postgresql://user:password@host:port/database <opciones>
```

> Siendo `database` el nombre de la sección en el archivo de configuración.

### Cadenas de conexión

Las cadenas de conexión para los distintos sistemas gestores de bases de datos soportados se muestran a continuación:

| Sistema | Cadena de conexión |
|---------|---------------------|
| PostgreSQL | `postgresql+psycopg2://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB_NAME}` |
| MySQL | `mysql+pymysql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB_NAME}` |
| SQL Server (SQL Server Authentication) | `mssql+pyodbc://{USER}:{PASSWORD}@{SERVER}}:{PORT}}/{DB_NAME}?driver={DRIVER}` |
| SQL Server (Windows Authentication) [SSPI] | `mssql+pyodbc://{SERVER}}:{PORT}}/{DB_NAME}?driver={DRIVER}&trusted_connection=yes` |


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