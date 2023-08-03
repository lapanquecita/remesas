# Ingresos por remesas en México

Este repositorio incluye varios datasets y scripts para analizar los ingreos por remesas en México desde el año 2013 hasta la primera mitad del 2023.

Las remesas han ido en aumento, siendo los últimos meses máximos históricos. En este repositorio observaremos de donde vienen y a donde llegan estas remesas.

![Imagen 1](./imgs/remesas_mensuales.png)

## Remesas por país de origen

México recibe remesas de casi todos los países del mundo, sin embargo EE. UU. es el que más aporta, con el 96.03% del total de estas.

En la siguiente gráfica de barras se muestran los 30 países que más envían remesas hacia México. Se tuvo que usar una escala logarítmica para poder hacer una mejor comparación, dada la gran diferencia de cifras.

![Imagen 2](./imgs/remesas_pais_top.png)

Del otro lado tenemos a los 30 países que menos remesas aportan. En esta gráfica no se muestran porcentajes ya que todos se aproximan al 0%.

![Imagen 3](./imgs/remesas_pais_bottom.png)

Por último, tenemos un mapa Choropleth con la distribución espacial. Se puede apreciar que la mayoría de las remesas provienen de América y Europa occidental. También se se hizo uso de una escala logarítmica para poder distribuir mejor las cifras.

![Imagen 4](./imgs/mapa_paises.png)

## Remesas provenientes de EE. UU.

Como lo fue mencionado anteriormente, durante la primera mitad del 2023 EE. UU. aportó el 96.03% del total de las remesas hacia México.

Los 10 estados de EE. UU. que aportaron más remesas fueron:

| Estado     |         Total |
|:-----------|--------------:|
| California | 9,884,000,504 |
| Texas      | 4,366,724,619 |
| Minnesota  | 1,962,610,204 |
| Arizona    | 1,057,911,811 |
| Georgia    |   968,239,310 |
| Illinois   |   869,591,832 |
| Florida    |   668,745,790 |
| Nueva York |   628,633,897 |
| Colorado   |   590,558,795 |
| Washington |   575,872,330 |

Aquí tenemos el problema que la mayoría de estos estados también son los que tienen la mayor población de mexaicanos. Debemos ajustar estas cifras para tener un mejor punto de comparación.

*Nota: Es importante recordar que no todos los mexicanos que viven en EE. UU. mandan dinero a México. No pude encontrar información exacta de cuantos migrantes mexicanos viven en EE. UU., así que utilicé la información más cercana dispoible.*

Ahora bien, aquí esta la tabla de los 10 estados que más enviaron remesas a México ajustado con la población de mexicanos:

| Estado           |         Total |  Per cápita |
|:-----------------|--------------:|---------:|
| Minnesota        | 1,962,610,204 |    9,814 |
| Vermont          |    38,906,565 |    9,664 |
| Dakota Del Norte |   113,982,003 |    5,413 |
| Maine            |    42,111,175 |    5,154 |
| Puerto Rico      |    31,113,334 |    5,133 |
| Luisiana         |   249,192,082 |    3,623 |
| Washington, D.C. |    30,712,093 |    2,681 |
| Hawaii           |   122,466,877 |    2,333 |
| Ohio             |   473,955,252 |    2,231 |
| West Virginia    |    23,618,133 |    2,166 |

En el siguiente mapa Choropleth se puede observar la distribución completa. También se utilizó una escala logarítmica dada la diferencia entre los primeros valores.

![Imagen 5](./imgs/mapa_usa.png)

## Ingresos por municipio

Ya sabemos de donde vienen las remesas, ahora falta saber a donde llegan. Primero vamos a revisar las cifras absolutas. En la siguiente tabla se muestran los 30 municipios que han recibido el mayor número de remesas durante la primera mitad del 2023:

![Imagen 6](./imgs/tabla_absolutos.png)

La mayoría de estos municipios coinciden con las ciudades más grandes del país. Debemos ajustar estas cifras con la población de cada municipio para conocer su impacto económico.

![Imagen 7](./imgs/tabla_capita.png)

Ahora sabemos que en Chiapas, Michoacán, Oaxaca, Puebla y Zacatecas es donde las remesas tienen mayor impacto económico.


