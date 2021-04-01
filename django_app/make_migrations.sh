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

# migrate db
python ./django_app/manage.py makemigrations
python ./django_app/manage.py migrate