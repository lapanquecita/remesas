"""
Este script muestra la tendencia y totales de remesas hacia México.

Fuente remesas mensuales:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CE81&locale=es

Fuente tipo de cambio:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=6&accion=consultarCuadro&idCuadro=CF86&locale=es

fuente IPC:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CP154&locale=es

"""

import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import STL


# Mes y año en que se recopilaron los datos.
FECHA_FUENTE = "julio 2026"

# Mes y año del IPC de referencia.
FECHA_INFLACION = "junio de 2026"

# Paleta de colores para todas las gráficas.
PLOT_COLOR = "#1C1F1A"
PAPER_COLOR = "#262B23"


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


def plot_mensuales(flujo):
    """
    Crea una gráfica de barras con las cifras mensuales de remesas en dólares nominales.

    Parameters
    ----------
    flujo : str
        Puede ser "Ingresos"|"Egresos" para diferenciar entre
        remesas enviadas o recibidas desde México.

    """

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Seleccionamos solo los registros del tipo de flujo indicado.
    df = df[df["FLUJO"] == flujo]

    # Convertimos las cifras a millones de dólares.
    df["VALOR_USD"] /= 1000000

    # Calculamos el total de remesas por año para los últimos 10 años.
    por_año = df.resample("YS").sum().tail(10)

    # Vamos a crear una tabla con los totales.
    tabla = "<b>Total por año (MDD)</b>"

    for k, v in por_año["VALOR_USD"].items():
        tabla += f"<br>{k.year}: {v:,.0f}"

    # Seleccionamos los últimos 10 años (120 meses).
    df = df.tail(120)

    # Calculamos la tendencia.
    df["trend"] = STL(df["VALOR_USD"]).fit().trend

    # El título cambia dependiendo el flujo.
    if flujo == "Ingresos":
        titulo = "Ingresos mensuales por remesas hacia México durante los últimos 10 años (dólares nominales)"
    elif flujo == "Egresos":
        titulo = "Egresos mensuales por remesas desde México durante los últimos 10 años (dólares nominales)"

    # Vamos a crear una gráfica de barras con las cifras absolutas y una
    # gráfica de linea con la tendencia usando el promedio móvil.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["VALOR_USD"],
            name="Serie original",
            marker_color="#04bfb3",
            opacity=1.0,
            marker_line_width=0,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["trend"],
            name="Tendencia (12 periodos)",
            mode="lines",
            line_color="#fbc02d",
            line_width=8,
            opacity=1.0,
        )
    )

    fig.update_xaxes(
        tickformat="%m<br>'%y",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=30,
    )

    fig.update_yaxes(
        title="Millones de dólares (nominales)",
        tickformat="s",
        separatethousands=True,
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showgrid=True,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=14,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        legend_orientation="h",
        showlegend=True,
        legend_x=0.5,
        legend_y=1.06,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=titulo,
        title_x=0.5,
        title_y=0.965,
        margin_t=120,
        margin_l=140,
        margin_r=40,
        margin_b=160,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.02,
                y=0.92,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                bordercolor="#EEEEEE",
                borderwidth=1.5,
                borderpad=7,
                bgcolor="#111111",
                align="left",
                text=tabla,
            ),
            dict(
                x=0.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./remesas_mensuales_{flujo.lower()}.png")


def plot_pesos(flujo):
    """
    Crea una gráfica de barras con las cifras mensuales de remesas en pesos nominales.

    Parameters
    ----------
    flujo : str
        Puede ser "Ingresos"|"Egresos" para diferenciar entre
        remesas enviadas o recibidas desde México.

    """

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Seleccionamos solo los registros del tipo de flujo indicado.
    df = df[df["FLUJO"] == flujo]

    # Convertimos las cifras a millones de dólares.
    df["VALOR_USD"] /= 1000000

    # Cargamos factor de inflación y tipo de cambio mensual.
    df = df.join(cargar_deflactadores("mensual"))

    # Hacemos la conversión a pesos corrientes.
    # Para esta función no ajustaremos por inflación.
    df["pesos"] = df["VALOR_USD"] * df["TIPO_CAMBIO"]

    # Calculamos el total de remesas por año para los últimos 10 años.
    por_año = df.resample("YS").sum().tail(10)

    # Vamos a crear una tabla con los totales.
    tabla = "<b>Total por año (MDP)</b>"

    for k, v in por_año["pesos"].items():
        tabla += f"<br>{k.year}: {v:,.0f}"

    # Seleccionamos los últimos 10 años (120 meses).
    df = df.tail(120)

    # Calculamos la tendencia.
    df["trend"] = STL(df["pesos"]).fit().trend

    # El título cambia dependiendo el flujo.
    if flujo == "Ingresos":
        titulo = "Ingresos mensuales por remesas hacia México durante los últimos 10 años (pesos nominales)"
    elif flujo == "Egresos":
        titulo = "Egresos mensuales por remesas desde México durante los últimos 10 años (pesos nominales)"

    # Vamos a crear una gráfica de barras con las cifras absolutas y una
    # gráfica de linea con la tendencia usando el promedio móvil.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["pesos"],
            name="Cifras absolutas",
            marker_color="#ff4081",
            opacity=1.0,
            marker_line_width=0,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["trend"],
            name="Tendencia (12 periodos)",
            mode="lines",
            line_color="#fbc02d",
            line_width=5,
            opacity=1.0,
        )
    )

    fig.update_xaxes(
        tickformat="%m<br>'%y",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=30,
    )

    fig.update_yaxes(
        title="Millones de pesos (nominales)",
        separatethousands=True,
        tickformat="s",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showgrid=True,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=14,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        legend_orientation="h",
        showlegend=True,
        legend_x=0.5,
        legend_y=1.06,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=titulo,
        title_x=0.5,
        title_y=0.965,
        margin_t=120,
        margin_l=140,
        margin_r=40,
        margin_b=160,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.02,
                y=0.92,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                bordercolor="#EEEEEE",
                borderwidth=1.5,
                borderpad=7,
                bgcolor="#111111",
                align="left",
                text=tabla,
            ),
            dict(
                x=0.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./remesas_mensuales_pesos_{flujo.lower()}.png")


def plot_real(flujo):
    """
    Crea una gráfica de barras con las cifras mensuales de remesas en pesos reales.

    Parameters
    ----------
    flujo : str
        Puede ser "Ingresos"|"Egresos" para diferenciar entre
        remesas enviadas o recibidas desde México.

    """

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Seleccionamos solo los registros del tipo de flujo indicado.
    df = df[df["FLUJO"] == flujo]

    # Convertimos las cifras a millones de dólares.
    df["VALOR_USD"] /= 1000000

    # Cargamos factor de inflación y tipo de cambio mensual.
    df = df.join(cargar_deflactadores("mensual"))

    # Ajustamos por inflación y tipo de cambio para obtener pesos reales.
    df["real"] = df["VALOR_USD"] * df["factor"] * df["TIPO_CAMBIO"]

    # Calculamos el total de remesas por año para los últimos 10 años.
    por_año = df.resample("YS").sum().tail(10)

    # Vamos a crear una tabla con los totales.
    tabla = "<b>Total por año (MDP)</b>"

    for k, v in por_año["real"].items():
        tabla += f"<br>{k.year}: {v:,.0f}"

    # Seleccionamos los últimos 10 años (120 meses).
    df = df.tail(120)

    # Calculamos la tendencia.
    df["trend"] = STL(df["real"]).fit().trend

    # El título cambia dependiendo el flujo.
    if flujo == "Ingresos":
        titulo = "Ingresos mensuales por remesas hacia México durante los últimos 10 años (pesos reales)"
    elif flujo == "Egresos":
        titulo = "Egresos mensuales por remesas desde México durante los últimos 10 años (pesos reales)"

    # Vamos a crear una gráfica de barras con las cifras absolutas y una
    # gráfica de linea con la tendencia usando el promedio móvil.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["real"],
            name="Cifras absolutas",
            marker_color="#ab47bc",
            opacity=1.0,
            marker_line_width=0,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["trend"],
            name="Tendencia (12 periodos)",
            mode="lines",
            line_color="#fbc02d",
            line_width=8,
            opacity=1.0,
        )
    )

    fig.update_xaxes(
        tickformat="%m<br>'%y",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=30,
    )

    fig.update_yaxes(
        title=f"Millones de pesos constantes (base, {FECHA_INFLACION})",
        tickformat="s",
        separatethousands=True,
        ticks="outside",
        ticklen=10,
        title_standoff=6,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showgrid=True,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=14,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        legend_orientation="h",
        showlegend=True,
        legend_x=0.5,
        legend_y=1.06,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=titulo,
        title_x=0.5,
        title_y=0.965,
        margin_t=120,
        margin_l=140,
        margin_r=40,
        margin_b=160,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.02,
                y=0.92,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                bordercolor="#EEEEEE",
                borderwidth=1.5,
                borderpad=7,
                bgcolor="#111111",
                align="left",
                text=tabla,
            ),
            dict(
                x=0.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./remesas_mensuales_reales_{flujo.lower()}.png")


def plot_real_anual(flujo):
    """
    Crea una gráfica de barras con las cifras anuales de remesas en pesos reales.

    Parameters
    ----------
    flujo : str
        Puede ser "Ingresos"|"Egresos" para diferenciar entre
        remesas enviadas o recibidas desde México.

    """

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Seleccionamos solo los registros del tipo de flujo indicado.
    df = df[df["FLUJO"] == flujo]

    # Cargamos factor de inflación y tipo de cambio mensual.
    df = df.join(cargar_deflactadores("mensual"))

    # Ajustamos por inflación y tipo de cambio para obtener pesos reales.
    df["real"] = df["VALOR_USD"] * df["factor"] * df["TIPO_CAMBIO"]

    # Calculamos el total de remesas por año.
    df = df.resample("YS").sum()

    # Cambiamos de fecha a integral para el índice.
    df.index = df.index.year

    # Nos limitamos a los úlitmos 20 años.
    df = df.tail(20)

    # El título cambia dependiendo el flujo.
    if flujo == "Ingresos":
        titulo = f"Evolución de los ingresos anuales reales por remesas hacia México ({df.index.min()}-{df.index.max()})"
        titulo_y = f"Billones de pesos a precios constantes de {FECHA_INFLACION}"

        # Convertimos las cifras a billones de pesos.
        df["real"] /= 1000000000000
        plantilla = "%{text:,.3f}"
    elif flujo == "Egresos":
        titulo = f"Evolución de los egresos anuales reales por remesas desde México ({df.index.min()}-{df.index.max()})"
        titulo_y = f"Millones de pesos a precios constantes de {FECHA_INFLACION}"

        # Convertimos las cifras a millones de pesos.
        df["real"] /= 1000000
        plantilla = "%{text:,.0f}"

    # Vamos a crear una gráfica de barras con las cifras absolutas y una
    # gráfica de linea con la tendencia usando el promedio móvil.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["real"],
            text=df["real"],
            texttemplate=plantilla,
            textfont_color="#FFFFFF",
            textfont_family="Oswald",
            textposition="outside",
            marker_color=df["real"],
            marker_colorscale="redor_r",
            opacity=1.0,
            marker_line_width=0,
            textfont_size=36,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=len(df) + 1,
    )

    fig.update_yaxes(
        range=[0, df["real"].max() * 1.08],
        title=titulo_y,
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showgrid=True,
        gridwidth=0.5,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=titulo,
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=140,
        margin_r=40,
        margin_b=125,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.02,
                y=0.92,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                bordercolor="#EEEEEE",
                borderwidth=1.5,
                borderpad=7,
                font_size=22,
                bgcolor=PLOT_COLOR,
                align="left",
                text=f"<b>Metodología:</b><br>Se convirtieron los dólares a pesos utilizando<br>el tipo de cambio de cada mes, se ajustó por<br>inflación a valores de {FECHA_INFLACION} y se<br>agruparon los resultados de forma anual.",
            ),
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./remesas_anuales_reales_{flujo.lower()}.png")


def remesa_promedio(flujo):
    """
    Genera una gráfica de oruga mostrando la
    evolución del motno promedio por remesa.

    Parameters
    ----------
    flujo : str
        Puede ser "Ingresos"|"Egresos" para diferenciar entre
        remesas enviadas o recibidas desde México.

    """

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Seleccionamos solo los registros del tipo de flujo indicado.
    df = df[df["FLUJO"] == flujo]

    # Cargamos factor de inflación y tipo de cambio mensual.
    df = df.join(cargar_deflactadores("mensual"))

    # Ajustamos por inflación y tipo de cambio para obtener pesos reales.
    df["real"] = df["VALOR_USD"] * df["factor"] * df["TIPO_CAMBIO"]

    # Calculamos el valor promedio or operación.
    df["valor_promedio"] = df["real"] / df["OPERACIONES"]

    # Para cada año vamos a a neceitar 3 valores.
    # Máximo, mínimo y promedio.
    df = df.resample("YS")["valor_promedio"].agg(max="max", min="min", promedio="mean")

    # Cambiamos de fecha a integral para el índice.
    df.index = df.index.year

    # El título cambia dependiendo el flujo.
    if flujo == "Ingresos":
        titulo = f"Evolución del monto promedio por remesa <b>hacia</b> México ({df.index.min()}-{df.index.max()})"
        color = "#ffa726"
    elif flujo == "Egresos":
        titulo = f"Evolución del monto promedio por remesa <b>desde</b> México ({df.index.min()}-{df.index.max()})"
        color = "#ba68c8"

    # Haremos una gráfica tipo oruga.
    # Cada año será representado por el
    # promedio anual y su variabilidad.
    fig = go.Figure()

    x = list()
    y = list()

    for index, row in df.iterrows():
        x.extend([index, index, None])
        y.extend([row["min"], row["max"], None])

    fig.add_traces(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name="Rango anual (míniom-máximo)",
            line_color="#FFFFFF",
            line_width=4,
        )
    )

    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["promedio"],
            mode="markers",
            name="Promedio anual",
            marker_color=color,
            marker_size=30,
        )
    )

    fig.update_xaxes(
        range=[df.index.min() - 0.7, df.index.max() + 0.7],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title=f"Pesos constantes (base, {FECHA_INFLACION})",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        linecolor="#EEEEEE",
        tickcolor="#EEEEEE",
        linewidth=2,
        showgrid=True,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=15,
    )

    fig.update_layout(
        showlegend=True,
        legend_borderwidth=1,
        legend_bordercolor="#EEEEEE",
        legend_x=0.99,
        legend_y=0.98,
        legend_xanchor="right",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=titulo,
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=140,
        margin_r=40,
        margin_b=125,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.02,
                y=0,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="bottom",
                bordercolor="#EEEEEE",
                borderwidth=1.5,
                borderpad=7,
                bgcolor=PLOT_COLOR,
                align="left",
                font_size=22,
                text="<b>Nota:</b> El promedio, mínimo y máximo anuales son calculados<br>a partir de los montos promedio mensuales en pesos constantes.",
            ),
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./remesas_monto_promedio_{flujo.lower()}.png")


if __name__ == "__main__":
    plot_mensuales("Ingresos")
    plot_mensuales("Egresos")

    plot_pesos("Ingresos")
    plot_pesos("Egresos")

    plot_real("Ingresos")
    plot_real("Egresos")

    plot_real_anual("Ingresos")
    plot_real_anual("Egresos")

    remesa_promedio("Ingresos")
    remesa_promedio("Egresos")
