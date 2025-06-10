import os
import re
from bs4 import BeautifulSoup

def extraer_foreign_keys(html_path):
    """Extrae claves foráneas desde un fichero HTML de tabla"""
    with open(html_path, 'r', encoding='cp1252') as f:
        soup = BeautifulSoup(f, 'html.parser')

    table = soup.find('table', {'id': 'Table.1'})
    if not table:
        return []

    fks = []
    rows = table.find_all('tr')[1:]
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all('td')]
        if len(cols) >= 6 and cols[1].lower() == 'foreign_key':
            fk = {
                'constraint': cols[0],
                'referenced_owner': cols[3],
                'referenced_table': cols[4],
                'referenced_constraint': cols[5]
            }
            fks.append(fk)
            print(f"---- {cols[0]}: Referencia a {cols[4]}")
    return fks

def buscar_fichero_tabla(tabla_referenciada, carpeta):
    """Busca ficheros HTML que contengan el nombre de una tabla"""
    tabla = tabla_referenciada.lower()
    for nombre_fichero in os.listdir(carpeta):
        if not nombre_fichero.lower().endswith('.html'):
            continue
        ruta = os.path.join(carpeta, nombre_fichero)
        with open(ruta, 'r', encoding='cp1252') as f:
            contenido = f.read().lower()
            #if tabla in contenido or tabla in nombre_fichero.lower():
            if tabla in nombre_fichero.lower():
                return nombre_fichero
    return None

def main(html_entrada, carpeta_htmls):
    fks = extraer_foreign_keys(html_entrada)
    print(f"\n🔗 Foreign Keys encontradas en {html_entrada}:\n")
    for fk in fks:
        tabla = fk['referenced_table']
        archivo = buscar_fichero_tabla(tabla, carpeta_htmls)
        if archivo:
            print(f"- {fk['constraint']}: Referencia a {tabla} → encontrado en archivo: {archivo}")
        else:
            print(f"- {fk['constraint']}: Referencia a {tabla} → ❌ archivo no encontrado")

if __name__ == '__main__':
    # Ruta al archivo TLALUMNOS.html (o similar)
    archivo_entrada = 'TLETAPAS.html'

    # Carpeta donde están los demás HTML de tablas
    carpeta_busqueda = '.'

    main(archivo_entrada, carpeta_busqueda)
