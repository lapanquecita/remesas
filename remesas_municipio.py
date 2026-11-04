"""

Fuente:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=1&accion=consultarCuadro&idCuadro=CE166&locale=es

"""

import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Mes y año en que se recopilaron los datos.
FECHA_FUENTE = "noviembre 2026"

# Periodo de tiempo del análisis.
PERIODO_TIEMPO = "enero-diciembre"


# Definimos los colores que usaremos para el mapa y tablas.
PLOT_COLOR = "#1C1F1A"
PAPER_COLOR = "#262B23"
HEADER_COLOR = "#C25B42"


def plot_mapa(año, tipo):
    """
    Esta función crea un mpara choropleth de los municipios de México.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    tipo : str
        El tipo de denominador a usar.
        Puede ser 'habitantes' o 'viviendas'.

    """

    # Cargamos el dataset de población o de viviendas
    # según el tipo de denominador especificado.
    if tipo == "habitantes":
        # Cargamos el dataset de población por municipio.
        pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str}, index_col=0)

        # Seleccionamos la población del año especificado.
        pop = pop[str(año)]

        # Renombramos la etiqueta.
        tipo = "per cápita"
    elif tipo == "viviendas":
        # Cargamos el dataset de viviendas habitadas por municipio.
        pop = pd.read_csv("./assets/viviendas.csv", dtype={"CVEGEO": str}, index_col=0)
        pop = pop["TOTAL"]

        # Renombramos la etiqueta.
        tipo = "por vivienda"

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv(
        "./data/remesas_municipio.csv",
        parse_dates=["PERIODO"],
        dtype={"CVE_GEO": str},
    )

    # Seleccionamos los reigstros del año especificado.
    df = df[df["PERIODO"].dt.year == año]

    # Calculamos el total por municipio.
    df = df.groupby("CVE_GEO").sum(numeric_only=True)

    # Asignamos la población/viviendas a cada municipio.
    df["pop"] = pop

    # Calculamos el valor per cápita/por vivienda.
    df["capita"] = df["VALOR_USD"] / df["pop"]

    # Calculamos las remesas per cápita para toda la polación.
    subtitulo = (
        f"Nacional: <b>{df['VALOR_USD'].sum() / pop.sum():,.0f}</b> dólares {tipo}"
    )

    # Quitamos los valores en cero e inválidos para que no interfieran con los siguientes pasos.
    df = df.dropna(axis=0)
    df = df[df["VALOR_USD"] != 0]

    # Calculamos algunas estadísticas descriptivas.
    estadisticas = [
        "Estadísticas descriptivas",
        f"<b>(dólares {tipo})</b>",
        f"Media: <b>{df['capita'].mean():,.1f}</b>",
        f"Mediana: <b>{df['capita'].median():,.1f}</b>",
        f"DE: <b>{df['capita'].std():,.1f}</b>",
        f"25%: <b>{df['capita'].quantile(0.25):,.1f}</b>",
        f"75%: <b>{df['capita'].quantile(0.75):,.1f}</b>",
        f"95%: <b>{df['capita'].quantile(0.95):,.1f}</b>",
        f"Máximo: <b>{df['capita'].max():,.1f}</b>",
    ]

    estadisticas = "<br>".join(estadisticas)

    # Estos valores serán usados para definir la escala en el mapa.
    # Para mitigar el impacto de valores atípicos, toparemola escala al percentíl 97.5.
    valor_min = df["capita"].min()
    valor_max = df["capita"].quantile(0.975)

    marcas = np.linspace(valor_min, valor_max, 11)
    etiquetas = [f"{item:,.0f}" for item in marcas]

    # Agregamos el símbolo de igual o mayr que a la última etiqueta.
    etiquetas[-1] = f"≥{etiquetas[-1]}"

    # Cargamos el archivo GeoJSON de México.
    geojson = json.load(open("./assets/municipios.json", "r", encoding="utf-8"))

    fig = go.Figure()

    # Configuramos nuestro mapa Choropleth con todas las variables antes definidas.
    # El parámetro 'featureidkey' debe coincidir con el de la variable 'geo' que
    # extrajimos en un paso anterior.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=df.index,
            z=df["capita"],
            featureidkey="properties.CVEGEO",
            colorscale="deep_r",
            marker_line_color="#FFFFFF",
            marker_line_width=1,
            zmin=valor_min,
            zmax=valor_max,
            colorbar=dict(
                x=0.035,
                y=0.5,
                thickness=150,
                ypad=400,
                ticks="outside",
                outlinewidth=5,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=5,
                tickcolor="#FFFFFF",
                ticklen=30,
                tickfont_size=80,
            ),
        )
    )

    # Vamos a sobreponer otro mapa Choropleth, el cual
    # tiene el único propósito de mostrar la división política
    # de las entidades federativas.

    # Cargamos el archivo GeoJSON de México.
    geo_borde = json.load(open("./assets/mexico.json", "r", encoding="utf-8"))

    # Este mapa tiene mucho menos personalización.
    # Lo único que necesitamos es que muestre los contornos
    # de cada entidad.
    fig.add_traces(
        go.Choropleth(
            geojson=geo_borde,
            locations=[item["properties"]["CVEGEO"] for item in geo_borde["features"]],
            z=[1 for _ in geo_borde["features"]],
            featureidkey="properties.CVEGEO",
            colorscale=["hsla(0, 0%, 0%, 0)", "hsla(0, 0%, 0%, 0)"],
            marker_line_color="#FFFFFF",
            marker_line_width=4,
            showscale=False,
        )
    )

    # Personalizamos algunos aspectos del mapa, como el color del oceáno
    # y el del terreno.
    fig.update_geos(
        fitbounds="geojson",
        showocean=True,
        oceancolor=PLOT_COLOR,
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#000000",
    )

    # Agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=False,
        font_family="Inter",
        font_color="#FFFFFF",
        margin_t=50,
        margin_r=100,
        margin_b=30,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=0.985,
                xanchor="center",
                yanchor="top",
                text=f"Ingresos por remesas {tipo} en municipios de México durante {PERIODO_TIEMPO} de {año}",
                font_size=140,
            ),
            dict(
                x=0.02,
                y=0.49,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text=f"Dólares {tipo} durante el año",
                font_size=100,
            ),
            dict(
                x=0.98,
                y=0.9,
                xanchor="right",
                yanchor="top",
                text=estadisticas,
                align="left",
                borderpad=30,
                bordercolor="#FFFFFF",
                bgcolor="#000000",
                borderwidth=5,
                font_size=120,
            ),
            dict(
                x=0.001,
                y=-0.003,
                xanchor="left",
                yanchor="bottom",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
                font_size=120,
            ),
            dict(
                x=0.5,
                y=-0.003,
                xanchor="center",
                yanchor="bottom",
                text=subtitulo,
                font_size=120,
            ),
            dict(
                x=1.0,
                y=-0.003,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
                font_size=120,
            ),
        ],
    )

    fig.write_image(f"./municipal_{año}_{tipo}.png")


def plot_tasa(año, tipo):
    """
    Genera una tabla con los 30 municipios que reciben más
    remesas ajustados por población/viviendas.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    tipo : str
        El tipo de denominador a usar.
        Puede ser 'habitantes' o 'viviendas'.

    """

    # Cargamos el dataset de población o de viviendas
    # según el tipo de denominador especificado.
    if tipo == "habitantes":
        # Cargamos el dataset de población por municipio.
        pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str}, index_col=0)

        # Seleccionamos la población del año especificado.
        pop = pop[str(año)]

        # Renombramos la etiqueta.
        tipo = "per cápita"
    elif tipo == "viviendas":
        # Cargamos el dataset de viviendas habitadas por municipio.
        pop = pd.read_csv("./assets/viviendas.csv", dtype={"CVEGEO": str}, index_col=0)
        pop = pop["TOTAL"]

        # Renombramos la etiqueta.
        tipo = "por vivienda"

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv(
        "./data/remesas_municipio.csv", parse_dates=["PERIODO"], dtype={"CVE_GEO": str}
    )

    # Seleccionamos los reigstros del año especificado.
    df = df[df["PERIODO"].dt.year == año]

    # Creamos una columna con el nombre completo de cada municipio.
    # Esta será utilizada para indexar el DataFrame.
    df["nombre"] = df["MUNICIPIO"] + ", " + df["ENTIDAD"]

    # Calculamos el monto total por municipio.
    df = df.groupby(["CVE_GEO", "nombre"], as_index=False).sum(numeric_only=True)

    # Quitamos valores en cero.
    df = df[df["VALOR_USD"] != 0]

    # Asignamos la población/viviendas a cada municipio.
    df["pop"] = df["CVE_GEO"].map(pop)

    # Calculamos el valor per cápita/por vivienda.
    df["capita"] = df["VALOR_USD"] / df["pop"]

    # Calculamos las remesas per cápita para toda la polación.
    subtitulo = (
        f"Nacional: <b>{df['VALOR_USD'].sum() / pop.sum():,.0f}</b> dólares {tipo}"
    )

    # Ordenamos per cápita de mayor a menor.
    df = df.sort_values("capita", ascending=False)

    # Seleccionamos las primeras 30 filas.
    df = df.head(30)

    # Para el rank resetearemos el índice y le sumaremos 1, para que sea del 1 al 30 en vez del 0 al 29.
    df = df.reset_index()
    df.index += 1

    # Acortamos el nombre del municipio más largo de México.
    df["nombre"] = df["nombre"].replace(
        {
            "Dolores Hidalgo Cuna de la Independencia Nal., Guanajuato": "Dolores Hidalgo, Guanajuato",
        }
    )

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[40, 200, 100, 100],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    "<b>Municipio, Entidad</b>",
                    "<b>Ingreso total (MDD)</b>",
                    f"<b>USD {tipo} ↓</b>",
                ],
                font_color="#FFFFFF",
                line_width=1,
                fill_color=["#00897b", "#00897b", "#00897b", HEADER_COLOR],
                align="center",
                height=43,
            ),
            cells=dict(
                values=[
                    df.index,
                    df["nombre"],
                    df["VALOR_USD"] / 1000000,
                    df["capita"],
                ],
                line_width=1,
                fill_color=PLOT_COLOR,
                height=43,
                format=["", "", ",.1f", ",.0f"],
                align=["center", "left", "center"],
            ),
        )
    )

    fig.update_layout(
        width=1280,
        height=1600,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=25,
        margin_t=180,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=40,
        title_text=f"Los municipios de México con mayores ingresos por remesas<br><b>{tipo}</b> durante {PERIODO_TIEMPO} de {año}",
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.015,
                y=0.02,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.57,
                y=0.02,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=0.02,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./tabla_tasa_{año}_{tipo}.png")


def plot_absolutos(año, tipo):
    """
    Esta función crea una tabla con los municiios que reciben mas remesas totales.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    tipo : str
        El tipo de denominador a usar.
        Puede ser 'habitantes' o 'viviendas'.

    """

    # Cargamos el dataset de población o de viviendas
    # según el tipo de denominador especificado.
    if tipo == "habitantes":
        # Cargamos el dataset de población por municipio.
        pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str}, index_col=0)

        # Seleccionamos la población del año especificado.
        pop = pop[str(año)]

        # Renombramos la etiqueta.
        tipo = "per cápita"
    elif tipo == "viviendas":
        # Cargamos el dataset de viviendas habitadas por municipio.
        pop = pd.read_csv("./assets/viviendas.csv", dtype={"CVEGEO": str}, index_col=0)
        pop = pop["TOTAL"]

        # Renombramos la etiqueta.
        tipo = "por vivienda"

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv(
        "./data/remesas_municipio.csv", parse_dates=["PERIODO"], dtype={"CVE_GEO": str}
    )

    # Seleccionamos los reigstros del año especificado.
    df = df[df["PERIODO"].dt.year == año]

    # Creamos una columna con el nombre completo de cada municipio.
    # Esta será utilizada para indexar el DataFrame.
    df["nombre"] = df["MUNICIPIO"] + ", " + df["ENTIDAD"]

    # Calculamos el monto total por municipio.
    df = df.groupby(["CVE_GEO", "nombre"], as_index=False).sum(numeric_only=True)

    # Quitamos valores en cero.
    df = df[df["VALOR_USD"] != 0]

    # Asignamos la población/viviendas a cada municipio.
    df["pop"] = df["CVE_GEO"].map(pop)

    # Calculamos el valor per cápita/por vivienda.
    df["capita"] = df["VALOR_USD"] / df["pop"]

    # Calculamos las remesas per cápita para toda la polación.
    subtitulo = (
        f"Nacional: <b>{df['VALOR_USD'].sum() / pop.sum():,.0f}</b> dólares {tipo}"
    )

    # Ordenamos per cápita de mayor a menor.
    df.sort_values("VALOR_USD", ascending=False, inplace=True)

    # Quitamos los valores infinitos.
    df = df[df["capita"] != np.inf]

    # Seleccionamos las primeras 30 filas.
    df = df.head(30)

    # Para el rank resetearemos el índice y le sumaremos 1, para que sea del 1 al 30 en vez del 0 al 29.
    df = df.reset_index()
    df.index += 1

    # Acortamos el nombre del municipio más largo de México.
    df["nombre"] = df["nombre"].replace(
        {
            "Dolores Hidalgo Cuna de la Independencia Nal., Guanajuato": "Dolores Hidalgo, Guanajuato",
        }
    )

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[40, 200, 110, 90],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    "<b>Municipio, Entidad</b>",
                    "<b>Ingreso total (MDD) ↓</b>",
                    f"<b>USD {tipo}</b>",
                ],
                font_color="#FFFFFF",
                line_width=1,
                fill_color=["#00897b", "#00897b", HEADER_COLOR, "#00897b"],
                align="center",
                height=43,
            ),
            cells=dict(
                values=[
                    df.index,
                    df["nombre"],
                    df["VALOR_USD"] / 1000000,
                    df["capita"],
                ],
                line_width=1,
                fill_color=PLOT_COLOR,
                height=43,
                format=["", "", ",.1f", ",.0f"],
                align=["center", "left", "center"],
            ),
        )
    )

    fig.update_layout(
        width=1280,
        height=1600,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=25,
        margin_t=180,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=40,
        title_text=f"Los municipios de México con mayores ingresos por remesas<br><b>totales</b> durante {PERIODO_TIEMPO} de {año}",
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.015,
                y=0.02,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.57,
                y=0.02,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=0.02,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./tabla_absolutos_{año}_{tipo}.png")


def plot_tendencias(primer_año, ultimo_año):
    """
    Esta función crea una cuadrícula de sparklines con
    los municipios que han crecido más en ingresos por remesas.

    Parameters
    ----------
    primer_año : int
        El año inicial que se desea comparar.

    ultimo_año :  int
        El año final que se desea comparar.

    """

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv("./data/remesas_municipio.csv", parse_dates=["PERIODO"])

    # Seleccionamos los años dentro de nuestro rango de interés.
    df = df[
        (df["PERIODO"].dt.year >= primer_año) & (df["PERIODO"].dt.year <= ultimo_año)
    ]

    # Creamos una nueva columna que después será el índice.
    df["nombre"] = df["MUNICIPIO"] + ", " + df["ENTIDAD"]

    # Transformamos nuestro dataset para que el índice sean los municipios y las columnas los años.
    df = df.pivot_table(
        index="nombre",
        columns=df["PERIODO"].dt.year,
        values="VALOR_USD",
        aggfunc="sum",
    )

    # Convertimos las cifras a millones de dólares.
    df /= 1000000

    # Vamos a calcular el cambio porcentual entre el primer y último año.
    df["change"] = (df[ultimo_año] - df[primer_año]) / df[primer_año] * 100

    # Calculamos el cambio nacional.
    cambio = (df[ultimo_año].sum() - df[primer_año].sum()) / df[primer_año].sum() * 100

    # Quitamos los municipsios con valores infinitos.
    df = df[df["change"] != np.inf]

    # Quitamos los municipios que hayan tenido menos de
    # 100 millones de dólares durante el último año.
    # Esto es con el propósito de encontrar los outliers más substanciales.
    df = df[df[ultimo_año] >= 100]

    # Ordenamos los valores usando el cambio porcentual de mayor a menor.
    df = df.sort_values("change", ascending=False)

    # Esta lista contendrá los textos de cada anotación.
    texto_anotaciones = list()

    # Formateamos los subtítulos para cada cuadro en nuestra cuadrícula.
    titles = [f"<b>{item}</b>" for item in df.index.tolist()]

    # Vamos a crear una cuadrícula de 3 columnas por 5 filas (15 cuadros).
    fig = make_subplots(
        rows=5,
        cols=3,
        horizontal_spacing=0.09,
        vertical_spacing=0.07,
        subplot_titles=titles,
    )

    # Esta variable la usaremos para saber de que fila extraer la información.
    index = 0

    # Con ciclos anidados es como creamos la cuadrícula.
    for row in range(5):
        for column in range(3):
            # Seleccionamos la fila correspondiente a la variable index pero omitimos la última columna.
            # la cual contiene el cambio porcentual.
            temp_df = df.iloc[index, :-1]

            # Al íncide (que son los años) lq quitamos los primeros 2 dígitos y le agregamos un apóstrofe.
            # Esto es para reducir el tamaño de la etiqueta de cada año.
            temp_df.index = temp_df.index.map(lambda x: f"'{x - 2000}")

            # Para nuestra gráfica de línea solo vamos a necesitar que el primer y último registro tengan un punto.
            sizes = [0 for _ in range(len(temp_df))]
            sizes[0] = 20
            sizes[-1] = 20

            # Vamos a extraer algunos valores para calcular el cambio porcentual.
            primer_valor = temp_df.iloc[0]
            ultimo_valor = temp_df.iloc[-1]

            # Solo el primer y último registro llevarán un texto con sus valores.
            textos = ["" for _ in range(len(temp_df))]

            if primer_valor < 10:
                textos[0] = f"<b>{primer_valor:,.1f}</b>"
            else:
                textos[0] = f"<b>{primer_valor:,.0f}</b>"

            textos[-1] = f"<b>{ultimo_valor:,.0f}</b>"

            # Posicionamos los dos textos.
            text_pos = ["middle center" for _ in range(len(temp_df))]
            text_pos[0] = "top center"
            text_pos[-1] = "bottom center"

            # Calculamos el cambio porcentual y creamos el texto que irá en la anotación de cada cuadro.
            change = (ultimo_valor - primer_valor) / primer_valor * 100
            diff = ultimo_valor - primer_valor

            texto_anotaciones.append(f"<b>+{diff:,.0f}</b><br>+{change:,.0f}%")

            fig.add_trace(
                go.Scatter(
                    x=temp_df.index,
                    y=temp_df.values,
                    text=textos,
                    mode="markers+lines+text",
                    textposition=text_pos,
                    marker_color="#80deea",
                    marker_opacity=1.0,
                    marker_size=sizes,
                    marker_line_width=0,
                    line_width=4,
                    line_shape="spline",
                    line_smoothing=1.0,
                ),
                row=row + 1,
                col=column + 1,
            )

            # Sumamos 1 a esta variable para que el siguiente cuadro extraíga la siguiente fila.
            index += 1

    fig.update_xaxes(
        tickfont_size=20,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=1.5,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        title_text="Millones de dólares",
        separatethousands=True,
        tickfont_size=20,
        tickformat="s",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=1.5,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=8,
    )

    fig.update_layout(
        font_family="Inter",
        showlegend=False,
        width=1920,
        height=2400,
        font_color="#FFFFFF",
        font_size=24,
        margin_t=160,
        margin_l=140,
        margin_r=60,
        margin_b=150,
        title_text=f"Los 15 municipios de México con mayor crecimiento en ingresos por remesas ({primer_año} vs. {ultimo_año})",
        title_x=0.5,
        title_y=0.985,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
    )

    # Vamos a crear una anotación en cada cuadro con textos mostrando el total y el cambio porcentual.
    # Lo que vamos a hacer a continuación se puede considerar como un 'hack'.
    annotations_x = list()
    annotations_y = list()

    # Iteramos sobre todos los subtítulos de cada cuadro, los cuales son considerados como anotaciones.
    for annotation in fig["layout"]["annotations"]:
        # A cada subtítulo lo vamos a ajustar ligeramente.
        annotation["y"] += 0.005
        annotation["font"]["size"] = 30

        # Vamos a extraer las coordenadas X y Y de cada subtítulo para usarlas de referencia
        # para nuestras nuevas anotaciones.
        annotations_x.append(annotation["x"])
        annotations_y.append(annotation["y"])

    # Es momento de crear nuestras nuevas anotaciones.
    # Usando la función zip() podemos iterar sobre nuestras listas de valores al mismo tiempo.
    for (
        x,
        y,
        t,
    ) in zip(annotations_x, annotations_y, texto_anotaciones):
        # Vamos a ajustar las nuevas anotaciones basandonos en las coornedas de los subtítulos.
        x -= 0.12
        y -= 0.03

        fig.add_annotation(
            x=x,
            xanchor="left",
            xref="paper",
            y=y,
            yanchor="top",
            yref="paper",
            text=t,
            font_color="#80deea",
            bordercolor="#80deea",
            borderpad=5,
            borderwidth=1.5,
            bgcolor=PLOT_COLOR,
        )

    fig.add_annotation(
        x=0.01,
        y=-0.07,
        xanchor="left",
        xref="paper",
        yanchor="bottom",
        yref="paper",
        text=f"Fuente: Banxico ({FECHA_FUENTE})",
    )

    fig.add_annotation(
        x=0.5,
        y=-0.07,
        xanchor="center",
        xref="paper",
        yanchor="bottom",
        yref="paper",
        text=f"Crecimiento nacional de {primer_año} a {ultimo_año}: <b>{cambio:,.2f}%</b>",
    )

    fig.add_annotation(
        x=1.01,
        y=-0.07,
        xanchor="right",
        xref="paper",
        yanchor="bottom",
        yref="paper",
        text="🧁 @lapanquecita",
    )

    fig.write_image("./municipios_tendencia.png")


if __name__ == "__main__":
    plot_mapa(2025, "habitantes")
    # plot_mapa(2025, "viviendas")

    plot_tasa(2025, "habitantes")
    # plot_tasa(2025, "viviendas")

    plot_absolutos(2025, "habitantes")
    # plot_absolutos(2025, "viviendas")

    plot_tendencias(2016, 2025)
