#!/bin/bash

cd /app

# static/js/config.js generate
rm -f static/js/config.js
sed "s/{KIBANA_ENDPOINT}/$KIBANA_ENDPOINT/" < static/js/config.js.template > static/js/config.js

# run flask app
python app.py
