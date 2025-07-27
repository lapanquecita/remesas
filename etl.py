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
REMESAS_PAIS_ORIGEN_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=1&accion=consultarCuadro&idCuadro=CE167&locale=es&formatoXLS.x=1&fechaInicio={}&fechaFin={}"
REMESAS_PAIS_DESTINO_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CE169&locale=es&formatoXLS.x=1&fechaInicio={}&fechaFin={}"
REMESAS_MUNICIPIO_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=1&accion=consultarCuadro&idCuadro=CE166&locale=es&formatoXLS.x=1&fechaInicio={}&fechaFin={}"
REMESAS_USA_URL = "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=1&accion=consultarCuadro&idCuadro=CE168&locale=es&formatoXLS.x=1&fechaInicio={}&fechaFin={}"

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
}

ENTIDADES_INVERSO = {v: k for k, v in ENTIDADES.items()}


PAISES = {
    "Afganistán": "AFG",
    "Albania": "ALB",
    "Alemania": "DEU",
    "Angola": "AGO",
    "Anguila": "AIA",
    "Antigua y Barbuda": "ATG",
    "Antillas Holandesas": "ANT",
    "Arabia Saudita": "SAU",
    "Argelia": "DZA",
    "Argentina": "ARG",
    "Armenia": "ARM",
    "Aruba": "ABW",
    "Australia": "AUS",
    "Austria": "AUT",
    "Azerbaiyán": "AZE",
    "Bahamas": "BHS",
    "Bahrein": "BHR",
    "Bangladesh": "BGD",
    "Barbados": "BRB",
    "Bélgica": "BEL",
    "Belice": "BLZ",
    "Benín": "BEN",
    "Bermudas": "BMU",
    "Bielorrusia": "BLR",
    "Bolivia": "BOL",
    "Bonaire": "BES",
    "Bosnia-Herzegovina": "BIH",
    "Botswana": "BWA",
    "Brasil": "BRA",
    "Brunei": "BRN",
    "Bulgaria": "BGR",
    "Burkina Faso": "BFA",
    "Burundi": "BDI",
    "Bután": "BTN",
    "Cabo Verde": "CPV",
    "Camboya": "KHM",
    "Camerún": "CMR",
    "Canadá": "CAN",
    "Chad": "TCD",
    "Chile": "CHL",
    "China": "CHN",
    "Chipre": "CYP",
    "Cisjordania": "PSE",
    "Colombia": "COL",
    "Comores": "COM",
    "Corea del Norte": "PRK",
    "Corea del Sur": "KOR",
    "Costa de Marfil": "CIV",
    "Costa Rica": "CRI",
    "Croacia": "HRV",
    "Cuba": "CUB",
    "Curazao": "CUW",
    "Dinamarca": "DNK",
    "Djibouti": "DJI",
    "Dominica": "DMA",
    "Ecuador": "ECU",
    "Egipto": "EGY",
    "El Salvador": "SLV",
    "Emiratos Árabes Unidos": "ARE",
    "Eslovaquia": "SVK",
    "Eslovenia": "SVN",
    "España": "ESP",
    "Estados Unidos": "USA",
    "Estonia": "EST",
    "Etiopía": "ETH",
    "Federación Rusa": "RUS",
    "Filipinas": "PHL",
    "Finlandia": "FIN",
    "Fiyi": "FJI",
    "Francia": "FRA",
    "Gabón": "GAB",
    "Gambia": "GMB",
    "Georgia": "GEO",
    "Ghana": "GHA",
    "Gibraltar": "GIB",
    "Granada": "GRD",
    "Grecia": "GRC",
    "Guadalupe": "GLP",
    "Guam": "GUM",
    "Guatemala": "GTM",
    "Guayana Francesa": "GUF",
    "Guinea Bisáu": "GNB",
    "Guinea Ecuatorial": "GNQ",
    "Guyana": "GUY",
    "Haití": "HTI",
    "Honduras": "HND",
    "Hong Kong": "HKG",
    "Hungría": "HUN",
    "India": "IND",
    "Indonesia": "IDN",
    "Iraq": "IRQ",
    "Irlanda": "IRL",
    "Isla de San Martín": "SXM",
    "Islandia": "ISL",
    "Islas Caimán": "CYM",
    "Islas Cocos": "CCK",
    "Islas Cook": "COK",
    "Islas Marshall": "MHL",
    "Islas Salomón": "SLB",
    "Islas Turcas y Caicos": "TCA",
    "Islas Virgenes Americanas": "VIR",
    "Islas Virgenes Británicas": "VGB",
    "Israel": "ISR",
    "Italia": "ITA",
    "Jamaica": "JAM",
    "Japón": "JPN",
    "Jordania": "JOR",
    "Kazajistán": "KAZ",
    "Kenia": "KEN",
    "Kirguistán": "KGZ",
    "Kiribati": "KIR",
    "Kosovo": "XKX",
    "Kuwait": "KWT",
    "Laos": "LAO",
    "Letonia": "LVA",
    "Líbano": "LBN",
    "Liberia": "LBR",
    "Libia": "LBY",
    "Liechtenstein": "LIE",
    "Lituania": "LTU",
    "Luxemburgo": "LUX",
    "Macao": "MAC",
    "Macedonia": "MKD",
    "Madagascar": "MDG",
    "Malasia": "MYS",
    "Malawi": "MWI",
    "Maldivas": "MDV",
    "Malí": "MLI",
    "Malta": "MLT",
    "Marianas del Norte": "MNP",
    "Marruecos": "MAR",
    "Martinica": "MTQ",
    "Mauricio": "MUS",
    "Mauritania": "MRT",
    "Moldavia": "MDA",
    "Mónaco": "MCO",
    "Mongolia": "MNG",
    "Montenegro": "MNE",
    "Montserrat": "MSR",
    "Mozambique": "MOZ",
    "Myanmar, Birmania": "MMR",
    "Namibia": "NAM",
    "Nepal": "NPL",
    "Nicaragua": "NIC",
    "Niger": "NER",
    "Nigeria": "NGA",
    "Niue": "NIU",
    "Noruega": "NOR",
    "Nueva Caledonia": "NCL",
    "Nueva Zelanda": "NZL",
    "Omán": "OMN",
    "Países Bajos": "NLD",
    "Pakistán": "PAK",
    "Palaos": "PLW",
    "Palestina": "PSE",
    "Panamá": "PAN",
    "Papúa-Nueva Guinea": "PNG",
    "Paraguay": "PRY",
    "Perú": "PER",
    "Polinesia Francesa": "PYF",
    "Polonia": "POL",
    "Portugal": "PRT",
    "Qatar": "QAT",
    "Reino de Lesoto": "LSO",
    "Reino Unido": "GBR",
    "República Centroafricana": "CAF",
    "República Checa": "CZE",
    "República de Abjasia": "ABK",
    "República del Congo": "COG",
    "República Democrática del Congo": "COD",
    "República Dominicana": "DOM",
    "República Guinea": "GIN",
    "Reunión": "REU",
    "Ruanda": "RWA",
    "Rumanía": "ROU",
    "Samoa": "WSM",
    "San Cristobal y Nevis": "KNA",
    "San Marino": "SMR",
    "San Vincente y Granadinas": "VCT",
    "Santa Lucía": "LCA",
    "Santo Tomé y Príncipe": "STP",
    "Senegal": "SEN",
    "Serbia": "SRB",
    "Sierra Leona": "SLE",
    "Singapur": "SGP",
    "Siria": "SYR",
    "Sri Lanka": "LKA",
    "Sudáfrica": "ZAF",
    "Sudán": "SDN",
    "Suecia": "SWE",
    "Suiza": "CHE",
    "Surinam": "SUR",
    "Swazilandia": "SWZ",
    "Tailandia": "THA",
    "Taiwan": "TWN",
    "Tanzania": "TZA",
    "Tayikistán": "TJK",
    "Timor Oriental": "TLS",
    "Togo": "TGO",
    "Trinidad y Tobago": "TTO",
    "Túnez": "TUN",
    "Turkmenistán": "TKM",
    "Turquía": "TUR",
    "Tuvalu": "TUV",
    "Ucrania": "UKR",
    "Uganda": "UGA",
    "Uruguay": "URY",
    "Uzbekistán": "UZB",
    "Vanuatu": "VUT",
    "Venezuela": "VEN",
    "Vietnam": "VNM",
    "Yemen": "YEM",
    "Zambia": "ZMB",
    "Zimbabwe": "ZWE",
    "No Identificado": "XXX",
}


ABREVIACIONES_USA = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Luisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississipi": "MS",
    "Misuri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "Nuevo Hampshire": "NH",
    "Nueva Jersey": "NJ",
    "Nuevo Mexico": "NM",
    "Nueva York": "NY",
    "Carolina Del Norte": "NC",
    "Dakota Del Norte": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pensilvania": "PA",
    "Puerto Rico": "PR",
    "Rhode Island": "RI",
    "Carolina Del Sur": "SC",
    "Dakota Del Sur": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "Washington, D.C.": "DC",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "No Identificado": "XX",
}


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
    df = df.iloc[2].to_frame("VALOR_USD")

    # Quitamos filas inválidas.
    df = df.dropna(axis=0)

    # COnvertimos las cifras de millones de dólares a dólares.
    df["VALOR_USD"] = df["VALOR_USD"].astype(float) * 1000000
    df["VALOR_USD"] = df["VALOR_USD"].astype(int)

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
        temp_df = df[entidad].to_frame("VALOR_USD")
        temp_df["CVE_ENT"] = ENTIDADES_INVERSO[nombre_entidad]
        temp_df["ENTIDAD"] = nombre_entidad

        dfs.append(temp_df)

    # Unimos los DataFrames de cada entidad en uno solo.
    final = pd.concat(dfs)

    # Reseteamos el índice.
    final.reset_index(names=["PERIODO"], inplace=True)

    # Arregalmos algunas columnas.
    final["PERIODO"] = final["PERIODO"].apply(arreglar_fecha_trimestre)
    final["VALOR_USD"] = final["VALOR_USD"].astype(float) * 1000000
    final["VALOR_USD"] = final["VALOR_USD"].astype(int)

    # Ordenamos las columnas.
    final = final[["PERIODO", "CVE_ENT", "ENTIDAD", "VALOR_USD"]]

    # Ordenamos todo el DataFrame.
    final.sort_values(list(final.columns), inplace=True)

    # Guardamos el archivo en la carpeta data.
    final.to_csv("./data/remesas_entidad.csv", index=False, encoding="utf-8")


def descargar_remesas_pais():
    """
    Descarga los ingresos trimestrales por remesas
    según entidad de destino.
    """

    # Cargamos el archivo Excel del origen de las remesas por país.
    df1 = pd.read_excel(
        REMESAS_PAIS_ORIGEN_URL.format(ENERO_1991, FECHA_FIN), skiprows=9, index_col=1
    )

    # Cargamos el archivo Excel del destino de las remesas por país.
    df2 = pd.read_excel(
        REMESAS_PAIS_DESTINO_URL.format(ENERO_1991, FECHA_FIN), skiprows=9, index_col=1
    )

    dfs = list()

    # Seleccionamos las filas y columnas necesarias.
    df1 = df1.iloc[2:-2, 1:].transpose()
    df2 = df2.iloc[2:-2, 1:].transpose()

    # Iteramos sobre cada país.
    for pais in df1.columns:
        nombre_pais = pais[3:].strip()

        # Creamos un DataFrame temporal y llenamos los valores necesarios.
        temp_df = df1[pais].to_frame("VALOR_USD")
        temp_df["ID_PAIS"] = PAISES[nombre_pais]
        temp_df["PAIS"] = nombre_pais
        temp_df["ID_FLUJO"] = 1
        temp_df["FLUJO"] = "Ingresos"

        dfs.append(temp_df)

    # Iteramos sobre cada país.
    for pais in df2.columns:
        nombre_pais = pais[3:].strip()

        # Creamos un DataFrame temporal y llenamos los valores necesarios.
        temp_df = df2[pais].to_frame("VALOR_USD")
        temp_df["ID_PAIS"] = PAISES[nombre_pais]
        temp_df["PAIS"] = nombre_pais
        temp_df["ID_FLUJO"] = 2
        temp_df["FLUJO"] = "Egresos"

        dfs.append(temp_df)

    # Unimos los DataFrames de cada entidad en uno solo.
    final = pd.concat(dfs)

    # Reseteamos el índice.
    final.reset_index(names=["PERIODO"], inplace=True)

    # Arregalmos algunas columnas.
    final["PERIODO"] = final["PERIODO"].apply(arreglar_fecha_trimestre)
    final["VALOR_USD"] = final["VALOR_USD"].astype(float) * 1000000
    final["VALOR_USD"] = final["VALOR_USD"].astype(int)

    # Ordenamos las columnas.
    final = final[["PERIODO", "ID_PAIS", "PAIS", "ID_FLUJO", "FLUJO", "VALOR_USD"]]

    # Ordenamos todo el DataFrame.
    final.sort_values(list(final.columns), inplace=True)

    # Guardamos el archivo en la carpeta data.
    final.to_csv("./data/remesas_pais.csv", index=False, encoding="utf-8")


def descargar_remesas_municipio():
    """
    Descarga los ingresos trimestrales por remesas
    según municipio de destino.
    """

    # Vamos a crear un DataFrame con los municipios no identificados.
    data = list()

    for k, v in ENTIDADES.items():
        data.append({"CVE": f"{k:02}999", "Entidad": v, "Municipio": "No identificado"})

    no_identificados = pd.DataFrame.from_records(data)

    # Cargamos el diccionario de municipios.
    municipios = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str})

    # Solo necesitaremos las primeras 3 columnas.
    municipios = municipios.iloc[:, :3]

    # Agregamos los municipios no identificados.
    municipios = pd.concat([municipios, no_identificados])

    # Peparamos el diccionario.
    municipios.index = municipios["Municipio"] + "@" + municipios["Entidad"]

    # Para este diccionario nuestros valores serán el código del municipio.
    municipios = municipios["CVE"]

    df = pd.read_excel(
        REMESAS_MUNICIPIO_URL.format(ENERO_1991, FECHA_FIN), skiprows=9, index_col=1
    )

    dfs = list()

    # La primera columna no tiene nombre fijo.
    # Nos vamos a referir a esta de forma dinámica.
    primera_columna = df.columns[0]

    # Vamos a extraer el nombre del estado.
    # Las filas con ● son estados.
    df[primera_columna] = df.index.map(lambda x: x if "●" in x else None)
    df[primera_columna] = df[primera_columna].fillna(method="ffill")

    # Ya que hemos asignado la entidad para cada municipio
    # solo seleccionaremos filas de municpiios.
    df = df[df.index.str.contains("⚬")]

    # Ahora arreglamos el nombre del municipio.
    df.index = df.apply(
        lambda x: f"{x.name[3:].strip()}@{x[primera_columna][2:].strip()}", axis=1
    )

    # Vamos a corregir los registros del Estado de México.
    df.index = df.index.str.replace("@México", "@Estado de México")

    # Omitimos la primera columna yvolteamos el
    # DataFrame para que los municipios sean las columnas.
    df = df.iloc[:, 1:].transpose()

    # Iteramos sobre cada municipio.
    for municipio in df.columns:
        nombre_municipio, nombre_entidad = municipio.split("@")
        cve_geo = municipios.loc[municipio]

        # Creamos un DataFrame temporal y llenamos los valores necesarios.
        temp_df = df[municipio].to_frame("VALOR_USD")

        temp_df["CVE_GEO"] = cve_geo
        temp_df["ENTIDAD"] = nombre_entidad
        temp_df["MUNICIPIO"] = nombre_municipio

        dfs.append(temp_df)

    # Unimos los DataFrames de cada entidad en uno solo.
    final = pd.concat(dfs)

    # Reseteamos el índice.
    final.reset_index(names=["PERIODO"], inplace=True)

    # Arregalmos algunas columnas.
    final["PERIODO"] = final["PERIODO"].apply(arreglar_fecha_trimestre)
    final["VALOR_USD"] = final["VALOR_USD"].astype(float) * 1000000
    final["VALOR_USD"] = final["VALOR_USD"].astype(int)

    # Ordenamos las columnas.
    final = final[["PERIODO", "CVE_GEO", "ENTIDAD", "MUNICIPIO", "VALOR_USD"]]

    # Ordenamos todo el DataFrame.
    final.sort_values(list(final.columns), inplace=True)

    # Guardamos el archivo en la carpeta data.
    final.to_csv("./data/remesas_municipio.csv", index=False, encoding="utf-8")


def descargar_remesas_usa():
    """
    Descarga los ingresos trimestrales por remesas
    provenientes de Estados Unidos según estado de origen.
    """

    df = pd.read_excel(
        REMESAS_USA_URL.format(ENERO_1991, FECHA_FIN), skiprows=9, index_col=1
    )

    dfs = list()

    # Seleccionamos las filas y columnas necesarias.
    df = df.iloc[2:55, 1:].transpose()

    # Iteramos sobre cada estado.
    for estado in df.columns:
        nombre_estado = estado[3:].strip()

        # Creamos un DataFrame temporal y llenamos los valores necesarios.
        temp_df = df[estado].to_frame("VALOR_USD")
        temp_df["ID_ESTADO"] = ABREVIACIONES_USA[nombre_estado]
        temp_df["ESTADO"] = nombre_estado

        dfs.append(temp_df)

    # Unimos los DataFrames de cada entidad en uno solo.
    final = pd.concat(dfs)

    # Reseteamos el índice.
    final.reset_index(names=["PERIODO"], inplace=True)

    # Arregalmos algunas columnas.
    final["PERIODO"] = final["PERIODO"].apply(arreglar_fecha_trimestre)
    final["VALOR_USD"] = final["VALOR_USD"].astype(float) * 1000000
    final["VALOR_USD"] = final["VALOR_USD"].astype(int)

    # Ordenamos las columnas.
    final = final[["PERIODO", "ID_ESTADO", "ESTADO", "VALOR_USD"]]

    # Ordenamos todo el DataFrame.
    final.sort_values(list(final.columns), inplace=True)

    # Guardamos el archivo en la carpeta data.
    final.to_csv("./data/remesas_usa.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    descargar_ipc()
    descargar_tipo_cambio()
    descargar_remesas_mensuales()
    descargar_remesas_entidad()
    descargar_remesas_pais()
    descargar_remesas_municipio()
    descargar_remesas_usa()
