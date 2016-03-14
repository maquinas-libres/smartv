sudo aptitude install -y lynx npm nodejs-legacy zenity transmission-gtk feh recode
sudo npm -g install peerflix
sudo pip install --upgrade youtube-dl

cd /tmp/
wget https://github.com/maquinas-libres/smartv/archive/master.zip
unzip master.zip
cd smartv-master

sudo cp -r usr/local/* /usr/local
