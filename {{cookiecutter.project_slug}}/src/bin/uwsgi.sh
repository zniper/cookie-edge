#!/usr/bin/env bash

ENVDIR=~/.virtualenvs/{{cookiecutter.project_slug}}
DJANGODIR=`pwd`

# Activate the virtual environment
source $ENVDIR/bin/activate

uwsgi --stop /tmp/{{cookiecutter.project_slug}}-uwsgi.pid
uwsgi --ini $DJANGODIR/{{cookiecutter.project_slug}}/uwsgi.ini
