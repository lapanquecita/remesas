"""
Este script descarga y limpia los conjuntos de datos
relevantes para el proyecto desde la página de Banxico.
"""

from datetime import datetime

import pandas as pd

# EStos timestamps son utilizados para formar las URLS.
ENERO_1970 = 100000
ENERO_1991 = int(datetime(1991, 1, 1).timestamp() * 1000)

FECHA_FIN = int(datetime(2026, 1, 1).timestamp() * 1000)


IPC_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=8&accion=consultarCuadro&idCuadro=CP154&locale=es&formatoXLS.x=1&fechaInicio={}&fechaFin={}"
TIPO_CAMBIO_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=6&accion=consultarCuadro&idCuadro=CF86&locale=es&formatoXLS.x=1&fechaInicio={}&fechaFin={}"

REMESAS_MENSUALES_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CE81&locale=es&formatoXLS.x=1&fechaInicio={}&fechaFin={}"
REMESAS_ENTIDAD_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=1&accion=consultarCuadro&idCuadro=CE100&locale=es&formatoXLS.x=1&fechaInicio={}&fechaFin={}"

MESES = {
    "Ene": "01",
    "Feb": "02",
    "Mar": "03",
    "Abr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Ago": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dic": "12",
}

TRIMESTRES = {"Ene-Mar": "01", "Abr-Jun": "04", "Jul-Sep": "07", "Oct-Dic": "10"}


ENTIDADES = {
    1: "Aguascalientes",
    2: "Baja California",
    3: "Baja California Sur",
    4: "Campeche",
    5: "Coahuila",
    6: "Colima",
    7: "Chiapas",
    8: "Chihuahua",
    9: "Ciudad de México",
    10: "Durango",
    11: "Guanajuato",
    12: "Guerrero",
    13: "Hidalgo",
    14: "Jalisco",
    15: "Estado de México",
    16: "Michoacán",
    17: "Morelos",
    18: "Nayarit",
    19: "Nuevo León",
    20: "Oaxaca",
    21: "Puebla",
    22: "Querétaro",
    23: "Quintana Roo",
    24: "San Luis Potosí",
    25: "Sinaloa",
    26: "Sonora",
    27: "Tabasco",
    28: "Tamaulipas",
    29: "Tlaxcala",
    30: "Veracruz",
    31: "Yucatán",
    32: "Zacatecas",
    99: "Se desconoce",
}

ENTIDADES_INVERSO = {v: k for k, v in ENTIDADES.items()}


def arreglar_fecha(x):
    mes, año = x.split()
    return f"{año}-{MESES[mes]}-01"


def arreglar_fecha_trimestre(x):
    trimestre, año = x.split()
    return f"{año}-{TRIMESTRES[trimestre]}-01"


def descargar_ipc():
    """
    Descarga el índice de precios al consumidor.
    """

    df = pd.read_excel(IPC_URL.format(ENERO_1970, FECHA_FIN), skiprows=9, index_col=1)

    # Seleccionamos la fila del INPC general.
    df = df.iloc[1].to_frame("IPC")

    # Quitamos filas inválidas.
    df = df.dropna(axis=0)

    # Convertimos el índice a formato ISO.
    df.index = df.index.map(arreglar_fecha)
    df.index.name = "PERIODO"

    # Guardamos el archivo en la carpeta assets.
    df.to_csv("./assets/IPC.csv", encoding="utf-8")


def descargar_tipo_cambio():
    """
    Descarga el tipo de cambio USDMXN.
    """

    df = pd.read_excel(
        TIPO_CAMBIO_URL.format(ENERO_1991, FECHA_FIN), skiprows=9, index_col=1
    )

    # Seleccionamos la fila del tipo de cambio FIX.
    df = df.iloc[3].to_frame("TIPO_CAMBIO")

    # Quitamos filas inválidas.
    df = df.dropna(axis=0)

    # Convertimos el índice a formato ISO.
    df.index = df.index.map(arreglar_fecha)
    df.index.name = "PERIODO"

    # Guardamos el archivo en la carpeta assets.
    df.to_csv("./assets/USDMXN.csv", encoding="utf-8")


def descargar_remesas_mensuales():
    """
    Descarga los ingresos mensuales por remesas.
    """

    df = pd.read_excel(
        REMESAS_MENSUALES_URL.format(ENERO_1991, FECHA_FIN), skiprows=9, index_col=1
    )

    # Seleccionamos la fila del tipo de cambio FIX.
    df = df.iloc[2].to_frame("TOTAL_USD")

    # Quitamos filas inválidas.
    df = df.dropna(axis=0)

    # COnvertimos las cifras de millones de dólares a dólares.
    df["TOTAL_USD"] = df["TOTAL_USD"].astype(float) * 1000000
    df["TOTAL_USD"] = df["TOTAL_USD"].astype(int)

    # Convertimos el índice a formato ISO.
    df.index = df.index.map(arreglar_fecha)
    df.index.name = "PERIODO"

    # Guardamos el archivo en la carpeta data.
    df.to_csv("./data/remesas_mensuales.csv", encoding="utf-8")


def descargar_remesas_entidad():
    """
    Descarga los ingresos trimestrales por remesas
    según entidad de destino.
    """

    df = pd.read_excel(
        REMESAS_ENTIDAD_URL.format(ENERO_1991, FECHA_FIN), skiprows=9, index_col=1
    )

    dfs = list()

    # Seleccionamos las filas y columnas necesarias.
    df = df.iloc[2:34, 1:].transpose()

    # Iteramos sobre cada entidad.
    for entidad in df.columns:
        nombre_entidad = entidad[3:].strip()

        # Creamos un DataFrame temporal y llenamos los valores necesarios.
        temp_df = df[entidad].to_frame("TOTAL_USD")
        temp_df["CVE_ENT"] = ENTIDADES_INVERSO[nombre_entidad]
        temp_df["ENTIDAD"] = nombre_entidad

        dfs.append(temp_df)

    # Unimos los DataFrames de cada entidad en uno solo.
    final = pd.concat(dfs)

    # Reseteamos el índice.
    final.reset_index(names=["PERIODO"], inplace=True)

    # Arregalmos algunas columnas.
    final["PERIODO"] = final["PERIODO"].apply(arreglar_fecha_trimestre)
    final["TOTAL_USD"] = final["TOTAL_USD"].astype(float) * 1000000
    final["TOTAL_USD"] = final["TOTAL_USD"].astype(int)

    # Ordenamos las columnas.
    final = final[["PERIODO", "CVE_ENT", "ENTIDAD", "TOTAL_USD"]]

    # Ordenamos todo el DataFrame.
    final.sort_values(list(final.columns), inplace=True)

    # Guardamos el archivo en la carpeta data.
    final.to_csv("./data/remesas_entidad.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    # descargar_ipc()
    # descargar_tipo_cambio()
    # descargar_remesas_mensuales()
    descargar_remesas_entidad()
