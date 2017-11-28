#!/bin/bash
# Packs the code of the lambda function into what Terraform expects

rm -f tag-scheduler.zip 2> /dev/null

pushd src > /dev/null 2>&1

#
# Getting PyTZ
#
pushd tagscheduler > /dev/null 2>&1
echo "Updating PyTZ"
rm -rf pytz
wget --quiet -O pytz.zip https://pypi.python.org/packages/60/88/d3152c234da4b2a1f7a989f89609ea488225eaea015bc16fbde2b3fdfefa/pytz-2017.3.zip
unzip -q pytz.zip
mv "$(find -type d -name 'pytz')" .
rm -rf pytz.zip pytz-*

#
# Testing
#
echo "Running Python tests"
python -m unittest discover
if [[ $? > 0 ]] ; then
    echo "Tests failed."
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
pushd tagscheduler > /dev/null 2>&1

echo "Packing"
zip -q ../../tag-scheduler.zip *

popd -2 > /dev/null 2>&1

# vim: ft=sh:ts=4:sw=4