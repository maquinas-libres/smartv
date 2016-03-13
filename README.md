SmartTV en GNU (realmente inteligente)
======================================

Es un conjunto de aplacaciones para armar tu televisor realmente inteligente, o sea descarga y reproduce series, peliculas y musica de torrent.

![inicio](img/inicio.png)

Como usarlo
-----------

![elegi](img/elegi.png)

![presentacion](img/presentacion.png)

![mira](img/mira.png)

Novedades
---------

![feed](img/novedades.png)

Aplicaciones
------------

![feed](img/aplicaciones.png)

Buscar videos
-------------

![busca](img/buscar.png)
	
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
* **filesharing:** youtube-dl
* **mensajes:** notify-send	→ se necesita una ventana interior

extras
------

* **navegador:** epiphany
* **Clima:** conky
* **historietas:** comix
* **pdf:** evince
* **texto:** openoffice fbreader
* **chat:** pidgin
* **correo:** geary
* **privacidad:** tor
* **Noticias:** liferea

Juegos
------

* juntar por colores: gweld
* rompecabeza: pysol (es medio feo)
* aventura simple (mario 1 o bubble)
* tableto: gtkboard, xmahjongg

Quehaceres
----------

* musica esta mal como se generan los links
* bajar la pelicula basado en los subtitulos (X)
* normalizar el volumen
* si las peliculas tienen muestra, elegir la mas grande (X)
* opciones de zoom
* opciones de idioma (subtitulos o doblada forzada)
* quitar sombra a los subtitulos
* vblog con lista de sitios (host:)
* generar cache de las busquedas
* mirar torrent-mount para la musica
* poner pausa al X11 mientras reproduce una pelicula
  * o poner en pausa al pidgin
* mascota

mirar esto:

* teclado: http://ozzmaker.com/virtual-keyboard-for-the-raspberry-pi/?utm_source=feedly
* https://github.com/Ivshti/stremio-addons-client
* https://www.npmjs.com/package/multipass-torrent

