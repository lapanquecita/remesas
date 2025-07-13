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
    df = df.iloc[2].to_frame("TOTAL")

    # Quitamos filas inválidas.
    df = df.dropna(axis=0)

    # COnvertimos las cifras de millones de dólares a dólares.
    df["TOTAL"] = df["TOTAL"].astype(float) * 1000000
    df["TOTAL"] = df["TOTAL"].astype(int)

    # Convertimos el índice a formato ISO.
    df.index = df.index.map(arreglar_fecha)
    df.index.name = "PERIODO"

    # Guardamos el archivo en la carpeta data.
    df.to_csv("./data/remesas_mensuales.csv", encoding="utf-8")


def arreglar_fecha(x):
    mes, año = x.split()
    return f"{año}-{MESES[mes]}-01"


if __name__ == "__main__":
    # descargar_ipc()
    # descargar_tipo_cambio()
    descargar_remesas_mensuales()
