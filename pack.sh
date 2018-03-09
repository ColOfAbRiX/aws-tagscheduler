#!/bin/bash

#
# MIT License
#
# Copyright (c) 2017 Fabrizio Colonna <colofabrix@tin.it>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

#
# Packs the code of the lambda function into what Terraform expects
#

pushd src > /dev/null 2>&1

#
# Testing (it assumes all dependencies are satisfied at OS level)
#
echo -e "\nRunning Python tests"
find -type f -iname '*.pyc' -delete
python -m unittest discover
if [[ $? > 0 ]] ; then
    echo "Tests failed."
    rm -rf pytz*
    exit 1
fi

#
# Getting PyTZ
#
pushd tagscheduler > /dev/null 2>&1
rm -rf pytz*
pip install -t . pytz
popd > /dev/null 2>&1

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