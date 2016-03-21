# elimina directorios locales
rm -r ~/python_games
rm -r ~/Desktop
rm -r ~/Videos
rm -r ~/Pictures
rm -r ~/Music
rm -r ~/Public
rm -r ~/Templates

# crea los directorios locales
cd ~
mkdir Descargas Juegos Público Vídeos Documentos Imágenes Música

# cosas de mas en raspbrian
sudo aptitude purge -y bluej vim dillo greenfoot idle idle3 sonic-pi supercollider squeak-vm vim wolfram-engine xpdf alacarte claws-mail minecraft-pi netsurf-gtk
sudo aptitude update
sudo aptitude upgrade

# paquetes para raspbrian
sudo aptitude install -y geary pidgin pidgin-otr mate-icon-theme-faenza localepurge recode comix evince unclutter uget aria2 lynx npm nodejs-legacy zenity feh
sudo aptitude install -y
sudo npm -g install peerflix
sudo pip install --upgrade youtube-dl

# tema Mona en gtk-3.0
rm ~/.config/gtk-3.0/gtk.css
ln -s ~/.themes/Mona\ 3.0/gtk-3.0/gtk.css ~/.config/gtk-3.0/gtk.css
