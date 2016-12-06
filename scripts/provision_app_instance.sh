#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# Install dependencies
apt-get update
apt-get -y install \
	python3-pip \
	libpq-dev \
	apache2 \
	apache2-dev \
	git

pip3 install --upgrade pip
pip3 install django psycopg2

# mod_wsgi
# Download
wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.5.9.tar.gz
tar xzf 4.5.9.tar.gz
# Build
cd mod_wsgi-4.5.9
./configure --with-python=/usr/bin/python3
make
make install
# Activate
cat <<EOF >/etc/apache2/mods-available/wsgi.load
LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
EOF
a2enmod wsgi
service apache2 restart

# Install the app
cd
git clone https://github.com/KTRosenberg/LSWA-Project-Team-1.git
cd LSWA-Project-Team-1

mkdir -p /var/www/site
cp -R web/appserver /var/www/site/appserver

mkdir -p /var/www/site/static
cd web/appserver
python3 manage.py collectstatic --noinput

cat <<EOF >/etc/apache2/sites-available/appserver.conf
WSGIScriptAlias / /var/www/site/appserver/appserver/wsgi.py
WSGIDaemonProcess appserver python-path=/var/www/site/appserver
WSGIProcessGroup appserver

<Directory /var/www/site/appserver/appserver>
  <Files wsgi.py>
    Require all granted
  </Files>
</Directory>

Alias /static/ /var/www/site/static/
<Directory /var/www/site/static>
  Require all granted
</Directory>
EOF

a2ensite appserver
service apache2 restart
