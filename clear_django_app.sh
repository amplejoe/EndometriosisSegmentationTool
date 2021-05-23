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

# clear database
python ./django_app/manage.py flush
find ./django_app/media/videos ! -name 'readme.txt' -type f -exec rm -f {} +
find ./django_app/media/results ! -name 'readme.txt' -type f -exec rm -f {} +
