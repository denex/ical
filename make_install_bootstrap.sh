#!/bin/bash

pushd bootstrap/
echo "MAKING BOOTSTRAP:"
make bootstrap
popd
echo "MOVING BOOTSTRAP:"
rm -rf static/bootstrap
mv -f bootstrap/bootstrap static/
