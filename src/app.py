import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import pandas as pd

# Paso 2: Descargar HTML
# Seleccionar el recurso a descargar
resource_url =  "https://companies-market-cap-copy.vercel.app/index.html"


# Petición para descargar el fichero de Internet
response = requests.get(resource_url)
#print( response.status_code)

html_content = response.text  # convertir a texto

# Transformamos el HTML plano en un HTML real (estructurado y anidado, con forma de árbol)

soup = BeautifulSoup (html_content, features="html.parser") # PARSER: analizar y convertir datos estructurados (como texto)
soup
#print(soup)

#Buscar todas las tablas.
table = soup.find("table")  
table


#Almacena los datos en un DataFrame.
database = []                                           
for row in tqdm(table.findAll('tr')[1:]):
    year = row.findAll('td')[0].find('span').text.strip() 
    revenue = row.findAll('td')[1].text.strip().replace('$', '').replace('B', '').strip() #limpia las filas para obtener los valores limpios eliminando $ y B
    database.append([year, revenue])

#print(database)

df = pd.DataFrame(database, columns=["Year", "Revenue"])
df = df.sort_values("Year", ascending=False)

print(df)


#Paso 5: Almacena los datos en sqlite
import sqlite3

conn = sqlite3.connect("revenues.db")
cur = conn.cursor()   # create a Cursor object

#CREATE TABLE IF NOT EXISTS revenues;     Crear tabla si no existe, esto permite ejecutar sin problemas varias veces
# Year INTEGER PRIMARY KEY,;   La clave primaria en Year me garantiza que cada fila en la tabla sea única y no hayan mas registros de ese año.

cur.execute('''
    CREATE TABLE IF NOT EXISTS revenues (
        Year INTEGER PRIMARY KEY,
        Revenue REAL
    )
''')

#Insertar datos 

for index, row in df.iterrows():
    cur.execute('''
        INSERT INTO revenues (Year, Revenue)
        VALUES (?, ?)
        ON CONFLICT(Year) DO UPDATE SET Revenue=excluded.Revenue
    ''', (int(row["Year"]), float(row["Revenue"])))


# Confirmar (commit) los cambios
conn.commit()

# Comprobar el contenido de la tabla
cur.execute("SELECT * FROM revenues")
rows = cur.fetchall()
for row in rows:
    print(row)

# Cerrar la conexión
conn.close()