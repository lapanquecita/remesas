"""

Esta script crea 3 imágenes, una con los 30 países que aportan más a las remesas, una de los países que aportan menos y un mapa con todas las aportaciones.

Fuente:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CE167&sector=1&locale=es

"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Definimos los colores usados para todas las visualizaciones.
PLOT_COLOR = "#1C1F1A"
PAPER_COLOR = "#262B23"

# Mes y año en que se recopilaron los datos.
FECHA_FUENTE = "febrero 2026"

# Periodo de tiempo del análisis.
PERIODO_TIEMPO = "enero-diciembre"


def plot_top(año, flujo):
    """
    Esta función crea una gráfica de los países con mayor aportación a las remesas.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    flujo : str
        Puede ser "Ingresos"|"Egresos" para diferenciar entre
        remesas enviadas o recibidas desde México.

    """

    # Cargamos el archivo CSV de remesas por país.
    df = pd.read_csv("./data/remesas_pais.csv", parse_dates=["PERIODO"])

    # Seleccionamos los reigstros del año especificado.
    df = df[df["PERIODO"].dt.year == año]

    # Seleccionamos solo los registros del tipo de flujo indicado.
    df = df[df["FLUJO"] == flujo]

    # Calculamos el total por país.
    df = df.groupby("PAIS").sum(numeric_only=True)

    # Convertimos las cifras a millones de dólares.
    df["VALOR_USD"] /= 1000000

    # Calculamos el porcentaje relativo al total de remesas.
    df["perc"] = df["VALOR_USD"] / df["VALOR_USD"].sum() * 100

    # Creamos el texto que irá en cada barra.
    df["text"] = df.apply(
        lambda x: (
            f" {x['VALOR_USD']:,.0f} ({x['perc']:,.4f}%) "
            if x["VALOR_USD"] > 100
            else f" {x['VALOR_USD']:,.1f} ({x['perc']:,.4f}%) "
        ),
        axis=1,
    )

    # ordenamos el DAtaframe de mayor a menor cantidad de remesas.
    df.sort_values("VALOR_USD", ascending=False, inplace=True)

    # Algunos nombres son muy largos, abreviaremos la palarba República y los partiremos en 2 líneas.
    df.index = df.index.str.replace("República", "Rep.")
    df.index = df.index.str.wrap(22).str.replace("\n", "<br>")

    # Seleccionamos las primeras 30 filas.
    df = df.head(30)

    # El título cambia dependiendo el flujo.
    if flujo == "Ingresos":
        titulo = f"Los 30 países con <b>mayor envío</b> de remesas hacia México<br>durante {PERIODO_TIEMPO} de {año}"
    elif flujo == "Egresos":
        titulo = f"Los 30 países con <b>mayor recepción</b> de remesas enviadas desde México<br>durante {PERIODO_TIEMPO} de {año}"

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["VALOR_USD"],
            text=df["text"],
            textfont_color="#FFFFFF",
            textfont_family="Oswald",
            textposition=["inside"] + ["outside" for _ in range(len(df) - 1)],
            orientation="h",
            marker_color="#42a5f5",
            marker_cornerradius=45,
            width=0.6,
        )
    )

    # Data la grana diferencia entre valores, usaremos una escala logarítmica.
    # En vez de usar billón para mil millones, usaremos giga.
    fig.update_xaxes(
        exponentformat="SI",
        type="log",
        range=[
            np.log10(df["VALOR_USD"].min()) // 1,
            np.log10(df["VALOR_USD"].max() * 1.05),
        ],
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        zeroline=False,
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
        ticklen=10,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=False,
        gridwidth=0.5,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        uniformtext_minsize=24,
        uniformtext_mode="show",
        showlegend=False,
        width=1920,
        height=1920,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=titulo,
        title_x=0.5,
        title_y=0.97,
        margin_t=120,
        margin_r=40,
        margin_b=120,
        margin_l=280,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=1.0,
                y=-0.01,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="bottom",
                align="left",
                bordercolor="#FFFFFF",
                borderwidth=1.5,
                borderpad=7,
                bgcolor=PLOT_COLOR,
                text="<b>Nota:</b><br>Se utilizó una escala logarítmica<br>dada la gran diferencia entre valores.",
            ),
            dict(
                x=0.01,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.55,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Millones de dólares estadounidenses (porcentaje respecto al total)",
            ),
            dict(
                x=1.01,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo usando los parámetros de la función.
    fig.write_image(f"./remesas_pais_top_{flujo.lower()}_{año}.png")


def plot_bottom(año, flujo):
    """
    Esta función crea una gráfica de los países con menor aportación a las remesas.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    flujo : str
        Puede ser "Ingresos"|"Egresos" para diferenciar entre
        remesas enviadas o recibidas desde México.

    """
    # Cargamos el archivo CSV de remesas por país.
    df = pd.read_csv("./data/remesas_pais.csv", parse_dates=["PERIODO"])

    # Seleccionamos los reigstros del año especificado.
    df = df[df["PERIODO"].dt.year == año]

    # Seleccionamos solo los registros del tipo de flujo indicado.
    df = df[df["FLUJO"] == flujo]

    # Calculamos el total por país.
    df = df.groupby("PAIS").sum(numeric_only=True)

    # Creamos el texto que irá en cada barra.
    df["text"] = df.apply(lambda x: f" {x['VALOR_USD']:,.0f} ", axis=1)

    # Ordenamos los valores de menor a mayor y quitamos los registros en cero.
    df.sort_values("VALOR_USD", inplace=True)
    df = df[df["VALOR_USD"] != 0]

    # Algunos nombres son muy largos, los partiremos en 2 líneas.
    df.index = df.index.str.wrap(18).str.replace("\n", "<br>")

    # Seleccionamos las primeras 30 filas.
    df = df.head(30)

    # Para acomodar el texto calcularemos que tan cerca está del valor máximo.
    df["ratio"] = df["VALOR_USD"] / df["VALOR_USD"].max()
    df["text_pos"] = df["ratio"].apply(lambda x: "inside" if x >= 0.95 else "outside")

    # El título cambia dependiendo el flujo.
    if flujo == "Ingresos":
        titulo = f"Los 30 países con <b>menor envío</b> de remesas hacia México<br>durante {PERIODO_TIEMPO} de {año}"
    elif flujo == "Egresos":
        titulo = f"Los 30 países con <b>menor recepción</b> de remesas enviadas desde México<br>durante {PERIODO_TIEMPO} de {año}"

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["VALOR_USD"],
            text=df["text"],
            textfont_color="#FFFFFF",
            textfont_family="Oswald",
            textposition=df["text_pos"],
            orientation="h",
            marker_color="#ff7043",
            marker_line_width=0,
            marker_cornerradius=45,
            width=0.6,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        range=[0, df["VALOR_USD"].max() * 1.01],
        separatethousands=True,
        ticklen=10,
        zeroline=False,
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
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=False,
        gridwidth=0.5,
        showline=True,
        nticks=40,
        mirror=True,
    )

    fig.update_layout(
        uniformtext_minsize=24,
        uniformtext_mode="show",
        showlegend=False,
        width=1920,
        height=1920,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=titulo,
        title_x=0.5,
        title_y=0.97,
        margin_t=120,
        margin_r=40,
        margin_b=120,
        margin_l=280,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=1.0,
                y=0.975,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                align="left",
                bordercolor="#FFFFFF",
                borderwidth=1.5,
                borderpad=7,
                bgcolor=PLOT_COLOR,
                text="<b>Nota:</b><br>No se tomaron en cuenta los países<br>que reportaron remesas en cero.",
            ),
            dict(
                x=0.01,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Dólares estadounidenses",
            ),
            dict(
                x=1.01,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo usando los parámetros de la función.
    fig.write_image(f"./remesas_pais_bottom_{flujo.lower()}_{año}.png")


def plot_map(año, flujo):
    """
    Esta función crea un mapa de las aportaciones a las remesas por país de origen.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    flujo : str
        Puede ser "Ingresos"|"Egresos" para diferenciar entre
        remesas enviadas o recibidas desde México.

    """

    # Cargamos el archivo CSV de remesas por país.
    df = pd.read_csv("./data/remesas_pais.csv", parse_dates=["PERIODO"])

    # Seleccionamos los reigstros del año especificado.
    df = df[df["PERIODO"].dt.year == año]

    # Seleccionamos solo los registros del tipo de flujo indicado.
    df = df[df["FLUJO"] == flujo]

    # Calculamos el total por país.
    df = df.groupby("ID_PAIS").sum(numeric_only=True)

    # Quitamos valores en cero.
    df = df[df["VALOR_USD"] != 0]

    # Obtenemos los valores logarítmicos.
    df["log"] = np.log10(df["VALOR_USD"])

    # Creamos la escala logarítmica usando el valor máximo y mínimo en nuestro dataset.
    valor_min = df["log"].min()
    valor_max = df["log"].max()

    # Creamos las marcas para la escala.
    marcas = np.arange(np.floor(valor_min), np.ceil(valor_max))

    textos = list()

    # Convertiremos los textos a base 10.
    for item in marcas:
        v, e = f"{10**item:e}".split("e")
        textos.append(f"{10 * float(v):.0f}<sup>{int(e) - 1}</sup>")

    # El título cambia dependiendo el flujo.
    if flujo == "Ingresos":
        titulo = f"Valor de las remesas recibidas en México por país de origen durante {PERIODO_TIEMPO} de {año}"
        subtitulo = f"Valor total: <b>{df['VALOR_USD'].sum():,.0f}</b> dólares de <b>{len(df)}</b> países"
    elif flujo == "Egresos":
        titulo = f"Valor de las remesas enviadas desde  México por país de destino durante {PERIODO_TIEMPO} de {año}"
        subtitulo = f"Valor total: <b>{df['VALOR_USD'].sum():,.0f}</b> dólares a <b>{len(df)}</b> países"

    fig = go.Figure()

    fig.add_traces(
        go.Choropleth(
            locations=df.index,
            z=df["log"],
            colorscale="geyser_r",
            marker_line_color="#FFFFFF",
            showscale=True,
            showlegend=False,
            marker_line_width=2,
            zmax=valor_max,
            zmin=valor_min,
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
        oceancolor=PLOT_COLOR,
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        font_size=120,
        font_family="Inter",
        font_color="#FFFFFF",
        margin_t=240,
        margin_r=100,
        margin_b=0,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.04,
                xanchor="center",
                yanchor="top",
                text=titulo,
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
            ),
            dict(
                x=0.5,
                y=-0.065,
                xanchor="center",
                yanchor="bottom",
                text=subtitulo,
            ),
            dict(
                x=1.0,
                y=-0.065,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo usando los parámetros de la función.
    fig.write_image(f"./mapa_pais_{flujo.lower()}_{año}.png")


def plot_tendencias(primer_año, ultimo_año, flujo):
    """
    Esta función crea una cuadrícula de sparklines con
    los países que han crecido más en envios de remesas.

    Parameters
    ----------
    primer_año : int
        El año inicial que se desea comparar.

    ultimo_año :  int
        El año final que se desea comparar.

    flujo : str
        Puede ser "Ingresos"|"Egresos" para diferenciar entre
        remesas enviadas o recibidas desde México.

    """

    # Cargamos el dataset de remesas por país.
    df = pd.read_csv("./data/remesas_pais.csv", parse_dates=["PERIODO"])

    # Seleccionamos solo los registros del tipo de flujo indicado.
    df = df[df["FLUJO"] == flujo]

    # Seleccionamos los años dentro de nuestro rango de interés.
    df = df[
        (df["PERIODO"].dt.year >= primer_año) & (df["PERIODO"].dt.year <= ultimo_año)
    ]

    # Transformamos nuestro dataset para que el índice sean los países y las columnas los años.
    df = df.pivot_table(
        index="PAIS",
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

    # Quitamos los países que hayan tenido menos de
    # 5 millones de dólares durante el último año.
    # Esto es con el propósito de encontrar los outliers más substanciales.
    df = df[df[ultimo_año] >= 5]

    # Ordenamos los valores usando el cambio porcentual de mayor a menor.
    df.sort_values("change", ascending=False, inplace=True)

    # El título y subtítulo cambian dependiendo el flujo.
    if flujo == "Ingresos":
        titulo = f"Los 15 países con mayor crecimiento en envio de remesas hacia México ({primer_año} vs. {ultimo_año})"
        subtitulo = f"Crecimiento nacional de {primer_año} a {ultimo_año}: <b>{cambio:,.2f}%</b>"
    elif flujo == "Egresos":
        titulo = f"Los 15 países con mayor crecimiento en recepción de remesas enviadas desde México ({primer_año} vs. {ultimo_año})"
        subtitulo = (
            f"Crecimiento general de {primer_año} a {ultimo_año}: <b>{cambio:,.2f}%</b>"
        )

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

            if ultimo_valor < 10:
                textos[-1] = f"<b>{ultimo_valor:,.1f}</b>"
            else:
                textos[-1] = f"<b>{ultimo_valor:,.0f}</b>"

            # Posicionamos los dos textos.
            text_pos = ["middle center" for _ in range(len(temp_df))]
            text_pos[0] = "top center"
            text_pos[-1] = "bottom center"

            # Calculamos el cambio porcentual y creamos el texto que irá en la anotación de cada cuadro.
            change = (ultimo_valor - primer_valor) / primer_valor * 100
            diff = ultimo_valor - primer_valor

            if diff < 10:
                texto_anotaciones.append(f"<b>+{diff:,.1f}</b><br>+{change:,.0f}%")
            else:
                texto_anotaciones.append(f"<b>+{diff:,.0f}</b><br>+{change:,.0f}%")

            fig.add_trace(
                go.Scatter(
                    x=temp_df.index,
                    y=temp_df.values,
                    text=textos,
                    mode="markers+lines+text",
                    textposition=text_pos,
                    marker_color="#ffd600",
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
        title_text=titulo,
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
            font_color="#ffd600",
            bordercolor="#ffd600",
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
        text=subtitulo,
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

    fig.write_image(f"./pais_tendencia_{flujo.lower()}.png")


if __name__ == "__main__":
    plot_top(2025, "Ingresos")
    plot_top(2025, "Egresos")

    plot_bottom(2025, "Ingresos")
    plot_bottom(2025, "Egresos")

    plot_map(2025, "Ingresos")
    plot_map(2025, "Egresos")

    plot_tendencias(2016, 2025, "Ingresos")
    plot_tendencias(2016, 2025, "Egresos")
