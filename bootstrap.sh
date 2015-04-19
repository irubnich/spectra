#!/usr/bin/env bash
apt-get update
apt-get -y upgrade

apt-get install -y python-pip sqlite3 libsqlite3-dev
pip install Flask
pip install Flask-SQLAlchemy
pip install IPython
