#!/bin/sh


# edit the pg_hba.conf file
echo """# "local" is for Unix domain socket connections only
local   all             user                                    trust
# IPv4 local connections:
host    all             tmdb            127.0.0.1/32            trust
# IPv6 local connections:
host    all             tmdb            ::1/128                 trust""" >> tmdb_data/pg_hba.conf

# Restart the server
gosu postgres pg_ctl -D tmdb_data/ -o "-c listen_addresses=''" -w restart

# Customize Postgres configuration file
# cp pg_hba.conf /usr/local/var/postgres/
cd ECTC_tournament_manager
python manage.py makemigrations tmdb && python manage.py migrate

# Start the Server
echo Starting ECTC_tournament_server
#python manage.py runserver 0.0.0.0:8000
#echo Starting Gunicorn.
pip3 install gunicorn

gunicorn ectc_tm_server.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
