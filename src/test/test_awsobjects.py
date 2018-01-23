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

import os
import sys
sys.path.append(os.path.join(os.getcwd(), "../tagscheduler"))

import unittest
from mock import patch, Mock, MagicMock

from tagscheduler import *


class MockBoto3Objects:
    def describe_regions(self):
        """
        Mock of boto3.client('ec2').describe_regions()
        """
        return {
            "Regions": [
                {"RegionName": "ap-south-1"},
                {"RegionName": "eu-west-3"},
                {"RegionName": "eu-west-2"}
        ]}

    def describe_db_instances(self):
        """
        Mock of boto3.client('rds').describe_db_instances()
        """
        return {
            "DBInstances": [{}, {}]
        }

    def all(self):
        """
        Mock of boto3.resource('ec2').instances.all()
        """
        return [None, None]


class SchedulerTest(unittest.TestCase):

    def setUp(self):
        # Patch of boto3.client()
        self.boto3_client_patch = patch(
            'boto3.client', return_value=MockBoto3Objects()
        )
        self.boto3_client = self.boto3_client_patch.start()

        # Patch of boto3.resource()
        self.boto3_resource_patch = patch(
            'boto3.resource', return_value=Mock(instances=MockBoto3Objects())
        )
        self.boto3_resource = self.boto3_resource_patch.start()

        # Patch of EC2Schedulable
        self.ec2_schedulable_patch = patch.object(
            EC2Schedulable, '__init__', return_value=None
        )
        self.ec2_schedulable = self.ec2_schedulable_patch.start()

        # Patch of RDSSchedulable
        self.rds_schedulable_patch = patch.object(
            RDSSchedulable, '__init__', return_value=None
        )
        self.rds_schedulable = self.rds_schedulable_patch.start()

    def tearDown(self):
        self.ec2_schedulable_patch.stop()
        self.rds_schedulable_patch.stop()
        self.boto3_resource_patch.stop()
        self.boto3_client_patch.stop()

    """ get_all_regions() """

    def test_get_all_regions_not_none(self):
        result = get_all_regions()
        self.assertIsNotNone(result)

    def test_get_all_regions_is_list(self):
        result = get_all_regions()
        self.assertIsInstance(result, list)

    def test_get_all_regions_values(self):
        result = get_all_regions()
        self.assertListEqual(result, ['ap-south-1', 'eu-west-3', 'eu-west-2'])

    """ get_all_instances() """

    def test_get_all_instances_not_none(self, *args):
        result = get_all_instances("eu-west-2")
        self.assertIsNotNone(result)

    def test_get_all_instances_keys(self, *args):
        result = get_all_instances("eu-west-2")
        self.assertListEqual(result.keys(), ['EC2', 'RDS'])

    """ get_all_instances() - EC2Schedulable """

    def test_get_all_instances_ec2_counts(self, *args):
        result = get_all_instances("eu-west-2")
        self.assertTrue(len(result['EC2']), 2)

    def test_get_all_instances_ec2_objects(self, *args):
        result = get_all_instances("eu-west-2")
        self.assertIsInstance(result['EC2'][0], EC2Schedulable)

    """ get_all_instances() - RDSSchedulable """

    def test_get_all_instances_rds_counts(self, *args):
        result = get_all_instances("eu-west-2")
        self.assertTrue(len(result['RDS']), 2)

    def test_get_all_instances_rds_objects(self, *args):
        result = get_all_instances("eu-west-2")
        self.assertIsInstance(result['RDS'][0], RDSSchedulable)


if __name__ == '__main__':
    unittest.main()

# vim: ft=python:ts=4:sw=4