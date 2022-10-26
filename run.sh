#!/bin/bash

if [ $# -eq 0 ]; then
  source ./ddenv/bin/activate && cd ./delosWhisperer && python3 manage.py runserver
else
  source ./ddenv/bin/activate && cd ./delosWhisperer && python3 manage.py collectstatic && python3 manage.py migrate && python3 manage.py runserver
fi
