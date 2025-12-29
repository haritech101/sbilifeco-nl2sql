#/bin/sh

if [ -f ".env" ] ; then
    export $(cat .env | xargs)
fi

sed -i "s#\(const API_BASE_URL = \).*\$#\1\"$API_URL\"#gi" \
    editor-ui/scripts/home.js
npx serve -p $HTTP_PORT
