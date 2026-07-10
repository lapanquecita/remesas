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


# Mes y año en que se recopilaron los datos.
FECHA_FUENTE = "julio 2026"

# Mes y año del IPC de referencia.
FECHA_INFLACION = "junio de 2026"

# Periodo de tiempo del análisis.
PERIODO_TIEMPO = "enero-diciembre"

# Definimos los colores que usaremos para el mapa y tablas.
PLOT_COLOR = "#1C1F1A"
PAPER_COLOR = "#262B23"
HEADER_COLOR = "#C25B42"


def cargar_deflactadores(modo):
    """
    Carga las series de tiempo del IPC y tipo de cambio
    en un solo DataFrame.

    Esto es utilizado para ajustar las remesas por inflación.

    Parameters
    ----------
    modo : str
        Puede ser 'mensual' o 'trimestral'.

    """

    # Cargamos el dataset del IPC.
    ipc = pd.read_csv("./assets/IPC.csv", parse_dates=["PERIODO"], index_col=0)

    # Escogemos un IPC de referencia (el más reciente).
    ipc_referencia = ipc["GENERAL"].iloc[-1]

    # Calculamos el factor.
    ipc["factor"] = ipc_referencia / ipc["GENERAL"]

    # Cargamos el dataset del tipo de cambio.
    fx = pd.read_csv("./assets/USDMXN.csv", parse_dates=["PERIODO"], index_col=0)

    # Unimos ambos DataFrames y quitamos las filas incompletas.
    df = pd.concat([ipc["factor"], fx], axis=1).dropna(axis=0)

    # Si la modalidad es mensual, regresamos el DataFrame tal cual.
    # Si es trimestral, hacemos remuestreo usando el promedio trimestral.
    if modo == "mensual":
        return df
    elif modo == "trimestral":
        return df.resample("QS").mean()


def plot_mapa(año):
    """
    Esta función crea un mapa y unas tablas con la información de remesas per cápita.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de la polación total estimada según el CONAPO.
    pop = pd.read_csv("./assets/poblacion.csv")

    # Calculamos la población total por entidad.
    pop = pop.groupby("Entidad").sum(numeric_only=True)

    # Seleccionamos la población del año de nuestro interés.
    pop = pop[str(año)]

    # Cargamos el dataset de remesas por entidad.
    df = pd.read_csv("./data/remesas_entidad.csv", parse_dates=["PERIODO"])

    # Seleccionamos los reigstros del año especificado.
    df = df[df["PERIODO"].dt.year == año]

    # Calculamos el total por entidad.
    df = df.groupby("ENTIDAD").sum(numeric_only=True)

    # Calculamos las remesas per cápita para toda la polación.
    subtitulo = (
        f"Nacional: <b>{df['VALOR_USD'].sum() / pop.sum():,.0f}</b> dólares per cápita"
    )

    # Asignamos la población a cada entidad.
    df["pop"] = pop

    # Calculamos el valor per cápita.
    df["capita"] = df["VALOR_USD"] / df["pop"]

    # Ordenamos per cápita de mayor a menor.
    df = df.sort_values("capita", ascending=False)

    # Estos valores serán usados para definir la escala en el mapa.
    valor_min = df["capita"].min()
    valor_max = df["capita"].max()

    marcas = np.linspace(valor_min, valor_max, 11)
    etiquetas = [f"{item:,.0f}" for item in marcas]

    # Cargamos el archivo GeoJSON de México.
    geojson = json.loads(open("./assets/mexico.json", "r", encoding="utf-8").read())

    fig = go.Figure()

    # Vamos a crear un mapa Choropleth con todas las variables anteriormente definidas.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=df.index,
            z=df["capita"],
            featureidkey="properties.NOM_ENT",
            colorscale="deep_r",
            marker_line_color="#FFFFFF",
            marker_line_width=1.5,
            zmin=valor_min,
            zmax=valor_max,
            colorbar=dict(
                x=0.03,
                y=0.5,
                ypad=50,
                ticks="outside",
                outlinewidth=2,
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=3,
                tickcolor="#EEEEEE",
                outlinecolor="#EEEEEE",
                ticklen=10,
            ),
        )
    )

    # Personalizamos la apariencia del mapa.
    fig.update_geos(
        fitbounds="geojson",
        showocean=True,
        oceancolor=PLOT_COLOR,
        showcountries=False,
        framecolor="#EEEEEE",
        framewidth=2,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        showlegend=False,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=80,
        margin_r=40,
        margin_b=60,
        margin_l=40,
        width=1920,
        height=1080,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.025,
                xanchor="center",
                yanchor="top",
                text=f"Ingresos por remesas hacia México por entidad durante {PERIODO_TIEMPO} de {año}",
                font_size=42,
            ),
            dict(
                x=0.0275,
                y=0.46,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Dólares per cápita durante el año",
            ),
            dict(
                x=0.01,
                y=-0.056,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.056,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=-0.056,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./0.png")

    # Vamos a crear dos tablas, cada una con la información de 16 entidades.
    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.03,
        specs=[[{"type": "table"}, {"type": "table"}]],
    )

    fig.add_trace(
        go.Table(
            columnwidth=[120, 120, 110],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Ingreso total (MDD)</b>",
                    "<b>USD per cápita ↓</b>",
                ],
                line_color="#EEEEEE",
                fill_color=HEADER_COLOR,
                align="center",
                height=45,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[:16],
                    df["VALOR_USD"][:16] / 1000000,
                    df["capita"][:16],
                ],
                fill_color=PLOT_COLOR,
                height=45,
                format=["", ",.0f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=1,
        row=1,
    )

    fig.add_trace(
        go.Table(
            columnwidth=[120, 120, 110],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Ingreso total (MDD)</b>",
                    "<b>USD per cápita ↓</b>",
                ],
                line_color="#EEEEEE",
                fill_color=HEADER_COLOR,
                align="center",
                height=45,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[16:],
                    df["VALOR_USD"][16:] / 1000000,
                    df["capita"][16:],
                ],
                fill_color=PLOT_COLOR,
                height=45,
                format=["", ",.0f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=2,
        row=1,
    )

    fig.update_layout(
        width=1920,
        height=840,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=25,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        paper_bgcolor=PAPER_COLOR,
    )

    fig.write_image("./1.png")

    # Unimos el mapa y las tablas en una sola imagen.
    image1 = Image.open("./0.png")
    image2 = Image.open("./1.png")

    result_width = image1.width
    result_height = image1.height + image2.height

    result = Image.new("RGB", (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, image1.height))

    result.save(f"./mapa_estatal_{año}.png")

    # Borramos las imágenes originales.
    os.remove("./0.png")
    os.remove("./1.png")


def comparacion_interanual(primer_año, segundo_año):
    """
    Crea una gráfica de barras horizontal mostrando el cambio
    porcentual interanual para cada entidad en México.

    Parameters
    ----------
    primre_año : int
        El año base que nos interesa comparar.

    segundo_año : int
        El año destino que nos interesa comparar.

    """

    # Cargamos el dataset de remesas por entidad.
    df = pd.read_csv("./data/remesas_entidad.csv", parse_dates=["PERIODO"])

    # Seleccionamos los años dentro de nuestro rango de interés.
    df = df[
        (df["PERIODO"].dt.year >= primer_año) & (df["PERIODO"].dt.year <= segundo_año)
    ]

    # Convertimos las cifras a millones de dólares.
    df["VALOR_USD"] /= 1000000

    # Transformamos nuestro dataset para que el índice sean los estados y las columnas los años.
    df = df.pivot_table(
        index="ENTIDAD",
        columns=df["PERIODO"].dt.year,
        values="VALOR_USD",
        aggfunc="sum",
    )

    # Calculamos el total nacional.
    df.loc["<b>Nacional</b>"] = df.sum(axis=0)

    # Calculamos el cambio porcentual.
    df["cambio"] = (df[segundo_año] - df[primer_año]) / df[primer_año] * 100

    # Preparamos el texto para cada observación.
    df["texto"] = df.apply(
        lambda x: (
            f" <b>{x['cambio']:,.0f}%</b> ({x[primer_año]:,.0f} → {x[segundo_año]:,.0f}) "
            if abs(x["cambio"]) >= 100
            else f" <b>{x['cambio']:,.1f}%</b> ({x[primer_año]:,.0f} → {x[segundo_año]:,.0f}) "
        ),
        axis=1,
    )

    # Ordenamos de mayor a menor basado en el cambio porcentual.
    df.sort_values("cambio", ascending=False, inplace=True)

    # Calculamos el valor máximo para ajustar el rango del eje horizontal.
    valor_max = df["cambio"].abs().max()
    valor_max = ((valor_max // 2) + 1) * 2

    # Determinamos la posición de los textos para cada barra.
    df["ratio"] = df["cambio"].abs() / valor_max
    df["texto_pos"] = df["ratio"].apply(lambda x: "inside" if x >= 0.7 else "outside")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["cambio"],
            text=df["texto"],
            textposition=df["texto_pos"],
            textfont_color="#FFFFFF",
            orientation="h",
            marker_color=df["cambio"],
            marker_colorscale="geyser_r",
            marker_cmid=0,
            marker_line_width=0,
            textfont_size=30,
            textfont_family="Oswald",
        )
    )

    fig.update_xaxes(
        range=[valor_max * -1, valor_max],
        ticksuffix="%",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=20,
    )

    fig.update_yaxes(
        autorange="reversed",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1920,
        height=1920,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Comparación del ingreso por remesas en México durante {PERIODO_TIEMPO} ({primer_año} vs. {segundo_año})",
        title_x=0.5,
        title_y=0.985,
        margin_t=80,
        margin_r=40,
        margin_b=120,
        margin_l=280,
        title_font_size=36,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.99,
                y=0.0,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="bottom",
                align="left",
                bgcolor=PLOT_COLOR,
                bordercolor="#EEEEEE",
                borderwidth=1.5,
                borderpad=7,
                text="<b>Nota:</b><br>Cifras expresadas en millones de dólares.",
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
                x=0.58,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Cambio porcentual (cambio absoluto)",
            ),
            dict(
                x=1.0,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./comparacion_entidad_{primer_año}_{segundo_año}.png")


def plot_tendencias(primer_año, ultimo_año, orden):
    """
    Esta función crea una cuadrícula de sparklines con los
    estados que han crecido más en ingresos por remesas.

    Parameters
    ----------
    primer_año : int
        El año inicial que se desea comparar.

    ultimo_año :  int
        El año final que se desea comparar.

    orden : str
        Define si se mostrarán las entidades
        con mayor o menor crecimiento.
        Puede ser 'top' o 'bottom'.

    """

    # Cargamos el dataset de remesas por entidad.
    df = pd.read_csv("./data/remesas_entidad.csv", parse_dates=["PERIODO"])

    # Seleccionamos los años dentro de nuestro rango de interés.
    df = df[
        (df["PERIODO"].dt.year >= primer_año) & (df["PERIODO"].dt.year <= ultimo_año)
    ]

    # Transformamos nuestro DataFrame para que el índice sean los trimestres y las columnas las entidades.
    df = df.pivot_table(
        index="PERIODO",
        columns="ENTIDAD",
        values="VALOR_USD",
        aggfunc="sum",
    )

    # Cargamos el IPC y el tipo de cambio trimestral.
    ipc_fx = cargar_deflactadores("trimestral")
    
    # Preparamos el coeficiente de deflactación para cada trimestre.
    ipc_fx = ipc_fx["TIPO_CAMBIO"] * ipc_fx["factor"]

    # Deflactamos cada entidad y convertimos las cifras en millones de pesos.
    for col in df.columns:
        df[col] = df[col] * ipc_fx / 1000000

    # Remuestreamos con la suma anual.
    df = df.resample("YS").sum()

    # Solo vamos a necesitar el año de cada fecha.
    df.index = df.index.year
    
    # Modificamos el DataFrame para que ahora los años sean las columnas.
    # Esto hace más fácil calcular el cambio porcentual.
    df = df.transpose()

    # Vamos a calcular el cambio porcentual entre el primer y último año.
    df["change"] = (df[ultimo_año] - df[primer_año]) / df[primer_año] * 100

    # Calculamos el cambio nacional.
    cambio = (df[ultimo_año].sum() - df[primer_año].sum()) / df[primer_año].sum() * 100

    # Quitamos los municipsios con valores infinitos.
    df = df[df["change"] != np.inf]

    # Ordenamos el DataFrame de acuerdo al valor del parámetro 'orden'.
    # Aprovechamos para ajustar el título del gráfico.
    if orden == "top":
        df.sort_values("change", ascending=False, inplace=True)
        titulo = f"Las 15 entidades de México con <b>mayor</b> crecimiento real en ingresos por remesas ({primer_año} vs. {ultimo_año})<br>(cifras en millones de pesos a precios constantes de {FECHA_INFLACION})"
    elif orden == "bottom":
        df.sort_values("change", ascending=True, inplace=True)
        titulo = f"Las 15 entidades de México con <b>menor</b> crecimiento real en ingresos por remesas ({primer_año} vs. {ultimo_año})<br>(cifras en millones de pesos a precios constantes de {FECHA_INFLACION})"

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

            textos[0] = (
                f"<b>{primer_valor / 1000:,.1f}k</b>"
                if primer_valor >= 1000
                else f"<b>{primer_valor:,.0f}</b>"
            )
            textos[-1] = (
                f"<b>{ultimo_valor / 1000:,.1f}k</b>"
                if ultimo_valor >= 1000
                else f"<b>{ultimo_valor:,.0f}</b>"
            )

            # Posicionamos los dos textos.
            text_pos = ["middle center" for _ in range(len(temp_df))]
            text_pos[0] = "top center"
            text_pos[-1] = "bottom center"

            # Calculamos el cambio porcentual y creamos el texto que irá en la anotación de cada cuadro.
            change = (ultimo_valor - primer_valor) / primer_valor * 100
            diff = ultimo_valor - primer_valor

            texto_anotaciones.append(
                f"<b>+{diff:,.0f}</b><br>+{change:,.0f}%".replace("+-", "-")
            )

            fig.add_trace(
                go.Scatter(
                    x=temp_df.index,
                    y=temp_df.values,
                    text=textos,
                    mode="markers+lines+text",
                    textposition=text_pos,
                    marker_color="#b2ff59",
                    marker_opacity=1.0,
                    marker_size=sizes,
                    marker_line_width=0,
                    line_width=4,
                    line_shape="spline",
                    line_smoothing=1.0,
                    textfont_size=22,
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
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=1.5,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        title_text="Millones de pesos",
        separatethousands=True,
        tickfont_size=20,
        tickformat="s",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
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
        margin_t=240,
        margin_l=140,
        margin_r=60,
        margin_b=150,
        title_text=titulo,
        title_x=0.5,
        title_y=0.97,
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
            font_color="#b2ff59",
            bordercolor="#b2ff59",
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
        text=f"Crecimiento real a nivel nacional de {primer_año} a {ultimo_año}: <b>{cambio:,.2f}%</b>",
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

    fig.write_image(f"./estados_tendencia_{orden}.png")


def comparar_pib(año):
    """
    Esta función crea una gráfica de barras para comparar el valor
     de las remesas y el del PIB de cada entidad.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset del PIB por entidad.
    pib = pd.read_csv("./assets/pib_estatal.csv")

    # Seleccionamos los datos del año que nos interesa.
    pib = pib[pib["PERIODO"] == año]

    # Seleccionamos los datos del PIB total.
    pib = pib[pib["CLAVE_INDUSTRIA"] == "PIB"]

    # Vamos a utilizar los valores corrientes.
    pib = pib.groupby("ENTIDAD").last()["VALOR_CORRIENTE"] * 1000000

    # Cargamos el dataset del tipo de cambio.
    fx = pd.read_csv("./assets/USDMXN.csv", parse_dates=["PERIODO"], index_col=0)

    # Remuestramos por promedio trimestral.
    fx = fx.resample("QS").mean()

    # Cargamos el dataset de remesas por entidad.
    df = pd.read_csv("./data/remesas_entidad.csv", parse_dates=["PERIODO"], index_col=0)

    # Seleccionamos los reigstros del año especificado.
    df = df[df.index.year == año]

    # Agregamos el tipo de cmabio.
    df["cambio"] = fx["TIPO_CAMBIO"]

    # Calculamos el valor en pesos.
    df["pesos"] = df["VALOR_USD"] * df["cambio"]

    # Agrupamos por entidad.
    df = df.groupby("ENTIDAD").sum()

    # Calculamos el total anual.
    df.loc["Nacional"] = df.sum(axis=0)

    # Agregamos el PIB a cada total.
    df["pib"] = pib

    # Calculamos el porcentaje.
    df["perc"] = df["pesos"] / df["pib"] * 100

    # Ordenamos de mayor a menor.
    df.sort_values("perc", ascending=False, inplace=True)

    # Creamos el texto para cada barra.
    df["text"] = df.apply(
        lambda x: f" {x['perc']:,.1f}% ({x['pesos'] / 1000000:,.0f}) ", axis=1
    )

    # Calculamos la posición para cada texto.
    df["ratio"] = df["perc"] / df["perc"].max()
    df["text_pos"] = df["ratio"].apply(lambda x: "inside" if x >= 0.95 else "outside")

    # Todas las barrras serán rojas excepto la del total nacional.
    df["color"] = df.index.map(lambda x: "#ffd54f" if x == "Nacional" else "#e57373")

    # Hacemos la categoría nacional en negritas.
    df.index = df.index.str.replace("Nacional", "<b>Nacional</b>")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["perc"],
            text=df["text"],
            textfont_color="#FFFFFF",
            textfont_family="Oswald",
            textposition=df["text_pos"],
            orientation="h",
            marker_color=df["color"],
            marker_cornerradius=45,
            width=0.6,
        )
    )

    fig.update_xaxes(
        range=[0, df["perc"].max() * 1.01],
        ticksuffix="%",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=20,
    )

    fig.update_yaxes(
        autorange="reversed",
        ticks="outside",
        ticklen=10,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
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
        title_text=f"Valor de los ingresos por remesas respecto al PIB estatal en México durante {año}",
        title_x=0.5,
        title_y=0.985,
        margin_t=80,
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
                bordercolor="#EEEEEE",
                borderwidth=1.5,
                borderpad=7,
                bgcolor=PLOT_COLOR,
                text="<b>Notas:</b><br>Los ingresos por remesas no forman parte del PIB, sin embargo,<br>se comparan para medir su importancia en la economía estatal.<br>Las cifras están expresadas en millones de pesos corrientes.",
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
                text="Porcentaje respecto al PIB (millones de pesos nominales)",
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

    fig.write_image(f"./remesas_pib_{año}.png")


if __name__ == "__main__":
    plot_mapa(2025)
    comparacion_interanual(2024, 2025)

    plot_tendencias(2016, 2025, "top")
    plot_tendencias(2016, 2025, "bottom")

    comparar_pib(2024)
