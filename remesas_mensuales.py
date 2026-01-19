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
FECHA_FUENTE = "enero 2026"

# Mes y año del IPC de referencia.
FECHA_INFLACION = "diciembre de 2025"

# Paleta de colores para todas las gráficas.
PLOT_COLOR = "#1C1F1A"
PAPER_COLOR = "#262B23"


def plot_mensuales():
    """
    Crea una gráfica de barras con las cifras mensuales de remesas en dólares nominales.
    """

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Convertimos las cifras a millones de dólares.
    df /= 1000000

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
        tickcolor="#FFFFFF",
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
        tickcolor="#FFFFFF",
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
        title_text="Ingresos mensuales por remesas hacia México durante los últimos 10 años (dólares nominales)",
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
                bordercolor="#FFFFFF",
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

    fig.write_image("./remesas_mensuales.png")


def plot_pesos():
    """
    Crea una gráfica de barras con las cifras mensuales de remesas en pesos nominales.
    """

    # Cargamos el dataset del tipo de cambio.
    fx = pd.read_csv("./assets/USDMXN.csv", parse_dates=["PERIODO"], index_col=0)

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Convertimos las cifras a millones de dólares.
    df /= 1000000

    # Agregamos el tipo de cambio mensual.
    df["cambio"] = fx["TIPO_CAMBIO"]

    # Hacemos la conversión a pesos.
    df["pesos"] = df["VALOR_USD"] * df["cambio"]

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
        tickcolor="#FFFFFF",
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
        tickcolor="#FFFFFF",
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
        title_text="Ingresos mensuales por remesas hacia México durante los últimos 10 años (pesos nominales)",
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
                bordercolor="#FFFFFF",
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

    fig.write_image("./remesas_mensuales_pesos.png")


def plot_real():
    """
    Crea una gráfica de barras con las cifras mensuales de remesas en pesos reales.
    """

    # Cargamos el dataset del IPC.
    ipc = pd.read_csv("./assets/IPC.csv", parse_dates=["PERIODO"], index_col=0)

    # Escogemos un IPC de referencia (el más reciente)
    ipc_referencia = ipc["GENERAL"].iloc[-1]

    # Calculamos el factor.
    ipc["factor"] = ipc_referencia / ipc["GENERAL"]

    # Cargamos el dataset del tipo de cambio.
    fx = pd.read_csv("./assets/USDMXN.csv", parse_dates=["PERIODO"], index_col=0)

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Convertimos las cifras a millones de dólares.
    df /= 1000000

    # Agregamos el tipo de cambio mensual.
    df["cambio"] = fx["TIPO_CAMBIO"]

    # Hacemos la conversión a pesos.
    df["pesos"] = df["VALOR_USD"] * df["cambio"]

    # Agregamos la columna de inflación.
    df["inflacion"] = ipc["factor"]

    # Ajustamos por inflación para obtener pesos reales.
    df["real"] = df["pesos"] * df["inflacion"]

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
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=30,
    )

    fig.update_yaxes(
        title=f"Millones de pesos reales (precio base, {FECHA_INFLACION})",
        tickformat="s",
        separatethousands=True,
        ticks="outside",
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
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
        title_text="Ingresos mensuales por remesas hacia México durante los últimos 10 años (pesos reales)",
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
                bordercolor="#FFFFFF",
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

    fig.write_image("./remesas_mensuales_reales.png")


def plot_real_anual():
    """
    Crea una gráfica de barras con las cifras anuales de remesas en pesos reales.
    """

    # Cargamos el dataset del IPC.
    ipc = pd.read_csv("./assets/IPC.csv", parse_dates=["PERIODO"], index_col=0)

    # Escogemos un IPC de referencia (el más reciente)
    ipc_referencia = ipc["GENERAL"].iloc[-1]

    # Calculamos el factor.
    ipc["factor"] = ipc_referencia / ipc["GENERAL"]

    # Cargamos el dataset del tipo de cambio.
    fx = pd.read_csv("./assets/USDMXN.csv", parse_dates=["PERIODO"], index_col=0)

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Agregamos el tipo de cambio mensual.
    df["cambio"] = fx["TIPO_CAMBIO"]

    # Hacemos la conversión a pesos.
    df["pesos"] = df["VALOR_USD"] * df["cambio"]

    # Agregamos la columna de inflación.
    df["inflacion"] = ipc["factor"]

    # Ajustamos por inflación para obtener pesos reales.
    df["real"] = df["pesos"] * df["inflacion"]

    # Convertimos las cifras a billones de pesos.
    df["real"] /= 1000000000000

    # Calculamos el total de remesas por año.
    df = df.resample("YS").sum()

    # Cambiamos de fecha a integral para el índice.
    df.index = df.index.year

    # Nos limitamos a los úlitmos 20 años.
    df = df.tail(20)

    # Vamos a crear una gráfica de barras con las cifras absolutas y una
    # gráfica de linea con la tendencia usando el promedio móvil.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["real"],
            text=df["real"],
            texttemplate="%{text:,.3f}",
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
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=30,
    )

    fig.update_yaxes(
        range=[0, df["real"].max() * 1.08],
        title=f"Billones de pesos a precios constantes de {FECHA_INFLACION}",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
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
        title_text=f"Evolución de los ingresos anuales reales por remesas hacia México ({df.index.min()}-{df.index.max()})",
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
                bordercolor="#FFFFFF",
                borderwidth=1.5,
                borderpad=7,
                bgcolor="#111111",
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

    fig.write_image("./remesas_anuales_reales.png")


if __name__ == "__main__":
    plot_mensuales()
    plot_pesos()
    plot_real()
    plot_real_anual()
