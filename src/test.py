from getpass import getpass
from dbutils.dbconfig import DBConfig
from dbutils.dbini import DBIni
from dbutils.dbutils import test_connection


dbini = DBIni.load()

config = dbini.get_config('MyDB1')
config.database = 'mierder'
dbini.add_config('MyDB1', config)
dbini.save()

"""
config = DBConfig(
    type="mssql",
    username="root",
    password="",
    host="localhost",
    port=1433, 
    database="dbutils", 
)
dbini.add_config('MyDB1', config)

config = DBConfig.from_url('mssql://localhost:1433/dbutils?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
dbini.add_config('MyDB2', config)

config = DBConfig.from_url('mysql://root:{PASSWORD}@localhost/dbutils?trusted_connection=yes')
dbini.add_config('MyDB3', config)

dbini.save()
print("Configuración guardada en dbtools.ini")"

config = dbini.get_config('MyDB3')
print(config.to_url())
placeholders = config.find_placeholders()
data = {}
for placeholder in placeholders:
    if placeholder == "PASSWORD":        
        input_value = getpass(f"Introduce el valor para {placeholder}: ")
    else:
        input_value = input(f"Introduce el valor para {placeholder}: ")
    data[placeholder] = input_value

print(config.to_url(False, data))

#dbini.remove_config('MyDB1')
#dbini.remove_config('MyDB2')
#dbini.remove_config('MyDB3')
#dbini.save()"
"""
