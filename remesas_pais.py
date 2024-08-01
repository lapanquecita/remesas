"""

Esta script crea 3 imágenes, una con los 30 países que aportan más a las remesas, una de los países que aportan menos y un mapa con todas las aportaciones.

Fuente:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CE167&sector=1&locale=es

"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go


# Códigos usados para enlazar los países con el mapa.
CODIGOS_ISO3 = {
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
    "República de Abjasia": "ABH",
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
}

# Mes y año en que se recopilaron los datos.
FECHA_FUENTE = "agosto 2024"

# Periodo de tiempo del análisis.
PERIODO_TIEMPO = "enero-diciembre"


def plot_top(año):
    """
    Esta función crea una gráfica de los países con mayor aportación a las remesas.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    """

    # Cargamos el archivo CSV de remesas por país.
    df = pd.read_csv("./data/remesas_pais.csv", index_col=0)

    # Seleccionamos las columnas del año que nos interesa.
    columnas = [col for col in df.columns if str(año) in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[columnas]

    # Sumamos todas las columnas.
    df = df.sum(axis=1).to_frame("total")

    # Quitamos la primera fila (total)
    df = df.iloc[1:]

    # Quitamos los decimales de las cifras.
    df["total"] = df["total"] * 1000000

    # Calculamos el porcentaje relativo al total de remesas.
    df["perc"] = df["total"] / df["total"].sum() * 100

    # Creamos el texto que irá en cada barra.
    df["text"] = df.apply(lambda x: f" ${x['total']:,.0f} ({x['perc']:,.4f}%) ", axis=1)

    # ordenamos el DAtaframe de mayor a menor cantidad de remesas.
    df = df.sort_values("total", ascending=False)

    # Algunos nombres son muy largos, abreviaremos la palarba República y los partiremos en 2 líneas.
    df.index = df.index.str.replace("República", "Rep.")
    df.index = df.index.str.wrap(22).str.replace("\n", "<br>")

    # Seleccionamos las primeras 30 filas.
    df = df[:30]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["total"],
            text=df["text"],
            textfont_color="#FFFFFF",
            textposition=["inside"] + ["outside" for _ in range(len(df) - 1)],
            orientation="h",
            marker_color="#0277bd",
        )
    )

    # Data la grana diferencia entre valores, usaremos una escala logarítmica.
    # En vez de usar billón para mil millones, usaremos giga.
    fig.update_xaxes(
        exponentformat="SI",
        type="log",
        range=[5, np.log10(df["total"].max() * 1.05)],
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        zeroline=False,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        tickfont_color="#FFFFFF",
        autorange="reversed",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=False,
        gridwidth=0.5,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=1280,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=16,
        title_text=f"Los 30 países que aportaron los <b>mayores ingresos</b> por remesas hacia México<br>durante {PERIODO_TIEMPO} de {año}",
        title_x=0.5,
        title_y=0.965,
        margin_t=100,
        margin_r=40,
        margin_b=90,
        margin_l=170,
        title_font_size=26,
        plot_bgcolor="#111111",
        paper_bgcolor="#282A3A",
        annotations=[
            dict(
                x=0.98,
                y=0.01,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="bottom",
                align="left",
                bordercolor="#FFFFFF",
                borderwidth=1.5,
                borderpad=7,
                bgcolor="#111111",
                text="<b>Nota:</b><br>Se utilizó una escala logarítmica<br>dada la gran diferencia entre valores.",
            ),
            dict(
                x=0.01,
                y=-0.075,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.55,
                y=-0.075,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Dólares estadounidenses (proporción respecto al total de remesas)",
            ),
            dict(
                x=1.01,
                y=-0.075,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./remesas_pais_top.png")


def plot_bottom(año):
    """
    Esta función crea una gráfica de los países con menor aportación a las remesas.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    """
    # Cargamos el archivo CSV de remesas por país.
    df = pd.read_csv("./data/remesas_pais.csv", index_col=0)

    # Seleccionamos las columnas del año que nos interesa.
    columnas = [col for col in df.columns if str(año) in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[columnas]

    # Sumamos todas las columnas.
    df = df.sum(axis=1).to_frame("total")

    # Quitamos la primera fila (total)
    df = df.iloc[1:]

    # Quitamos los decimales de las cifras.
    df["total"] = df["total"] * 1000000

    # Creamos el texto que irá en cada barra.
    df["text"] = df.apply(lambda x: f" ${x['total']:,.0f} ", axis=1)

    # Ordenamos los valores de menor a mayor y quitamos los registros en cero.
    df = df.sort_values("total")
    df = df[df["total"] != 0]

    # Algunos nombres son muy largos, los partiremos en 2 líneas.
    df.index = df.index.str.wrap(18).str.replace("\n", "<br>")

    # Seleccionamos las primeras 30 filas.
    df = df[:30]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["total"],
            text=df["text"],
            textfont_color="#FFFFFF",
            textposition=["outside" for _ in range(len(df) - 1)] + ["inside"],
            orientation="h",
            marker_color="#e65100",
            marker_line_width=0,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        range=[0, df["total"].max() * 1.01],
        separatethousands=True,
        ticklen=10,
        zeroline=False,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        tickfont_color="#FFFFFF",
        autorange="reversed",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=False,
        gridwidth=0.5,
        showline=True,
        nticks=40,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=1280,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=16,
        title_text=f"Los 30 países que aportaron los <b>menores ingresos</b> por remesas hacia México<br>durante {PERIODO_TIEMPO} de {año}",
        title_x=0.5,
        title_y=0.965,
        margin_t=100,
        margin_r=40,
        margin_b=90,
        margin_l=170,
        title_font_size=26,
        plot_bgcolor="#111111",
        paper_bgcolor="#282A3A",
        annotations=[
            dict(
                x=0.98,
                y=0.95,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                align="left",
                bordercolor="#FFFFFF",
                borderwidth=1.5,
                borderpad=7,
                bgcolor="#111111",
                text="<b>Nota:</b><br>No se tomaron en cuenta los países<br>que reportaron remesas en cero.",
            ),
            dict(
                x=0.01,
                y=-0.075,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.075,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Dólares estadounidenses",
            ),
            dict(
                x=1.01,
                y=-0.075,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./remesas_pais_bottom.png")


def plot_map(año):
    """
    Esta función crea un mapa de las aportaciones a las remesas por país de origen.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    """

    # Cargamos el archivo CSV de remesas por país.
    df = pd.read_csv("./data/remesas_pais.csv", index_col=0)

    # Seleccionamos las columnas del año que nos interesa.
    columnas = [col for col in df.columns if str(año) in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[columnas]

    # Descartamos la primera fila.
    df = df.iloc[1:]

    # Sumamos todas las columnas.
    df = df.sum(axis=1).to_frame("total")

    # Quitamos los decimales de las cifras.
    df["total"] = df["total"] * 1000000

    # Quitamos todos los valores en cero.
    df = df[df["total"] != 0]

    # Obtenemos los valores logarítmicos.
    df["log"] = np.log10(df["total"])

    # Creamos la escala logarítmica usando el valor máximo y mínimo en nuestro dataset.
    min_value = df["log"].min()
    max_value = df["log"].max()

    # Creamos las marcas para la escala.
    marcas = np.arange(np.floor(min_value), np.ceil(max_value))

    textos = list()

    # Convertiremos los textos a base 10.
    for item in marcas:
        v, e = f"{10 ** item:e}".split("e")
        textos.append(f"{10* float(v):.0f}<sup>{int(e)-1}</sup>")

    # Agregamos los códigos ISO3 de cada país.
    df["iso3"] = df.index.map(CODIGOS_ISO3)

    fig = go.Figure()

    fig.add_traces(
        go.Choropleth(
            locations=df["iso3"],
            z=df["log"],
            colorscale="portland",
            marker_line_color="#FFFFFF",
            showscale=True,
            showlegend=False,
            marker_line_width=2,
            zmax=max_value,
            zmin=min_value,
            colorbar=dict(
                x=0.03,
                y=0.42,
                thickness=150,
                ypad=840,
                ticks="outside",
                outlinewidth=5,
                outlinecolor="#FFFFFF",
                tickwidth=5,
                tickcolor="#FFFFFF",
                ticklen=30,
                tickfont_size=80,
                tickvals=marcas,
                ticktext=textos,
            ),
        )
    )

    fig.update_geos(
        showocean=True,
        oceancolor="#082032",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        legend_bgcolor="#111111",
        legend_font_size=100,
        legend_bordercolor="#FFFFFF",
        legend_borderwidth=2,
        font_family="Lato",
        font_color="#FFFFFF",
        margin_t=240,
        margin_r=100,
        margin_b=0,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor="#282A3A",
        annotations=[
            dict(
                x=0.5,
                y=1.045,
                xanchor="center",
                yanchor="top",
                text=f"Ingresos totales por remesas hacia México por país de origen durante {PERIODO_TIEMPO} de {año}",
                font_size=140,
            ),
            dict(
                x=0.02,
                y=0.16,
                textangle=270,
                xanchor="left",
                yanchor="middle",
                text="Dólares estadounidenses (escala logarítmica)",
                font_size=90,
            ),
            dict(
                x=0.001,
                y=-0.065,
                xanchor="left",
                yanchor="bottom",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
                font_size=120,
            ),
            dict(
                x=0.5,
                y=-0.065,
                xanchor="center",
                yanchor="bottom",
                text=f"Ingreso total por remesas: {df['total'].sum():,.0f} dólares",
                font_size=120,
            ),
            dict(
                x=1.0,
                y=-0.065,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
                font_size=120,
            ),
        ],
    )

    fig.write_image("./mapa_paises.png")


if __name__ == "__main__":
    plot_top(2023)
    plot_bottom(2023)
    plot_map(2023)
