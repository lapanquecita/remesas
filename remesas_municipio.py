"""

Fuente: https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=1&accion=consultarCuadro&idCuadro=CE166&locale=es

"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_capita():
    """
    Esta función crea una tabla con los municiios que reciben mas remesas per cápita.
    """

    # Cargamos el archivo CSV con la población por municipio.
    pop = pd.read_csv("./poblacion.csv")

    # Vamos a renombrar algunas entidades para que coincidan con el dataset de Banxico.
    pop = pop.replace(
        {"entidad": {
            "Coahuila de Zaragoza": "Coahuila",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz"}
         }
    )

    # Juntamos el nombre de la entidad y municipio para crear nuestro índice.
    pop.index = pop["municipio"] + ", " + pop["entidad"]

    # Solo necesitamos la columna de población.
    pop = pop["poblacion"]

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv("./remesas_municipio.csv")

    # La estructura de este dataset es jerárquica.
    # Tenemos que hacer algunas modificaciones para que coincida con el dataset de población.
    df["Entidad"] = df["Municipio"].apply(fill_entidad)
    df.fillna(method="ffill", inplace=True)
    df.index = df.apply(fill_cve, axis=1)

    # Quitamos los registros que no sean municipios.
    df = df[df["Municipio"].str.contains("⚬")]

    # Seleccionamos las columnas del año que nos interesa.
    cols = [col for col in df.columns if "2023" in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[cols]

    # Quitamos los decimales de las cifras.
    df["total"] = df.sum(axis=1) * 1000000

    # Asignamos la población a cada municipio.
    df["pop"] = df.index.map(pop)

    # Rellenamos con 0 a los municipios no identificados.
    df = df.fillna(0)

    # Calculamos el valor per cápita.
    df["capita"] = df["total"] / df["pop"]

    # Ordenamos per cápita de mayor a menor.
    df = df.sort_values("capita", ascending=False)

    # Quitamos los valores infinitos.
    df = df[df["capita"] != np.inf]

    # Seleccionamos las primeras 30 filas.
    df = df[:30]

    # Para el rank resetearemos el índice y le sumaremos 1, para que sea del 1 al 30 en vez del 0 al 29.
    df.reset_index(inplace=True)
    df.index = df.index + 1

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[50, 200, 100, 100],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    f"<b>Municipio, Entidad</b>",
                    # f"<b>Población 2020</b>",
                    f"<b>Remesas en dólares</b>",
                    "<b>Per cápita ↓</b>",
                ],
                font_color="#FFFFFF",
                line_width=0.75,
                fill_color="#E94560",
                align="center",
                height=28
            ),
            cells=dict(
                values=[
                    df.index,
                    df["index"],
                    # df["pop"],
                    df["total"],
                    df["capita"]
                ],
                line_width=0.75,
                fill_color="#1A1A2E",
                height=28,
                format=["", "", ",.0f", ",.2f"],
                prefix=["", "", "$", "$"],
                align=["center", "left", "left", "center", "center"]
            )
        )
    )

    fig.update_layout(
        showlegend=False,
        width=840,
        height=1050,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=16,
        margin_t=110,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=26,
        title_text="Los 30 municipios de México con mayores ingresos por remesas<br><b>per cápita</b> durante el primer trimestre del 2023",
        paper_bgcolor="#16213E",
        annotations=[
            dict(
                x=0.015,
                y=0.015,
                xanchor="left",
                yanchor="top",
                text="Fuente: Banxico (julio 2023)"
            ),
            dict(
                x=0.5,
                y=0.015,
                xanchor="center",
                yanchor="top",
                text="Nacional: 110.86 dólares per cápita"
            ),
            dict(
                x=1.01,
                y=0.015,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            )
        ]
    )

    fig.write_image("./tabla_capita.png")


def plot_absolutos():
    """
    Esta función crea una tabla con los municiios que reciben mas remesas totales.
    """

    # Cargamos el archivo CSV con la población por municipio.
    pop = pd.read_csv("./poblacion.csv")

    # Vamos a renombrar algunas entidades para que coincidan con el dataset de Banxico.
    pop = pop.replace(
        {"entidad": {
            "Coahuila de Zaragoza": "Coahuila",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz"}
         }
    )

    # Juntamos el nombre de la entidad y municipio para crear nuestro índice.
    pop.index = pop["municipio"] + ", " + pop["entidad"]

    # Solo necesitamos la columna de población.
    pop = pop["poblacion"]

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv("./remesas_municipio.csv")

    # La estructura de este dataset es jerárquica.
    # Tenemos que hacer algunas modificaciones para que coincida con el dataset de población.
    df["Entidad"] = df["Municipio"].apply(fill_entidad)
    df.fillna(method="ffill", inplace=True)
    df.index = df.apply(fill_cve, axis=1)

    # Quitamos los registros que no sean municipios.
    df = df[df["Municipio"].str.contains("⚬")]

    # Seleccionamos las columnas del año que nos interesa.
    cols = [col for col in df.columns if "2023" in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[cols]

    # Quitamos los decimales de las cifras.
    df["total"] = df.sum(axis=1) * 1000000

    # Asignamos la población a cada municipio.
    df["pop"] = df.index.map(pop)

    # Rellenamos con 0 a los municipios no identificados.
    df = df.fillna(0)

    # Calculamos el valor per cápita.
    df["capita"] = df["total"] / df["pop"]

    # Ordenamos por el total de mayor a menor.
    df = df.sort_values("total", ascending=False)

    # Quitamos los valores infinitos.
    df = df[df["capita"] != np.inf]

    # Seleccionamos las primeras 30 filas.
    df = df[:30]

    # Para el rank resetearemos el índice y le sumaremos 1, para que sea del 1 al 30 en vez del 0 al 29.
    df.reset_index(inplace=True)
    df.index = df.index + 1

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[50, 200, 110, 80],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    f"<b>Municipio, Entidad</b>",
                    # f"<b>Población 2020</b>",
                    f"<b>Remesas en dólares ↓</b>",
                    "<b>Per cápita</b>",
                ],
                font_color="#FFFFFF",
                line_width=0.75,
                fill_color="#f4511e",
                align="center",
                height=28
            ),
            cells=dict(
                values=[
                    df.index,
                    df["index"],
                    # df["pop"],
                    df["total"],
                    df["capita"]
                ],
                line_width=0.75,
                fill_color="#182c25",
                height=28,
                format=["", "", ",.0f", ",.2f"],
                prefix=["", "", "$", "$"],
                align=["center", "left", "left", "center", "center"]
            )
        )
    )

    fig.update_layout(
        showlegend=False,
        width=840,
        height=1050,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=16,
        margin_t=110,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=26,
        title_text="Los 30 municipios de México con mayores ingresos por remesas<br><b>totales</b> durante el primer trimestre del 2023",
        paper_bgcolor="#1e453e",
        annotations=[
            dict(
                x=0.015,
                y=0.015,
                xanchor="left",
                yanchor="top",
                text="Fuente: Banxico (julio 2023)"
            ),
            dict(
                x=0.5,
                y=0.015,
                xanchor="center",
                yanchor="top",
                text="Nacional: 13,970,353,200 dólares"
            ),
            dict(
                x=1.01,
                y=0.015,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            )
        ]
    )

    fig.write_image("./tabla_absolutos.png")


def fill_entidad(x):
    """
    En el dataset de municipios los registros que empiezan con un círculo son las entidades.
    Si el registro es una entidad la regresamos limpia, de lo contrario regresamos un valor nulo.
    """

    if "●" in x:
        return x.replace("●", "").strip()
    else:
        return None


def fill_cve(x):
    """
    Vamos a crear un valor 'cve' igual al del dataset de población.
    Para esto limpiamos el nombre del municipio y lo juntamos con la entidad.
    """

    return x["Municipio"].replace("⚬", "").strip() + ", " + x["Entidad"]


def plot_tendencias():
    """
    Esta función crea una cuadrícula de sparklines con los municipios que han crecido más en ingresos por remesas.
    """

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv("./remesas_municipio.csv")

    # La estructura de este dataset es jerárquica.
    # Tenemos que hacer algunas modificaciones para asignar la entdad a cada municipio.
    df["Entidad"] = df["Municipio"].apply(fill_entidad)
    df.fillna(method="ffill", inplace=True)
    df.index = df.apply(fill_cve, axis=1)

    # Quitamos los registros que no sean municipios.
    df = df[df["Municipio"].str.contains("⚬")]

    # Vamos a sumar los totales de remesas por año.
    # PAra esto crearemos un ciclo del 2013 al 2022.
    for year in range(2013, 2023):

        cols = [col for col in df.columns if str(year) in col]
        df[str(year)] = df[cols].sum(axis=1)

    # Solo vamos a escoger las últimas columnas que creamos.
    df = df.iloc[:, -10:]

    # Vamos a calcular el cambio porcentual del 2013 al 2022.
    df["change"] = (df["2022"] - df["2013"]) / df["2013"] * 100

    # Quitamos los municipsios con valores infinitos.
    df = df[df["change"] != np.inf]

    # Quitamos los municipios que hayan tenido menos de 10 millones de dólares durante el 2013.
    # Esto es con el propósito de eliminar ruido.
    df = df[df["2013"] >= 10]

    # Ordenamos los valores usando el cambio porcentual de mayor a menor.
    df = df.sort_values("change", ascending=False)

    # Esta lista contendrá los textos de cada anotación.
    texto_anotaciones = list()

    # Fromateamos los subtítulos para cada cuadro en nuestra cuadrícula.
    titles = [f"<b>{item}</b>" for item in df.index.tolist()]

    # Vamos a crear una cuadrícula de 3 columnas por 5 filas (15 cuadros).
    fig = make_subplots(
        rows=5, cols=3,
        horizontal_spacing=0.09,
        vertical_spacing=0.07,
        subplot_titles=titles
    )

    # Esta variable la usaremos para saber de que fila extraer la información.
    index = 0

    # Con ciclos anidados es como creamos la cuadrícula.
    for row in range(5):
        for column in range(3):

            # Seleccinamos la fila correspondiente a la variable index pero omitimos la última columna.
            # la cual contiene el cambio porcentual.
            temp_df = df.iloc[index, :-1]

            # Al íncide (que son los años) lq quitamos los primeros 2 dígitos y le agregamos un apóstrofe.
            # Esto es para reducir el tamaño de la etiqueta de cada año.
            temp_df.index = temp_df.index.map(lambda x: f"'{x[-2:]}")

            # Para nuestra gráfica de línea solo vamos a necesitar que el primer y último registro tengan un punto.
            sizes = [0 for _ in range(len(temp_df))]
            sizes[0] = 20
            sizes[-1] = 20

            # Vamos a extraer algunos valores para calcular el cambio porcentual y saber cual fue el valor máximo.
            primer_valor = temp_df[0]
            ultimo_valor = temp_df[-1]
            valor_maximo = temp_df.max()

            # Solo el primer y último registro llevarán un texto con sus valores.
            textos = ["" for _ in range(len(temp_df))]
            textos[0] = f"<b>{primer_valor:,.1f}</b>"
            textos[-1] = f"<b>{ultimo_valor:,.1f}</b>"

            # Posicionar los textos es un poco complicado ya que se pueden salir fácilmente
            # de la gráfica, con el siguiente código detectamos estos escenarios y ajustamos la posición.
            text_pos = ["middle center" for _ in range(len(temp_df))]

            # Este código ajusta el primer texto.
            if primer_valor == valor_maximo:
                text_pos[0] = "middle right"
            else:
                text_pos[0] = "top center"

            # Este código ajusta el último texto.
            if ultimo_valor == valor_maximo:
                text_pos[-1] = "middle left"
            else:
                text_pos[-1] = "bottom center"

            # Calculamos el cambio porcentual y creamos el texto que irá en la anotación de cada cuadro.
            change = (ultimo_valor - primer_valor) / primer_valor * 100
            diff = ultimo_valor - primer_valor
            texto_anotaciones.append(f"<b>+{diff:,.1f}</b><br>+{change:,.2f}%")

            fig.add_trace(
                go.Scatter(
                    x=temp_df.index,
                    y=temp_df.values,
                    text=textos,
                    mode="markers+lines+text",
                    textposition=text_pos,
                    textfont_size=18,
                    marker_color="#b2ff59",
                    marker_opacity=1.0,
                    marker_size=sizes,
                    marker_line_width=0,
                    line_width=4,
                    line_shape="spline",
                    line_smoothing=1.0,
                ),
                row=row+1, col=column+1)

            # Sumamos 1 a esta variable para que el siguiente cuadro extraíga la siguiente fila.
            index += 1

    fig.update_xaxes(
        tickfont_size=14,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=1.5,
        showline=True,
        gridwidth=0.35,
        mirror=True,
        nticks=15
    )

    fig.update_yaxes(
        title_text="Millones de dólares",
        separatethousands=True,
        tickfont_size=14,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=1.5,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=8
    )

    fig.update_layout(
        font_family="Lato",
        showlegend=False,
        width=1280,
        height=1600,
        font_color="#FFFFFF",
        font_size=14,
        margin_t=140,
        margin_l=110,
        margin_r=40,
        margin_b=100,
        title_text="Los 15 municipios de México con mayor crecimiento en ingresos por remesas durante los últimos 10 años",
        title_x=0.5,
        title_y=0.985,
        title_font_size=26,
        plot_bgcolor="#171010",
        paper_bgcolor="#2B2B2B",
    )

    # Vamos a crear una anotación en cada cuadro con textos mostrando el total y el cambio porcentual.
    # Lo que vamos a hacer a continuación se puede considerar como un 'hack'.
    annotations_x = list()
    annotations_y = list()

    # Iteramos sobre todos los subtítulos de cada cuadro, los cuales son considerados como anotaciones.
    for annotation in fig["layout"]["annotations"]:

        # A cada subtítulo lo vamos a ajustar ligeramente.
        annotation["y"] += 0.005
        annotation["font"]["size"] = 20

        # Vamos a extraer las coordenadas X y Y de cada subtítulo para usarlas de referencia
        # para nuestras nuevas anotaciones.
        annotations_x.append(annotation["x"])
        annotations_y.append(annotation["y"])

    # Es momento de crear nuestras nuevas anotaciones.
    # Usando la función zip() podemos iterar sobre nuestras listas de valores al mismo tiempo.
    for x, y, t, in zip(annotations_x, annotations_y, texto_anotaciones):

        # Vamos a ajustar las nuevas anotaciones basandonos en las coornedas de los subtítulos.
        x -= 0.12
        y -= 0.035

        fig.add_annotation(
            x=x,
            xanchor="left",
            xref="paper",
            y=y,
            yanchor="top",
            yref="paper",
            text=t,
            font_color="#b2ff59",
            font_size=18,
            bordercolor="#b2ff59",
            borderpad=5,
            borderwidth=1.5,
            bgcolor="#171010",
        )

    fig.add_annotation(
        x=0.01,
        xanchor="left",
        xref="paper",
        y=-0.085,
        yanchor="bottom",
        yref="paper",
        text="Fuente: Banxico (julio 2023)"
    )

    fig.add_annotation(
        x=0.5,
        xanchor="center",
        xref="paper",
        y=1.04,
        yanchor="top",
        yref="paper",
        font_size=22,
        text="(sólo se tomaron en cuenta los municipios con al menos 10 mdd por ingresos de remesas durante el 2013)"
    )

    fig.add_annotation(
        x=0.5,
        xanchor="center",
        xref="paper",
        y=-0.085,
        yanchor="bottom",
        yref="paper",
        text="El crecimiento nacional por ingresos de remesas del 2013 al 2022 es de <b>162.34%</b>"
    )

    fig.add_annotation(
        x=1.01,
        xanchor="right",
        xref="paper",
        y=-0.085,
        yanchor="bottom",
        yref="paper",
        text="🧁 @lapanquecita"
    )

    fig.write_image("./municipios_tendencia.png")


if __name__ == "__main__":

    # plot_capita()
    # plot_absolutos()
    plot_tendencias()
