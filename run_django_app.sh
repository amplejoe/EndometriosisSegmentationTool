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

# run sever
$PYTHON_INTERPRETER ./django_app/manage.py runserver --noreload
