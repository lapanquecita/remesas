"""
Este script muestra la tendencia y totales de remesas hacia México.

Fuente:
https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CE81&locale=es

"""

import pandas as pd
import plotly.graph_objects as go


def plot_mensuales():

    # Cargamos el dataset de las remesas mensuales.
    df = pd.read_csv("./data/remesas_mensuales.csv",
                     parse_dates=["fecha"], index_col="fecha")

    # Calculamos el total de remesas por año para los últimos 10 años.
    por_año = df.resample("Y").sum().tail(10)

    # Vamos a crear una tabla con los totales.
    tabla = "<b>Total por año</b>"

    for k, v in por_año["total"].items():
        tabla += f"<br>{k.year}: {v:,.0f}"

    # Calculamos la media móvil a 12 periodos.
    df["rolling"] = df["total"].rolling(12).mean()

    # Seleccionamos los últimos 10 años (121 meses).
    df = df[-121:]

    # Calculamos el cambio porcentual del primer y último periodo.
    cambio = (df["rolling"].iloc[-1] - df["rolling"].iloc[0]) / \
        df["rolling"].iloc[0] * 100

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
            y=df["rolling"],
            name="Promedio móvil (12 periodos)",
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
        title="Millones de dólares",
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
        title_text="Ingresos mensuales por remesas hacia México durante los últimos 10 años",
        title_x=0.5,
        title_y=0.97,
        margin_t=60,
        margin_l=110,
        margin_r=40,
        margin_b=100,
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
                text=tabla
            ),
            dict(
                x=0.5,
                y=0.08,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                bordercolor="#FFFFFF",
                borderwidth=1.5,
                borderpad=7,
                bgcolor="#111111",
                text=f"Cambio porcentual (promedio móvil): <b>{cambio:,.2f}%</b>"
            ),
            dict(
                x=0.01,
                y=-0.17,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: Banxico (noviembre 2023)"
            ),
            dict(
                x=0.5,
                y=-0.17,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro"
            ),
            dict(
                x=1.01,
                y=-0.17,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            ),
        ]
    )

    fig.write_image("./remesas_mensuales.png")


if __name__ == "__main__":

    plot_mensuales()
