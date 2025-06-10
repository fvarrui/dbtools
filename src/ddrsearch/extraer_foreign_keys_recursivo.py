import os
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
            #print(f"---- {cols[0]}: Referencia a {cols[4]} de {html_path}")
    return fks

def buscar_fichero_tabla(tabla_referenciada, carpeta):
    """Busca ficheros HTML cuyo nombre contenga el nombre de la tabla referenciada"""
    tabla = tabla_referenciada.lower()
    for nombre_fichero in os.listdir(carpeta):
        if not nombre_fichero.lower().endswith('.html'):
            continue
       # print(f"- Tabla: {tabla}  -- Nombre fichero {nombre_fichero.lower()}")
        if  nombre_fichero.lower().startswith(tabla):
            return os.path.join(carpeta, nombre_fichero)
    return None

def recorrer_tablas_recursivamente(tabla_actual, html_path, carpeta, visitadas, nivel=0):
    indent = "  " * nivel
    print(f"{indent}🔍 Tabla: {tabla_actual}")

    if tabla_actual in visitadas:
        #print(f"{indent}↪️ Ya visitada, omitiendo...")
        return
    visitadas.add(tabla_actual)

    foreign_keys = extraer_foreign_keys(html_path)
    for fk in foreign_keys:
        tabla_destino = fk['referenced_table']
        html_destino = buscar_fichero_tabla(tabla_destino, carpeta)
        if html_destino:
            print(f"{indent}  ↳ FK {fk['constraint']} → {tabla_destino}")
            #print(f"- {fk['constraint']}: Referencia a {tabla_destino} → encontrado en archivo: {html_destino}")
            recorrer_tablas_recursivamente(tabla_destino, html_destino, carpeta, visitadas, nivel + 1)
        else:
            print(f"{indent}  ⚠️ FK {fk['constraint']} → {tabla_destino} (archivo no encontrado)")

def main(tabla_inicial, carpeta_htmls):
    archivo_inicial = buscar_fichero_tabla(tabla_inicial, carpeta_htmls)
    if not archivo_inicial:
        print(f"❌ No se encontró el archivo HTML para la tabla {tabla_inicial}")
        return

    visitadas = set()
    #print(f"---- Tabla inicial: {tabla_inicial}   ---  Archivo inicial: {archivo_inicial}")
    recorrer_tablas_recursivamente(tabla_inicial, archivo_inicial, carpeta_htmls, visitadas)

if __name__ == '__main__':
    # Tabla raíz y carpeta de ficheros HTML
    tabla_raiz = 'TLCENTROS'
    carpeta_htmls = '.'

    main(tabla_raiz, carpeta_htmls)
