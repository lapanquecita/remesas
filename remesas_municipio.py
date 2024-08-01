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
FECHA_FUENTE = "agosto 2024"

# Periodo de tiempo del análisis.
PERIODO_TIEMPO = "enero-diciembre"


def plot_map(año):
    """
    Esta función crea un mpara choropleth de los municipios de México.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    """

    # El índice lo vamos a necesitar como cadena.
    pop_types = {"CVE": str}

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv", dtype=pop_types)

    # Renombramos algunos estados a sus nombres más comunes.
    pop["Entidad"] = pop["Entidad"].replace(
        {
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz",
        }
    )

    # Creamos el índice y seleccionamos las columnas de nuestro interés.
    pop.index = pop["Municipio"] + ", " + pop["Entidad"]
    pop = pop[["CVE", str(año)]]

    # Renombramos las columnas.
    pop.columns = ["CVE", "poblacion"]

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv("./data/remesas_municipio.csv")

    # La estructura de este dataset es jerárquica.
    # Tenemos que hacer algunas modificaciones para que coincida con el dataset de población.
    df["Entidad"] = df["Municipio"].apply(fill_entidad)
    df["Entidad"] = df["Entidad"].replace("México", "Estado de México")
    df.ffill(inplace=True)
    df.index = df.apply(fill_cve, axis=1)

    # Quitamos los registros que no sean municipios.
    df = df[df["Municipio"].str.contains("⚬")]

    # Seleccionamos las columnas del año que nos interesa.
    cols = [col for col in df.columns if str(año) in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[cols]

    # Quitamos los decimales de las cifras.
    df["total"] = df.sum(axis=1) * 1000000

    # Calculamos las remesas per cápita para toda la polación.
    subtitulo = f"Nacional: {df['total'].sum() / pop["poblacion"].sum():,.2f} dólares per cápita"

    # Asignamos la población a cada municipio.
    df = df.join(pop)

    # Rellenamos con 0 a los municipios no identificados.
    df = df.fillna(0)

    # Calculamos el valor per cápita.
    df["capita"] = df["total"] / df["poblacion"]

    # Quitamos los valores infinitos o en ceros.
    df = df[df["capita"] != np.inf]
    df = df[df["capita"] > 0]

    # Usaremos la clave del municipio como índice.
    df.set_index("CVE", inplace=True)

    # Calculamos algunas estadísticas descriptivas.
    estadisticas = [
        "Estadísticas descriptivas",
        f"Media: <b>{df['capita'].mean():,.1f}</b>",
        f"Mediana: <b>{df['capita'].median():,.1f}</b>",
        f"DE: <b>{df['capita'].std():,.1f}</b>",
        f"25%: <b>{df['capita'].quantile(.25):,.1f}</b>",
        f"75%: <b>{df['capita'].quantile(.75):,.1f}</b>",
        f"95%: <b>{df['capita'].quantile(.95):,.1f}</b>",
        f"Máximo: <b>{df['capita'].max():,.1f}</b>",
    ]

    estadisticas = "<br>".join(estadisticas)

    # Determinamos los valores mínimos y máximos para nuestra escala.
    # Para el valor máximo usamos el 95 percentil para mitigar los
    # efectos de valores atípicos.
    valor_min = df["capita"].min()
    valor_max = df["capita"].quantile(0.975)

    # Vamos a crear nuestra escala con 13 intervalos.
    marcas = np.linspace(valor_min, valor_max, 13)
    etiquetas = list()

    for item in marcas:
        etiquetas.append(f"{item:,.0f}")

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{valor_max:,.0f}"

    # Cargamos el GeoJSON de municipios de México.
    geojson = json.loads(open("./assets/mexico2019.json", "r", encoding="utf-8").read())

    # Estas listas serán usadas para configurar el mapa Choropleth.
    ubicaciones = list()
    valores = list()

    # Iteramos sobre cada municipio e nuestro GeoJSON.
    for item in geojson["features"]:
        geo = str(item["properties"]["CVEGEO"])

        # Si el municipio no se encuentra en nuestro DataFrame,
        # agregamos un valor nulo.
        try:
            value = df.loc[geo]["capita"]
        except Exception as _:
            value = None

        # Agregamos el objeto del municipio y su valor a las listas correspondientes.
        ubicaciones.append(geo)
        valores.append(value)

    fig = go.Figure()

    # Configuramos nuestro mapa Choropleth con todas las variables antes definidas.
    # El parámetro 'featureidkey' debe coincidir con el de la variable 'geo' que
    # extrajimos en un paso anterior.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=ubicaciones,
            z=valores,
            featureidkey="properties.CVEGEO",
            colorscale="solar",
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
    geojson_borde = json.loads(
        open("./assets/mexico.json", "r", encoding="utf-8").read()
    )

    # Estas listas serán usadas para configurar el mapa Choropleth.
    ubicaciones_borde = list()
    valores_borde = list()

    # Iteramos sobre cada entidad dentro de nuestro archivo GeoJSON de México.
    for item in geojson_borde["features"]:
        geo = item["properties"]["NOMGEO"]

        # Alimentamos las listas creadas anteriormente con la ubicación y su valor per capita.
        ubicaciones_borde.append(geo)
        valores_borde.append(1)

    # Este mapa tiene mucho menos personalización.
    # Lo único que necesitamos es que muestre los contornos
    # de cada entidad.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson_borde,
            locations=ubicaciones_borde,
            z=valores_borde,
            featureidkey="properties.NOMGEO",
            colorscale=["hsla(0, 0, 0, 0)", "hsla(0, 0, 0, 0)"],
            marker_line_color="#FFFFFF",
            marker_line_width=4,
            showscale=False,
        )
    )

    # Personalizamos algunos aspectos del mapa, como el color del oceáno
    # y el del terreno.
    fig.update_geos(
        fitbounds="locations",
        showocean=True,
        oceancolor="#092635",
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
        font_family="Lato",
        font_color="#FFFFFF",
        margin_t=50,
        margin_r=100,
        margin_b=30,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor="#393053",
        annotations=[
            dict(
                x=0.5,
                y=0.985,
                xanchor="center",
                yanchor="top",
                text=f"Ingresos por remesas per cápita en municipios de México durante {PERIODO_TIEMPO} de {año}",
                font_size=140,
            ),
            dict(
                x=0.02,
                y=0.49,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Dólares per cápita durante el año",
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

    fig.write_image(f"./municipal_{año}.png")


def plot_capita(año):
    """
    Esta función crea una tabla con los municiios que reciben mas remesas per cápita.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    """

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv")

    # Renombramos algunos estados a sus nombres más comunes.
    pop["Entidad"] = pop["Entidad"].replace(
        {
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz",
        }
    )

    # Creamos el índice y seleccionamos las columnas de nuestro interés.
    pop.index = pop["Municipio"] + ", " + pop["Entidad"]
    pop = pop[str(año)]

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv("./data/remesas_municipio.csv")

    # La estructura de este dataset es jerárquica.
    # Tenemos que hacer algunas modificaciones para que coincida con el dataset de población.
    df["Entidad"] = df["Municipio"].apply(fill_entidad)
    df["Entidad"] = df["Entidad"].replace("México", "Estado de México")
    df.ffill(inplace=True)
    df.index = df.apply(fill_cve, axis=1)

    # Quitamos los registros que no sean municipios.
    df = df[df["Municipio"].str.contains("⚬")]

    # Seleccionamos las columnas del año que nos interesa.
    cols = [col for col in df.columns if str(año) in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[cols]

    # Quitamos los decimales de las cifras.
    df["total"] = df.sum(axis=1) * 1000000

    # Calculamos las remesas per cápita para toda la polación.
    subtitulo = f"Nacional: {df['total'].sum() / pop.sum():,.2f} dólares per cápita"

    # Asignamos la población a cada municipio.
    df["pop"] = pop

    # Rellenamos con 0 a los municipios no identificados.
    df = df.fillna(0)

    # Calculamos el valor per cápita.
    df["capita"] = df["total"] / df["pop"]

    # Ordenamos per cápita de mayor a menor.
    df = df.sort_values("capita", ascending=False)

    # Quitamos los valores infinitos.
    df = df[df["capita"] != np.inf]

    # Seleccionamos las primeras 30 filas.
    df = df.head(30)

    # Para el rank resetearemos el índice y le sumaremos 1, para que sea del 1 al 30 en vez del 0 al 29.
    df.reset_index(inplace=True)
    df.index += 1

    # Acortamos el nombre del municipio más largo de México.
    df["index"] = df["index"].replace(
        {
            "Dolores Hidalgo Cuna de la Independencia Nal., Guanajuato": "Dolores Hidalgo, Guanajuato",
        }
    )

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[50, 200, 100, 100],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    "<b>Municipio, Entidad</b>",
                    "<b>Remesas en dólares</b>",
                    "<b>Per cápita ↓</b>",
                ],
                font_color="#FFFFFF",
                line_width=0.75,
                fill_color="#E94560",
                align="center",
                height=28,
            ),
            cells=dict(
                values=[df.index, df["index"], df["total"], df["capita"]],
                line_width=0.75,
                fill_color="#1A1A2E",
                height=28,
                format=["", "", ",.0f", ",.2f"],
                prefix=["", "", "$", "$"],
                align=["center", "left", "left", "center", "center"],
            ),
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
        title_text=f"Los 30 municipios de México con mayores ingresos por remesas<br><b>per cápita</b> durante {PERIODO_TIEMPO}  de {año}",
        paper_bgcolor="#16213E",
        annotations=[
            dict(
                x=0.015,
                y=0.015,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(x=0.58, y=0.015, xanchor="center", yanchor="top", text=subtitulo),
            dict(
                x=1.01, y=0.015, xanchor="right", yanchor="top", text="🧁 @lapanquecita"
            ),
        ],
    )

    fig.write_image("./tabla_capita.png")


def plot_absolutos(año):
    """
    Esta función crea una tabla con los municiios que reciben mas remesas totales.

    Parameters
    ----------
    año : int
        El año que nos interesa analizar.

    """

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv")

    # Renombramos algunos estados a sus nombres más comunes.
    pop["Entidad"] = pop["Entidad"].replace(
        {
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz",
        }
    )

    # Creamos el índice y seleccionamos las columnas de nuestro interés.
    pop.index = pop["Municipio"] + ", " + pop["Entidad"]
    pop = pop[str(año)]

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv("./data/remesas_municipio.csv")

    # La estructura de este dataset es jerárquica.
    # Tenemos que hacer algunas modificaciones para que coincida con el dataset de población.
    df["Entidad"] = df["Municipio"].apply(fill_entidad)
    df["Entidad"] = df["Entidad"].replace("México", "Estado de México")
    df.ffill(inplace=True)
    df.index = df.apply(fill_cve, axis=1)

    # Quitamos los registros que no sean municipios.
    df = df[df["Municipio"].str.contains("⚬")]

    # Seleccionamos las columnas del año que nos interesa.
    cols = [col for col in df.columns if str(año) in col]

    # Filtramos el DataFrama con las columnas que nos interesan.
    df = df[cols]

    # Quitamos los decimales de las cifras.
    df["total"] = df.sum(axis=1) * 1000000

    # Calculamos el total para el subtítulo.
    subtitulo = f"Nacional: {df['total'].sum():,.0f} dólares"

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
    df = df.head(30)

    # Para el rank resetearemos el índice y le sumaremos 1, para que sea del 1 al 30 en vez del 0 al 29.
    df.reset_index(inplace=True)
    df.index += 1

    # Acortamos el nombre del municipio más largo de México.
    df["index"] = df["index"].replace(
        "Dolores Hidalgo Cuna de la Independencia Nal., Guanajuato",
        "Dolores Hidalgo, Guanajuato",
    )

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[50, 200, 110, 80],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    "<b>Municipio, Entidad</b>",
                    "<b>Remesas en dólares ↓</b>",
                    "<b>Per cápita</b>",
                ],
                font_color="#FFFFFF",
                line_width=0.75,
                fill_color="#f4511e",
                align="center",
                height=28,
            ),
            cells=dict(
                values=[df.index, df["index"], df["total"], df["capita"]],
                line_width=0.75,
                fill_color="#182c25",
                height=28,
                format=["", "", ",.0f", ",.2f"],
                prefix=["", "", "$", "$"],
                align=["center", "left", "left", "center", "center"],
            ),
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
        title_text=f"Los 30 municipios de México con mayores ingresos por remesas<br><b>totales</b> durante {PERIODO_TIEMPO} de {año}",
        paper_bgcolor="#1e453e",
        annotations=[
            dict(
                x=0.015,
                y=0.015,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: Banxico ({FECHA_FUENTE})",
            ),
            dict(
                x=0.58,
                y=0.015,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01, y=0.015, xanchor="right", yanchor="top", text="🧁 @lapanquecita"
            ),
        ],
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


def plot_tendencias(primer_año, ultimo_año):
    """
    Esta función crea una cuadrícula de sparklines con los municipios que han crecido más en ingresos por remesas.

    Parameters
    ----------
    primer_año : int
        El año inicial que se desea comparar.

    ultimo_año :  int
        El año final que se desea comparar.

    """

    # Cargamos el dataset de remesas por municipio.
    df = pd.read_csv("./data/remesas_municipio.csv")

    # La estructura de este dataset es jerárquica.
    # Tenemos que hacer algunas modificaciones para asignar la entdad a cada municipio.
    df["Entidad"] = df["Municipio"].apply(fill_entidad)
    df.ffill(inplace=True)
    df.index = df.apply(fill_cve, axis=1)

    # Quitamos los registros que no sean municipios.
    df = df[df["Municipio"].str.contains("⚬")]

    # Vamos a sumar los totales de remesas por año.
    # Para esto crearemos un ciclo del 2013 al 2024.
    for year in range(2013, 2025):
        cols = [col for col in df.columns if str(year) in col]
        df[str(year)] = df[cols].sum(axis=1)

    # Solo vamos a escoger las columnas que creamos.
    df = df.iloc[:, -12:]

    # Cambiamos las columnas de str a int.
    df.columns = [int(col) for col in df.columns]

    # Seleccionamos solo las columnas que nos interesan.
    df = df[[col for col in df.columns if col >= primer_año and col <= ultimo_año]]

    # Vamos a calcular el cambio porcentual entre el primer y último año.
    df["change"] = (df[ultimo_año] - df[primer_año]) / df[primer_año] * 100

    # Quitamos los municipsios con valores infinitos.
    df = df[df["change"] != np.inf]

    # Quitamos los municipios que hayan tenido menos de
    # 100 millones de dólares durante el último año.
    # Esto es con el propósito de encontrar los outliers más interesantes.
    df = df[df[ultimo_año] >= 100]

    # Ordenamos los valores usando el cambio porcentual de mayor a menor.
    df.sort_values("change", ascending=False, inplace=True)

    # Esta lista contendrá los textos de cada anotación.
    texto_anotaciones = list()

    # Fromateamos los subtítulos para cada cuadro en nuestra cuadrícula.
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
            temp_df.index = temp_df.index.map(lambda x: f"'{x-2000}")

            # Para nuestra gráfica de línea solo vamos a necesitar que el primer y último registro tengan un punto.
            sizes = [0 for _ in range(len(temp_df))]
            sizes[0] = 20
            sizes[-1] = 20

            # Vamos a extraer algunos valores para calcular el cambio porcentual y saber cual fue el valor máximo.
            primer_valor = temp_df.iloc[0]
            ultimo_valor = temp_df.iloc[-1]
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
            texto_anotaciones.append(f"<b>+{diff:,.1f}</b><br>+{change:,.0f}%")

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
                row=row + 1,
                col=column + 1,
            )

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
        nticks=15,
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
        nticks=8,
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
        title_text=f"Los 15 municipios de México con mayor crecimiento en ingresos por remesas ({primer_año} vs. {ultimo_año})",
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
    for (
        x,
        y,
        t,
    ) in zip(annotations_x, annotations_y, texto_anotaciones):
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
        text=f"Fuente: Banxico ({FECHA_FUENTE})",
    )

    fig.add_annotation(
        x=0.5,
        xanchor="center",
        xref="paper",
        y=1.04,
        yanchor="top",
        yref="paper",
        font_size=22,
        text=f"(solo se tomaron en cuenta los municipios con al menos 100 mdd por ingresos de remesas durante el {ultimo_año})",
    )

    fig.add_annotation(
        x=0.5,
        xanchor="center",
        xref="paper",
        y=-0.085,
        yanchor="bottom",
        yref="paper",
        text=f"El crecimiento nacional por ingresos de remesas del {primer_año} al {ultimo_año} es de <b>162.34%</b>",
    )

    fig.add_annotation(
        x=1.01,
        xanchor="right",
        xref="paper",
        y=-0.085,
        yanchor="bottom",
        yref="paper",
        text="🧁 @lapanquecita",
    )

    fig.write_image("./municipios_tendencia.png")


if __name__ == "__main__":
    plot_map(2023)
    plot_capita(2023)
    plot_absolutos(2023)
    plot_tendencias(2014, 2023)
