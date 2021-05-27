#!/bin/bash

###
# File: make_migrations.sh
# Created: Wednesday, 31st March 2021 6:43:55 pm
# Author: Andreas (amplejoe@gmail.com)
# -----
# Last Modified: Wednesday, 31st March 2021 6:44:00 pm
# Modified By: Andreas (amplejoe@gmail.com)
# -----
# Copyright (c) 2021 Klagenfurt University
#
###

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $SCRIPT_DIR/../cfg.sh

# migrate db
$PYTHON_INTERPRETER ./django_app/manage.py makemigrations
$PYTHON_INTERPRETER ./django_app/manage.py migrate