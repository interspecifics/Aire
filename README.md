![header](https://raw.githubusercontent.com/interspecifics/Aire/master/aire.png?raw=true)

# AIRE 15.0 (2018)
# Interspecifics

Espacios: Casa del Lago [2016]. Museo Universitario Arte Contemporáneo [2018].

Aire es una pieza sonora generativa inspirada en la complejidad y variación de la contaminación atmosférica en una de las ciudades más contaminadas del mundo, la Ciudad de México. Partimos de un trabajo de investigación que se encarga de entender la forma en la que opera el sistema de monitoreo ambiental de la CDMX y utiliza un software escrito en Python para acceder a los valores que arrojan los sensores ambientales ubicados en las estaciones de Ecobici. Los datos recibidos: dióxido de azufre, monóxido de carbono, óxido de nitrógeno, dióxido de nitrógeno, monóxido de nitrógeno, ozono y partículas por millar, son distribuidos por zonas y analizados en un escala de niveles de saturación para con su flujo dar carácter y animar un ensamble de sintetizadores virtuales programados en Supercollider.  En la pieza, cada uno de los contaminantes tiene una identidad sonora propia y la fluctuación de la información modula todas sus características. Los patrones más relevantes y particulares que arroja el sistema detonan y apagan eventos de sonido conforme suceden y crean la estructura de la composición sobre la marcha. Además, el valor de velocidad y dirección del viento sirve como eje para controlar la lógica de espacialización de los instrumentos en un sistema de 15 canales organizado bajo una lógica cartesiana. Esta pieza forma parte de una serie de investigaciones sobre la performatividad de distintos fenómenos físicos y la capacidad del sonido para crear experiencias multimodales de los mismos.


Desarrollo 

Software para captura de datos escrito es Python 

Lógica de composición escrita en supercollider 

Sintesis digital escritos en supercollider 

![the system](https://github.com/interspecifics/Aire/blob/master/soft.png?raw=true)


#Librerias:

1 - sudo pip install request

2 - sudo pip install bs4

3 - sudo pip install pygame

4 - sudo pip install oscpy


# mini(2020.05):

1 - Actualizar rutas de archivos de datos   (21,22)

2 - Actualizar host osc                     (24,25)

3 - Ejecutar con aire_mini.py en la terminal


#Activar:

1 - Correr primero el archivo airetodo.sc en supercollider

2 - sudo python airstreamPromedios.py en la terminal 

![the system](https://raw.githubusercontent.com/interspecifics/Aire/master/run.png?raw=true)


