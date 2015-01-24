#!/bin/bash

set -ue

find . -name "*.pyc" -delete

coverage run --source='.' manage.py test
coverage html

open "http://localhost:8000/"
(cd htmlcov && python -m SimpleHTTPServer)
