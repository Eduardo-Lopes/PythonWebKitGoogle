#!/bin/sh

CREDENTIAL=credentials.json

if [ ! -f "$CREDENTIAL" ]; then
    echo "You must create the credentials.json"
    echo "Follow https://developers.google.com/workspace/guides/create-credentials"
    echo "exiting..."
    exit
fi

FILE=pythonloader.so
if test -f "$FILE"; then
    echo "$FILE exists."
else
    echo "Building pythonloader.so ..."
    cd webkit2gtk-python-webextension-example
    make -s
    cd ..
    cp "webkit2gtk-python-webextension-example/${FILE}" "$FILE"
    echo "pythonloader.so builded"
fi

export LD_PRELOAD=libpython3.8.so
python3 SheetDemo.py $1