#!/usr/bin/env python
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

from __future__ import print_function

import boto3

from schedulable import *


def get_all_regions():
    """
    Returns a list of available AWS regions
    """
    return [x['RegionName'] for x in boto3.client('ec2').describe_regions()['Regions']]


def get_all_instances(region):
    """
    Returns a list of all the type of instances, and their instances, managed
    by the scheduler
    """
    ec2 = boto3.resource('ec2', region_name=region)
    rds = boto3.client('rds', region_name=region)

    return {
        'EC2': [EC2Schedulable(ec2, i) for i in ec2.instances.all()],
        'RDS': [RDSSchedulable(rds, i) for i in rds.describe_db_instances()['DBInstances']]
    }

# vim: ft=python:ts=4:sw=4