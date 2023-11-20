"""

Esta script genera un mapa con las remesas provenientes de EE. UU. ajustadas con la población estimada de mexicanos viviendo en EE. UU.

Fuente remesas:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=1&accion=consultarCuadro&idCuadro=CE168&locale=es

Fuente población:
https://data.census.gov/table?q=DP05

"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go


# Estas abreviaciones son usadas para enlazar los valores con el amapa.
ABREVIACIONES = {
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
    "Wyoming": "WY"
}

# Población estimada de mexicanos viviendo en cada estado de EE. UU.
# Confirmación obtenida de la American Community Survey (ACS)
POBLACION = {
    "Total": 37235886,
    "Alabama": 145112,
    "Alaska": 22299,
    "Arizona": 2008741,
    "Arkansas": 168405,
    "California": 12699700,
    "Colorado": 906912,
    "Connecticut": 59915,
    "Delaware": 38020,
    "Washington, D.C.": 11457,
    "Florida": 785184,
    "Georgia": 553892,
    "Hawaii": 52485,
    "Idaho": 205294,
    "Illinois": 1757306,
    "Indiana": 356501,
    "Iowa": 153858,
    "Kansas": 286245,
    "Kentucky": 92409,
    "Luisiana": 68788,
    "Maine": 8171,
    "Maryland": 115989,
    "Massachusetts": 50921,
    "Michigan": 384807,
    "Minnesota": 199975,
    "Mississipi": 48306,
    "Misuri": 165835,
    "Montana": 31747,
    "Nebraska": 161125,
    "Nevada": 693197,
    "Nuevo Hampshire": 11442,
    "Nueva Jersey": 231000,
    "Nuevo Mexico": 685330,
    "Nueva York": 469828,
    "Carolina Del Norte": 538184,
    "Dakota Del Norte": 21059,
    "Ohio": 212403,
    "Oklahoma": 354431,
    "Oregon": 473003,
    "Pensilvania": 177215,
    "Rhode Island": 10858,
    "Carolina Del Sur": 165277,
    "Dakota Del Sur": 18624,
    "Tennessee": 219910,
    "Texas": 9721127,
    "Utah": 338842,
    "Vermont": 4026,
    "Virginia": 196543,
    "Washington": 801325,
    "West Virginia": 10905,
    "Wisconsin": 298280,
    "Wyoming": 43678,
    "Puerto Rico": 6062,
}


def plot_usa():
    """
    Crea un mapa Choropleth de EE. UU. con los egresos por remesas per cápita
    de población mexicana.
    """

    # Cargamos el archivo CSV con las remesas provenientes de EE. UU.
    df = pd.read_csv("./data/remesas_usa.csv", index_col="Estado")

    # Seleccionamos las columnas del año que nos interesa.
    columnas = [col for col in df.columns if "2023" in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[columnas]

    # Sumamos todas las columnas.
    df = df.sum(axis=1).to_frame("total")

    # Quitamos los decimales de las cifras.
    df["total"] = df["total"] * 1000000

    # Asignamos las abreviaturas de cada estado.
    df["abreviatura"] = df.index.map(ABREVIACIONES)

    # Asignamos la población de cada estado.
    df["poblacion"] = df.index.map(POBLACION)

    # Calculamos las remesas per cápita.
    df["capita"] = df["total"] / df["poblacion"]

    # Obtenemos el valor logarítmico.
    df["log"] = np.log10(df["capita"])

    # Extraemos valores totales que serán usados para algunas anotaciones.
    total_remesas = df["total"].iloc[0]
    total_poblacion = df["poblacion"].iloc[0]
    total_capita = df["capita"].iloc[0]

    # Quitamos los registros sin abreviatura.
    df = df[~pd.isna(df["abreviatura"])]

    # Creamos la escala logarítmica usando el valor máximo y mínimo en nuestro dataset.
    min_value = df["log"].min()
    max_value = df["log"].max()

    marcas = np.linspace(min_value, max_value, 11)
    textos = [f"{10 ** item:,.0f}" for item in marcas]

    fig = go.Figure()

    # Este mapa choropleth tiene la particularidad de ser específico de los EE. UU.
    # Algunos parametros como 'locationmode' y 'scope' son importantes de definir.
    fig.add_traces(
        go.Choropleth(
            locations=df["abreviatura"],
            z=df["log"],
            locationmode="USA-states",
            colorscale="speed_r",
            marker_line_color="#FFFFFF",
            showscale=True,
            showlegend=False,
            marker_line_width=2,
            zmax=max_value,
            zmin=min_value,
            colorbar={
                "x": 0.03,
                "y": 0.5,
                "thickness": 150,
                "ypad": 400,
                "ticks": "outside",
                "outlinewidth": 5,
                "outlinecolor": "#FFFFFF",
                "tickwidth": 5,
                "tickcolor": "#FFFFFF",
                "ticklen": 30,
                "tickfont_size": 80,
                "tickvals": marcas,
                "ticktext": textos,
            },
        )
    )

    fig.update_geos(
        bgcolor="#082032",
        showocean=True,
        oceancolor="#082032",
        showframe=True,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        showrivers=False,
        landcolor="#1C0A00",
        scope="usa",
    )

    fig.update_layout(
        legend_bgcolor="#111111",
        legend_font_size=100,
        legend_bordercolor="#FFFFFF",
        legend_borderwidth=2,
        font_family="Quicksand",
        font_color="#FFFFFF",
        margin_t=400,
        margin_r=300,
        margin_b=380,
        margin_l=300,
        width=7680,
        height=4320,
        paper_bgcolor="#082032",
        annotations=[
            dict(
                x=0.5,
                y=1.08,
                xanchor="center",
                yanchor="top",
                text="Estado de origen de los ingresos por remesas provenientes de EE. UU. hacia México durante enero-septiembre de 2023<br>(ajustado con la población estimada de mexicanos en EE. UU. durante el 2021)",
                font_size=120
            ),
            dict(
                x=0.02,
                y=0.105,
                textangle=270,
                xanchor="left",
                yanchor="middle",
                text="Dólares estadounidenses`por cada mexicano (escala logarítmica)",
                font_size=90
            ),
            dict(
                x=0.01,
                y=-0.08,
                xanchor="left",
                yanchor="bottom",
                text="Fuente: Banxico (noviembre 2023)",
                font_size=100
            ),
            dict(
                x=0.5,
                y=-0.08,
                xanchor="center",
                yanchor="bottom",
                text=f"Nacional: ${total_capita:,.0f} dólares por cada mexicano en EE. UU.",
                font_size=100
            ),
            dict(
                x=1.0,
                y=-0.08,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
                font_size=100
            ),
            dict(
                x=1.0,
                y=0.3,
                xanchor="right",
                yanchor="top",
                text=f"Remesas totales durante la primera<br>mitad del 2023: <b>${total_remesas:,.0f}</b> dólares<br>Población estimada de mexicanos<br>en EE. UU. (2021): <b>{total_poblacion:,.0f}</b>",
                font_size=70,
                align="left",
                bordercolor="#FFFFFF",
                borderwidth=5,
                borderpad=30,
            )
        ]
    )

    fig.write_image("./mapa_usa.png")


def stats_usa():
    """
    Obtiene el top 10 de estados en una tabla Markdown.
    """

    # Cargamos el archivo CSV con las remesas provenientes de EE. UU.
    df = pd.read_csv("./data/remesas_usa.csv", index_col="Estado")

    # Seleccionamos las columnas del año que nos interesa.
    columnas = [col for col in df.columns if "2023" in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[columnas]

    # Sumamos todas las columnas.
    df = df.sum(axis=1).to_frame("total")

    # Quitamos los decimales de las cifras.
    df["total"] = df["total"] * 1000000

    # Asignamos las abreviaturas de cada estado.
    df["abreviatura"] = df.index.map(ABREVIACIONES)

    # Asignamos la población de cada estado.
    df["poblacion"] = df.index.map(POBLACION)

    # Calculamos las remesas per cápita.
    df["capita"] = df["total"] / df["poblacion"]

    # Quitamos la primera fila.
    df = df.iloc[1:]

    # Ordenamos por cifras totales.
    df.sort_values("total", ascending=False, inplace=True)

    # Mostramos el top 10.
    print(df["total"].head(10).to_markdown(floatfmt=",.0f"))

    # Ordenamos per cápita.
    df.sort_values("capita", ascending=False, inplace=True)

    # Mostramos el top 10.
    print(df[["total", "capita"]].head(10).to_markdown(floatfmt=",.0f"))


if __name__ == "__main__":

    plot_usa()
    stats_usa()
