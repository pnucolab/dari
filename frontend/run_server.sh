#!/bin/bash

echo "Running frontend server..."
if [[ $DEBUG == "True" ]]; then
    npm run dev -- --host --port 3000
else
    export NODE_ENV=production
    node build
fi