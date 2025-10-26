from sqlacodegen.generators import DeclarativeGenerator
from sqlalchemy import create_engine, MetaData

from dbschema.database import Database

def generate_orm_code(dburl, prefix, output_dir='.'):

    database = Database(dburl)
    database.connect()

    print(database)

    # Recuperando la lista de tablas de la base de datos con el prefijo indicado
    table_names = database.list_tables(filter=prefix)
    print("📋 Tablas a incluir: ✅", table_names or "Todas")

    # Cargar la estructura de la base de datos existente
    print("🔄 Cargando la estructura de la base de datos...")
    metadata = MetaData()
    metadata.reflect(bind=database.engine, only=table_names)

    # Generar el código ORM
    print("🛠️ Generando el código ORM...")
    generator_class = DeclarativeGenerator
    generator = generator_class(metadata, database.engine, set())

    with open(f"{output_dir}/{prefix}models.py", "w", encoding="utf-8") as f:
        f.write(generator.generate())

    print(f"✅ Clases ORM generadas correctamente en '{output_dir}/{prefix}models.py'")
