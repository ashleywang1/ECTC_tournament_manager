#!/bin/sh

# First time tmdb startup
python3 manage.py makemigrations tmdb && python3 manage.py migrate

# Import Gdrive creds
python3 manage.py update_gdrive_creds -f keys.json

# Start the server
/usr/bin/gunicorn ectc_tm_server.wsgi:application -w 2 -b :8000
