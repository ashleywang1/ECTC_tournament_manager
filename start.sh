#!/bin/sh

# Start Gunicorn processes
#echo Starting Gunicorn.
#exec gunicorn ectc_tm_server.wsgi:application \
#    --bind 0.0.0.0:8000 \
#    --workers 3

# Move into the code source directory
cd /usr/src/app

# Add tmdb user
useradd tmdb

# Clone the tournament_manager code
# git clone https://github.com/ashish-b10/tournament_manager.git
git clone https://github.com/ashleywang1/ECTC_tournament_manager.git
ln -s ECTC_tournament_manager/ectc_tm_server/db_settings_docker.py ECTC_tournament_manager/ectc_tm_server/.db_settings

pip3 install -r ECTC_tournament_manager/requirements.txt
pip3 install cryptography

# Set up the database
apk update
apk add postgresql
apk add postgresql-contrib
apk add curl
curl -o /usr/local/bin/gosu -sSL "https://github.com/tianon/gosu/releases/download/1.2/gosu-amd64"
chmod +x /usr/local/bin/gosu

mkdir tmdb_data
chmod 775 tmdb_data
sudo chown postgres tmdb_data
gosu postgres initdb tmdb_data

mkdir -p /run/postgresql
chmod g+s /run/postgresql
chown -R postgres /run/postgresql
gosu postgres pg_ctl -D tmdb_data/ -o "-c listen_addresses=''" -w start

# Create user and database
gosu postgres createuser tmdb -d
gosu postgres createdb tmdb

# edit the pg_hba.conf file
echo """# "local" is for Unix domain socket connections only
local   all             user                                    trust
# IPv4 local connections:
host    all             tmdb            127.0.0.1/32            trust
# IPv6 local connections:
host    all             tmdb            ::1/128                 trust""" >> tmdb_data/pg_hba.conf

# Restart the server
gosu postgres pg_ctl -D tmdb_data/ -o "-c listen_addresses=''" -w restart

# Python bindings
pip3 install psycopg2 pelican

pip3 install django-bootstrap-form

# Customize Postgres configuration file
# cp pg_hba.conf /usr/local/var/postgres/
cd ECTC_tournament_manager
python manage.py makemigrations tmdb && python manage.py migrate


# Restart to make changes apply
# brew services restart postgresql
# /etc/init.d/postgresql restart

# Set up PostgreSQL for Django
# python manage.py makemigrations tmdb && python manage.py migrate

# echo Starting ECTC_tournament_server
# python manage.py runserver
