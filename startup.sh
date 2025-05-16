#!/bin/bash
exec gunicorn --bind 0.0.0.0:15000 --reuse-port --reload main:app