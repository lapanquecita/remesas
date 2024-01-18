"""

Fuente:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=1&accion=consultarCuadro&idCuadro=CE100&locale=es

"""

import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots


# Definimos los colores que usaremos para el mapa y tablas.
PLOT_COLOR = "#18122B"
PAPER_COLOR = "#393053"
HEADER_COLOR = "#e65100"


def plot_mapa(año):
    """
    Esta función crea un mapa y unas tablas con la información de remesas per cápita.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de población total por entidad.
    pop = pd.read_csv("./assets/poblacion_anual.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    pop = pop[str(año)]

    # Renombramos algunos estados a sus nombres más comunes.
    pop = pop.rename(
        {
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz"
        }
    )

    # Cargamos el dataset de remesas por entidad.
    df = pd.read_csv("./data/remesas_entidad.csv", index_col="Entidad")

    # Seleccionamos las columnas del año que nos interesa.
    cols = [col for col in df.columns if str(año) in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[cols]

    # Quitamos los decimales de las cifras.
    df["total"] = df.sum(axis=1) * 1000000

    # Calculamos las remesas per cápita para toda la polación.
    subtitulo = f"Nacional: {df['total'].sum() / pop.sum():,.2f} dólares p. c."

    # Asignamos la población a cada entidad.
    df["pop"] = df.index.map(pop)

    # Calculamos el valor per cápita.
    df["capita"] = df["total"] / df["pop"]

    # Ordenamos per cápita de mayor a menor.
    df = df.sort_values("capita", ascending=False)

    # Estas listas nos serviran para alimetnar el mapa.
    ubicaciones = list()
    valores = list()

    # Estos valores serán usados para definir la escala en el mapa.
    min_val = df["capita"].min()
    max_val = df["capita"].max()

    marcas = np.linspace(min_val, max_val, 11)
    etiquetas = list()

    for item in marcas:
        etiquetas.append("{:,.0f}".format(item))

    # Cargamos el archivo GeoJSON de México.
    geojson = json.loads(open("./assets/mexico.json",
                              "r", encoding="utf-8").read())
    
    # Iteramos sobre cada entidad dentro de nuestro archivo GeoJSON de México.
    for item in geojson["features"]:

        geo = item["properties"]["NOM_ENT"]

        # Alimentamos las listas creadas anteriormente con la ubicación y su valor per capita.
        ubicaciones.append(geo)
        valores.append(df.loc[geo, "capita"])

    fig = go.Figure()

    # Vamos a crear un mapa Choropleth con todas las variables anteriormente definidas.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=ubicaciones,
            z=valores,
            featureidkey="properties.NOM_ENT",
            colorscale="oranges",
            reversescale=True,
            marker_line_color="#FFFFFF",
            marker_line_width=1.0,
            zmin=min_val,
            zmax=max_val,
            colorbar=dict(
                x=0.03,
                y=0.5,
                ypad=50,
                ticks="outside",
                outlinewidth=1.5,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=2,
                tickcolor="#FFFFFF",
                ticklen=10,
                tickfont_size=20
            ),
        )
    )

    # Personalizamos la apariencia del mapa.
    fig.update_geos(
        fitbounds="locations",
        showocean=True,
        oceancolor=PLOT_COLOR,
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=2,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00"
    )

    fig.update_layout(
        legend_x=.01,
        legend_y=0.07,
        legend_bgcolor="#111111",
        legend_font_size=20,
        legend_bordercolor="#FFFFFF",
        legend_borderwidth=2,
        font_family="Quicksand",
        font_color="#FFFFFF",
        margin={"r": 40, "t": 50, "l": 40, "b": 30},
        width=1280,
        height=720,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.01,
                xanchor="center",
                yanchor="top",
                text=f"Ingresos por remesas hacia México por entidad durante el {año}",
                font_size=28
            ),
            dict(
                x=0.58,
                y=-0.04,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
                font_size=26
            ),
            dict(
                x=0.0275,
                y=0.45,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Dólares per cápita",
                font_size=18
            ),
            dict(
                x=0.01,
                y=-0.04,
                xanchor="left",
                yanchor="top",
                text="Fuente: Banxico (noviembre 2023)",
                font_size=24
            ),
            dict(
                x=1.01,
                y=-0.04,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
                font_size=24
            )
        ]
    )

    fig.write_image("./0.png")

    # Vamos a crear dos tablas, cada una con la información de 16 entidades.
    fig = make_subplots(
        rows=1, cols=2,
        horizontal_spacing=0.03,
        specs=[
              [{"type": "table"}, {"type": "table"}]]
    )

    fig.add_trace(
        go.Table(
            columnwidth=[145, 100, 100],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    f"<b>Total en dólares</b>",
                    F"<b>Per cápita ↓</b>",
                ],
                font_color="#FFFFFF",
                fill_color=HEADER_COLOR,
                align="center",
                height=29,
                line_width=0.8
            ),
            cells=dict(
                values=[
                    df.index[:16],
                    df["total"][:16],
                    df["capita"][:16],
                ],
                fill_color=PLOT_COLOR,
                height=29,
                prefix=["", "$", "$"],
                format=["", ",.0f", ",.2f"],
                line_width=0.8,
                align=["left", "left", "center"]
            )
        ), col=1, row=1
    )

    fig.add_trace(
        go.Table(
            columnwidth=[145, 100, 100],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    f"<b>Total en dólares</b>",
                    F"<b>Per cápita ↓</b>",
                ],
                font_color="#FFFFFF",
                fill_color=HEADER_COLOR,
                align="center",
                height=29,
                line_width=0.8
            ),
            cells=dict(
                values=[
                    df.index[16:],
                    df["total"][16:],
                    df["capita"][16:],
                ],
                fill_color=PLOT_COLOR,
                height=29,
                prefix=["", "$", "$"],
                format=["", ",.0f", ",.2f"],
                line_width=0.8,
                align=["left", "left", "center"]
            )
        ), col=2, row=1
    )

    fig.update_layout(
        showlegend=False,
        legend_borderwidth=1.5,
        xaxis_rangeslider_visible=False,
        width=1280,
        height=560,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=18,
        title="",
        title_x=0.5,
        title_y=0.95,
        margin_t=20,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_font_size=26,
        paper_bgcolor=PAPER_COLOR,
    )

    fig.write_image("./1.png")

    # Unimos el mapa y las tablas en una sola imagen.
    image1 = Image.open("./0.png")
    image2 = Image.open("./1.png")

    result_width = 1280
    result_height = image1.height + image2.height

    result = Image.new("RGB", (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, image1.height))

    result.save("./mapa_mexico.png")

    # Borramos las imágenes originales.
    os.remove("./0.png")
    os.remove("./1.png")


if __name__ == "__main__":

    plot_mapa(2023)
