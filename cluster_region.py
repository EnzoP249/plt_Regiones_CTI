# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 10:35:18 2026

@author: Enzo
"""

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
# -----------------------------
# 1. Copia del dataframe
# -----------------------------
region = pd.read_excel("bd_capacidades_regionales_cti.xlsx", sheet_name="Hoja1", header=0)
df_ml = region.copy()

# Se analiza la estructura del dataframe df_ml
df_ml.shape
df_ml.columns
df_ml.info()

# -----------------------------
# 2. Definir columna identificadora
# -----------------------------
col_region = "Departamento"   # cambia esto por el nombre real de tu columna

# Por el momento, no se considerará Lima
df_ml = df_ml[df_ml["Departamento"] != "LIMA"]


# -----------------------------
# 3. Seleccionar variables numéricas
# -----------------------------
X = df_ml.drop(columns=[col_region]).select_dtypes(include=[np.number])

# Validación básica
if X.isnull().sum().sum() > 0:
    X = X.fillna(X.median())

# -----------------------------
# 4. Estandarizar
# -----------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -----------------------------
# 5. Evaluar varios valores de k
# -----------------------------
resultados = []

for k in range(2, 7):   # por ejemplo de 2 a 6 clusters
    kmeans = KMeans(
        n_clusters=k,
        init="k-means++",
        n_init=20,
        max_iter=300,
        random_state=42
    )
    labels = kmeans.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels)
    resultados.append({
        "k": k,
        "silhouette_score": sil,
        "inercia": kmeans.inertia_
    })

df_resultados = pd.DataFrame(resultados)
print(df_resultados)

# -----------------------------
# 6. Elegir un k
# -----------------------------
k_optimo = 3   # cámbialo según tus resultados

kmeans_final = KMeans(
    n_clusters=k_optimo,
    init="k-means++",
    n_init=20,
    max_iter=300,
    random_state=42
)

df_ml["cluster"] = kmeans_final.fit_predict(X_scaled)


score = silhouette_score(X_scaled, labels)
print("Silhouette:", score)

# -----------------------------
# 7. Ver regiones por cluster
# -----------------------------
print(df_ml[[col_region, "cluster"]].sort_values("cluster"))

# -----------------------------
# 8. Tamaño de cada cluster
# -----------------------------
print(df_ml["cluster"].value_counts().sort_index())

# -----------------------------
# 9. Perfil promedio por cluster
# -----------------------------
perfil_clusters = df_ml.groupby("cluster")[X.columns].mean()
print(perfil_clusters)


conteo = df_ml["cluster"].value_counts().sort_index()

plt.figure(figsize=(6,4))
conteo.plot(kind="bar")
plt.xlabel("Cluster")
plt.ylabel("Número de regiones")
plt.title("Distribución de regiones por cluster")
plt.show()


import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# -----------------------------
# 1. PCA
# -----------------------------
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# -----------------------------
# 2. Construir índice de capacidad
# -----------------------------
df_ml["indice_capacidad"] = X_scaled.mean(axis=1)

# -----------------------------
# 3. Ordenar clusters por capacidad
# -----------------------------
orden = df_ml.groupby("cluster")["indice_capacidad"].mean().sort_values()

# Mapping cluster -> nivel
mapping = {
    orden.index[0]: "Débiles capacidades",
    orden.index[1]: "Capacidades emergentes",
    orden.index[2]: "Altas capacidades"
}

df_ml["nivel_capacidad"] = df_ml["cluster"].map(mapping)

# -----------------------------
# 4. Definir colores
# -----------------------------
colors = {
    "Altas capacidades": "#1D3557",        # azul oscuro
    "Capacidades emergentes": "#2A9D8F",   # verde
    "Débiles capacidades": "#E63946"       # rojo
}

# -----------------------------
# 5. Gráfico
# -----------------------------
plt.figure(figsize=(10,7))

for nivel in ["Altas capacidades", "Capacidades emergentes", "Débiles capacidades"]:
    idx = df_ml["nivel_capacidad"] == nivel
    
    plt.scatter(
        X_pca[idx, 0],
        X_pca[idx, 1],
        label=nivel,
        color=colors[nivel],
        s=80,
        edgecolor="black"
    )

# -----------------------------
# 6. Etiquetas (regiones)
# -----------------------------
for i, txt in enumerate(df_ml["Departamento"]):
    plt.annotate(
        txt,
        (X_pca[i,0], X_pca[i,1]),
        fontsize=8,
        xytext=(3,3),
        textcoords="offset points"
    )

# -----------------------------
# 7. Estética
# -----------------------------
plt.axhline(0, linestyle="--", linewidth=0.5, color="gray")
plt.axvline(0, linestyle="--", linewidth=0.5, color="gray")

plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% varianza)")
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% varianza)")

plt.title("Estructura de capacidades regionales (CTI)", fontsize=13)

plt.legend(title="Nivel de capacidad")
plt.grid(alpha=0.2)
plt.tight_layout()

plt.show()




# Se elabora un indice de capacidades en ciencia, tecnología e innovación
df_ml["indice_capacidad"] = X_scaled.mean(axis=1)

q1 = df_ml["indice_capacidad"].quantile(0.33)
q2 = df_ml["indice_capacidad"].quantile(0.66)


def clasificar(x):
    if x <= q1:
        return "Baja capacidad"
    elif x <= q2:
        return "Emergente"
    else:
        return "Alta capacidad"

df_ml["nivel_capacidad"] = df_ml["indice_capacidad"].apply(clasificar)


###############################################################################
# Se realiza un análisis de la información descarga del portal Consulta CEPLAN
###############################################################################

# Se procesa la información de los Gobiernos Regionales
gores1 = pd.read_csv("ao_aei_oei_todos_los_gore.csv", encoding="utf-8", delimiter=",")
gores2 = pd.read_csv("ao_aei_oei_departamento.csv", encoding="utf-8", delimiter=",")

gores = pd.concat([gores1, gores2], axis=0)

# Se valida una instancia del dataframe gores
caso = gores[gores["oei"]=="OEI.04-440: PROMOVER LA COMPETITIVIDAD ECONÓMICA CON ENFOQUE DE INVESTIGACIÓN; DESARROLLO E INNOVACIÓN EN EL DEPARTAMENTO"]


import pandas as pd
import re
import unicodedata

# -----------------------------
# 1. Función para normalizar texto
#    - pasa a minúsculas
#    - elimina tildes
# -----------------------------
def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto

# -----------------------------
# 2. Crear versiones normalizadas de OEI y AEI
# -----------------------------
gores["oei_norm"] = gores["oei"].apply(normalizar_texto)
gores["aei_norm"] = gores["aei"].apply(normalizar_texto)

# -----------------------------
# 3. Definir palabras clave
# -----------------------------
palabras_clave = ["ciencia", "tecnologia", "innovacion"]

# regex: busca cualquiera de las palabras
patron = r"\b(" + "|".join(map(re.escape, palabras_clave)) + r")\b"

# -----------------------------
# 4. Buscar coincidencias en oei o aei
# -----------------------------
mask = (
    gores["oei_norm"].str.contains(patron, regex=True, na=False) |
    gores["aei_norm"].str.contains(patron, regex=True, na=False)
)

df_cti = gores.loc[mask].copy()

# -----------------------------
# 5. Resultado
# -----------------------------
print(df_cti[["departamento", "oei", "aei"]])
print("Total de filas encontradas:", len(df_cti))

###############################################################################
###############################################################################
###############################################################################

import pandas as pd
import unicodedata

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto

gores["oei_norm"] = gores["oei"].apply(normalizar_texto)
gores["aei_norm"] = gores["aei"].apply(normalizar_texto)
gores["texto_busqueda"] = gores["oei_norm"] + " " + gores["aei_norm"]

terminos_cti = [
    "ciencia",
    "cientific",
    "tecnologia",
    "tecnologic",
    "innovacion",
    "innovador",
    "investigacion",        
    "cti",
    "i+d"
]

def score_cti(texto):
    score = 0
    coincidencias = []
    for termino in terminos_cti:
        if termino in texto:
            score += 1
            coincidencias.append(termino)
    return pd.Series([score, ", ".join(coincidencias)])

gores[["score_cti", "coincidencias_cti"]] = gores["texto_busqueda"].apply(score_cti)

df_cti = gores[gores["score_cti"] > 0].copy()

print(df_cti[["departamento", "oei", "aei", "score_cti", "coincidencias_cti"]].to_string())

# Se cuentan los gobiernos regionales
df_cti["departamento"].nunique()
version = df_cti.drop_duplicates(subset=["departamento"])
print(version["departamento"])

###############################################################################
###############################################################################
###############################################################################

import pandas as pd
import unicodedata

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto

gores["oei_norm"] = gores["oei"].apply(normalizar_texto)
gores["aei_norm"] = gores["aei"].apply(normalizar_texto)
gores["actividad_operativa_norm"] = gores["actividad_operativa"].apply(normalizar_texto)
gores["texto_busqueda"] = gores["oei_norm"] + " " + gores["aei_norm"]


terminos_cti = [
    "instrumentos de innovacion",
    "Clubes de Ciencia y Tecnologia",
    "adopcion de tecnologias",
    "tecnologic"    
]

def score_cti(texto):
    score = 0
    coincidencias = []
    for termino in terminos_cti:
        if termino in texto:
            score += 1
            coincidencias.append(termino)
    return pd.Series([score, ", ".join(coincidencias)])

gores[["score_cti", "coincidencias_cti"]] = gores["texto_busqueda"].apply(score_cti)

df_cti = gores[gores["score_cti"] > 0].copy()

print(df_cti[["departamento", "oei", "aei", "score_cti", "coincidencias_cti"]].to_string())

# Se cuentan los gobiernos regionales
df_cti["departamento"].nunique()
version = df_cti.drop_duplicates(subset=["departamento"])
print(version["departamento"])







