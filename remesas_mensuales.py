"""
Este script muestra la tendencia y totales de remesas hacia México.

Fuente remesas mensuales:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CE81&locale=es

Fuente tipo de cambio:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=6&accion=consultarCuadro&idCuadro=CF86&locale=es

fuente IPC:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CP154&locale=es

"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import STL

# Mes y año en que se recopilaron los datos.
FECHA_FUENTE = "febrero 2025"

# Mes y año del IPC de referencia.
FECHA_INFLACION = "diciembre de 2024"


def plot_mensuales():
    """
    Crea una gráfica de barras con las cifras mensuales de remesas en dólares nominales.
    """

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv(
        "./data/remesas_mensuales.csv", parse_dates=["fecha"], index_col="fecha"
    )

    # Calculamos el total de remesas por año para los últimos 10 años.
    por_año = df.resample("YS").sum().tail(10)

    # Vamos a crear una tabla con los totales.
    tabla = "<b>Total por año (MDD)</b>"

    for k, v in por_año["total"].items():
        tabla += f"<br>{k.year}: {v:,.0f}"

    # Seleccionamos los últimos 10 años (120 meses).
    df = df.tail(120)

    # Calculamos la tendencia.
    df["trend"] = STL(df["total"]).fit().trend

    # Vamos a crear una gráfica de barras con las cifras absolutas y una
    # gráfica de linea con la tendencia usando el promedio móvil.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["total"],
            name="Cifras absolutas",
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
            line_width=5,
            opacity=1.0,
        )
    )

    fig.update_xaxes(
        tickformat="%m<br>'%y",
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.35,
        mirror=True,
        nticks=50,
    )

    fig.update_yaxes(
        title="Millones de dólares (nominales)",
        tickfont_size=16,
        separatethousands=True,
        ticks="outside",
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=True,
        gridwidth=0.35,
        showline=True,
        mirror=True,
        nticks=14,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        showlegend=True,
        legend_x=0.5,
        legend_y=0.98,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1280,
        height=720,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=18,
        title_text="Ingresos mensuales por remesas hacia México durante los últimos 10 años (dólares nominales)",
        title_x=0.5,
        title_y=0.97,
        margin_t=60,
        margin_l=110,
        margin_r=40,
        margin_b=100,
        title_font_size=24,
        plot_bgcolor="#111111",
        paper_bgcolor="#282A3A",
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
    fx = pd.read_csv("./assets/USDMXN.csv", parse_dates=["Fecha"], index_col=0)

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv("./data/remesas_mensuales.csv", parse_dates=["fecha"], index_col=0)

    # Agregamos el tipo de cambio mensual.
    df["cambio"] = fx["Cambio"]

    # Hacemos la conversión a pesos.
    df["pesos"] = df["total"] * df["cambio"]

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
            marker_color="#e64a19",
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
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.35,
        mirror=True,
        nticks=50,
    )

    fig.update_yaxes(
        title="Millones de pesos (nominales)",
        tickfont_size=16,
        separatethousands=True,
        ticks="outside",
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=True,
        gridwidth=0.35,
        showline=True,
        mirror=True,
        nticks=14,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        showlegend=True,
        legend_x=0.5,
        legend_y=0.98,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1280,
        height=720,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=18,
        title_text="Ingresos mensuales por remesas hacia México durante los últimos 10 años (pesos nominales)",
        title_x=0.5,
        title_y=0.97,
        margin_t=60,
        margin_l=110,
        margin_r=40,
        margin_b=100,
        title_font_size=24,
        plot_bgcolor="#111111",
        paper_bgcolor="#282A3A",
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
    ipc = pd.read_csv("./assets/IPC.csv", parse_dates=["Fecha"], index_col=0)

    # Escogemos un IPC de referencia (el más reciente)
    ipc_referencia = ipc["IPC"].iloc[-1]

    # Calculamos el factor.
    ipc["factor"] = ipc_referencia / ipc["IPC"]

    # Cargamos el dataset del tipo de cambio.
    fx = pd.read_csv("./assets/USDMXN.csv", parse_dates=["Fecha"], index_col=0)

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv("./data/remesas_mensuales.csv", parse_dates=["fecha"], index_col=0)

    # Agregamos el tipo de cambio mensual.
    df["cambio"] = fx["Cambio"]

    # Hacemos la conversión a pesos.
    df["pesos"] = df["total"] * df["cambio"]

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
            line_width=5,
            opacity=1.0,
        )
    )

    fig.update_xaxes(
        tickformat="%m<br>'%y",
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.35,
        mirror=True,
        nticks=50,
    )

    fig.update_yaxes(
        title=f"Millones de pesos a precios constantes de {FECHA_INFLACION}",
        title_font_size=20,
        tickfont_size=16,
        separatethousands=True,
        ticks="outside",
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=True,
        gridwidth=0.35,
        showline=True,
        mirror=True,
        nticks=14,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        showlegend=True,
        legend_x=0.5,
        legend_y=0.98,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1280,
        height=720,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=18,
        title_text="Ingresos mensuales por remesas hacia México durante los últimos 10 años (pesos reales)",
        title_x=0.5,
        title_y=0.97,
        margin_t=60,
        margin_l=110,
        margin_r=40,
        margin_b=100,
        title_font_size=24,
        plot_bgcolor="#111111",
        paper_bgcolor="#282A3A",
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
    ipc = pd.read_csv("./assets/IPC.csv", parse_dates=["Fecha"], index_col=0)

    # Escogemos un IPC de referencia (el más reciente)
    ipc_referencia = ipc["IPC"].iloc[-1]

    # Calculamos el factor.
    ipc["factor"] = ipc_referencia / ipc["IPC"]

    # Cargamos el dataset del tipo de cambio.
    fx = pd.read_csv("./assets/USDMXN.csv", parse_dates=["Fecha"], index_col=0)

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv("./data/remesas_mensuales.csv", parse_dates=["fecha"], index_col=0)

    # Agregamos el tipo de cambio mensual.
    df["cambio"] = fx["Cambio"]

    # Hacemos la conversión a pesos.
    df["pesos"] = df["total"] * df["cambio"]

    # Agregamos la columna de inflación.
    df["inflacion"] = ipc["factor"]

    # Ajustamos por inflación para obtener pesos reales.
    df["real"] = df["pesos"] * df["inflacion"]

    # Calculamos el total de remesas por año.
    df = df.resample("YS").sum()

    # Cambiamos de fecha a integral para el índice.
    df.index = df.index.year

    # Nos limitamos a los úlitmos 25 años.
    df = df.tail(25)

    # Le daremos formato a las cifras para que sean más fáciles de interpretar.
    df["texto"] = df["real"].apply(lambda x: f"{x / 1000000:,.3f}")

    # Creamos la escala para el eje vertical.
    marcas = np.linspace(0, 1300000, 14)
    textos = [f"{item / 1000000:,.1f}" for item in marcas]
    textos[0] = "0"

    # Vamos a crear una gráfica de barras con las cifras absolutas y una
    # gráfica de linea con la tendencia usando el promedio móvil.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["real"],
            text=df["texto"],
            textfont_color="#FFFFFF",
            textfont_family="Oswald",
            textposition="outside",
            marker_color=df["real"],
            name="Cifras absolutas",
            marker_colorscale="agsunset",
            opacity=1.0,
            marker_line_width=0,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=50,
    )

    fig.update_yaxes(
        title=f"Billones de pesos a precios constantes de {FECHA_INFLACION}",
        tickvals=marcas,
        ticktext=textos,
        title_font_size=20,
        tickfont_size=16,
        ticks="outside",
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=True,
        gridwidth=0.35,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        showlegend=False,
        legend_x=0.5,
        legend_y=0.98,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1280,
        height=720,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=18,
        title_text="Evolución de los ingresos anuales por remesas hacia México (pesos reales)",
        title_x=0.5,
        title_y=0.97,
        margin_t=60,
        margin_l=110,
        margin_r=40,
        margin_b=85,
        title_font_size=26,
        plot_bgcolor="#111111",
        paper_bgcolor="#282A3A",
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
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro",
            ),
            dict(
                x=1.01,
                y=-0.13,
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
