#!/bin/sh
cd server

# First time tmdb startup
python3 manage.py makemigrations tmdb && python3 manage.py migrate

# Import Gdrive creds
python3 manage.py update_gdrive_creds -f keys.json

# Start the server
# /usr/bin/gunicorn ectc_tm_server.wsgi:application -w 2 -b :8000
LOGDIR=${HOME}/tournament_manager/logs/
mkdir -p ${LOGDIR}

## TODO(awang) figure out how to put each runworker in its own docker container
cd /data/web/server
python3 manage.py runworker & #> ${LOGDIR}/worker1.log 2>&1 &
python3 manage.py runworker & #> ${LOGDIR}/worker2.log 2>&1 &
python3 manage.py runworker & #> ${LOGDIR}/worker3.log 2>&1 &

exec /usr/bin/daphne -b 0.0.0.0 ectc_tm_server.asgi:channel_layer > ${LOGDIR}/daphne.log 2>&1
