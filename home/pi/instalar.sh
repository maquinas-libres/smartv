sudo aptitude install -y lynx npm nodejs-legacy zenity transmission-gtk feh
sudo npm -g install peerflix
sudo pip install --upgrade youtube-dl

# archivos y programas a eliminar

[ ! "$USER" == "pi" ] && exit

rm -r ~/python_games
rm -r ~/Desktop
rm -r ~/Templates


# cosas de mas en raspbrian
sudo aptitude purge -y bluej vim dillo greenfoot idle idle3 sonic-pi supercollider squeak-vm vim wolfram-engine xpdf alacarte claws-mail minecraft-pi netsurf-gtk
sudo aptitude update
sudo aptitude upgrade

# paquetes para raspbrian
sudo aptitude install -y geary pidgin pidgin-otr libnotify-bin mate-icon-theme-faenza localepurge recode comix evince unclutter

# tema Mona en gtk-3.0
rm ~/.config/gtk-3.0/gtk.css
ln -s ~.themes/Mona\ 3.0/gtk-3.0/gtk.css ~/.config/gtk-3.0/gtk.css

