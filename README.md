SmartTV en GNU (realmente inteligente)
======================================

Es un conjunto de aplacaciones para armar tu televisor realmente inteligente

![busca](img/inicio.png)

Como usarlo
-----------

![busca](img/buscar.png)
	
![elegi](img/elegi.png)

![mira](img/mira.png)

Novedades
---------

![feed](img/novedades.png)

Aplicaciones
------------

![feed](img/aplicaciones.png)

Busca peliculas en imdb y genera archivos `.desktop` en un carpeta al presionar sobre ellos se busca la pelicula en `torrent-search`.
Este se renueva cada X cantidad de tiempo.


Instalar en GNU
===============

Instalar dependencias. 
Copiar la carpeta `home/pi/bin` en la carpeta del usuario `~/bin`, de modo que sean ejecutables.
Tambien se los puede copiar en `/usr/local/bin`.


Instalar en raspberry
=====================

Generar una microsd de raspberian y luego compiar las carpetas `home`, iniciar la raspberry y correr `~/instalar.sh`

Que tiene
=========

* **splash:** fbi 
* **iconos:** mate-icon-theme-faenza
* **tema:** [moka](http://gnome-look.org/content/download.php?content=168447&id=1&tan=71798382)
* **subtitulo:** [subdl](https://github.com/akexakex/subdl)
* **reproductor:** omxplayer, mpv, mplayer
* **buscador:** torrent-search.sf.net	→ python-libxml2 python-httplib2
* **streaming:** * peerflix	
* **descarga:** transmission	→ grabar en videos una vez terminada la descarga
* **filesharing:** youtube-dl	→ omxplayer -b $(youtube-dl --max-quality 35 -g "$1")
* **mensajes:** notify-send	→ se necesita una ventana interior

novedades
---------

* liferea
* conky | para el clima en pantalla

navegador
---------

* epiphany
	
extras
------

###textos

* comix
* evince
* openoffice
* calibre?

###Juegos

* juntar por colores (brix, ..)
* rompecabeza
* aventura simple (mario 1 o bubble)
* tableto (damas, ajedres)

###chat

* pidgin

###mail

* geasy

###privacidad

* tor



Quehaceres
----------

* portada tipo información de la pelicula
* al generar el .desktop buscar el magnet
* tema para osd
* ventana cuando descarga
* placa o imagen para cuando esta descargando
* generar cache de las busquedas y subtitulos

mirar esto:

* https://github.com/Ivshti/stremio-addons-client
* https://www.npmjs.com/package/multipass-torrent
