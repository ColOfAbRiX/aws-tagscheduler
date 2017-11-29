#!/bin/bash
# Packs the code of the lambda function into what Terraform expects
pushd src > /dev/null 2>&1

#
# Getting PyTZ
#
pushd tagscheduler > /dev/null 2>&1
rm -rf pytz*
pip install -t . pytz
popd > /dev/null 2>&1

#
# Testing
#
echo -e "\nRunning Python tests"
python -m unittest discover
if [[ $? > 0 ]] ; then
    echo "Tests failed."
    rm -rf pytz*
    exit 1
fi

#
# Cleanups
#
echo "Cleanups"
find -type f -iname '*.pyc' -delete

#
# Pack it
#
echo "Packing"
pushd tagscheduler > /dev/null 2>&1

rm -f ../../tag-scheduler.zip 2> /dev/null
zip -qr ../../tag-scheduler.zip *

rm -rf pytz*
popd -2 > /dev/null 2>&1
# vim: ft=sh:ts=4:sw=4