FROM alpine:3.7

# Initialize
RUN mkdir -p /data/web
WORKDIR /data/web
COPY requirements.txt /data/web/

# Setup
RUN apk update
RUN apk upgrade
RUN apk add --update python3 python3-dev postgresql-client postgresql-dev build-base gettext
RUN apk add --update git
# This gets cryptography module to install
RUN apk add --update gcc musl-dev python3-dev libffi-dev libressl-dev
# This gets Pillow to install
RUN apk add --update build-base py-pip jpeg-dev zlib-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Clean
RUN apk del -r python3-dev postgresql

# Prepare
COPY . /data/web/
RUN mkdir -p server/tmdb/static/admin
