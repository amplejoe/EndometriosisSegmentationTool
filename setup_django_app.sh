#!/bin/bash

###
# File: run_django_app.sh
# Created: Wednesday, 31st March 2021 6:05:18 pm
# Author: Andreas (amplejoe@gmail.com)
# -----
# Last Modified: Wednesday, 31st March 2021 6:43:32 pm
# Modified By: Andreas (amplejoe@gmail.com)
# -----
# Copyright (c) 2021 Klagenfurt University
#
###

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $SCRIPT_DIR/cfg.sh

# generate secret key
$PYTHON_INTERPRETER -c 'from django.core.management.utils import get_random_secret_key; print(f"SECRET_KEY = \"{get_random_secret_key()}\"")' > ./django_app/django_app/secret_settings.py
# migrate db
./django_app/make_migrations.sh
# superuser
# python manage.py createsuperuser

