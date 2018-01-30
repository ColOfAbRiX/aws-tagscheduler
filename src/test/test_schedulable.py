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

import unittest
from mock import patch

import pytz as tz
from mocked_objects import *
from datetime import datetime, time
from tagscheduler.schedulable import *


class EC2SchedulableTest(unittest.TestCase):

    """ Constructor """

    def test_constructor_client_none(self):
        with self.assertRaises(ValueError):
            result = EC2Schedulable(None, "")

    def test_constructor_instance_none(self):
        with self.assertRaises(ValueError):
            result = EC2Schedulable("", None)

    def test_constructor_not_none(self):
        mock_ec2 = MockEC2Instance()
        result = EC2Schedulable(mock_ec2, mock_ec2)
        self.assertIsNotNone(result)

    """ Various information """

    def test_instance_id(self):
        mock_ec2 = MockEC2Instance(instance_id="ABC")
        result = EC2Schedulable(mock_ec2, mock_ec2)
        self.assertEquals(result.id(), "ABC")

    def test_status_running(self):
        mock_ec2 = MockEC2Instance(status="Running")        # It also checks lowercase conversion
        result = EC2Schedulable(mock_ec2, mock_ec2)
        self.assertEquals(result.status(), "running")

    def test_status_stopped(self):
        mock_ec2 = MockEC2Instance(status="Stopped")        # It also checks lowercase conversion
        result = EC2Schedulable(mock_ec2, mock_ec2)
        self.assertEquals(result.status(), "stopped")

    def test_tags_empty(self):
        mock_ec2 = MockEC2Instance()
        result = EC2Schedulable(mock_ec2, mock_ec2)
        self.assertListEqual(result.tags(), [])

    def test_tags(self):
        mock_ec2 = MockEC2Instance(tags={'test_1': 'value_1', 'test_2': 'value_2'})
        result = EC2Schedulable(mock_ec2, mock_ec2)
        self.assertListEqual(result.tags(), [{
            'Key': 'test_1',
            'Value': 'value_1'
        }, {
            'Key': 'test_2',
            'Value': 'value_2'
        }])

    """ start_time() and stop_time() """

    def test_start_time_on_running(self):
        mock_ec2 = MockEC2Instance(
            status="running",
            launch_time="2018-05-04 03:02:01"
        )
        result = EC2Schedulable(mock_ec2, mock_ec2).start_time()
        self.assertEquals(result, datetime(2018, 5, 4, 3, 2, 1, tzinfo=tz.utc))

    def test_start_time_on_stopped(self):
        mock_ec2 = MockEC2Instance(
            status="stopped",
            launch_time="2018-05-04 03:02:01"
        )
        result = EC2Schedulable(mock_ec2, mock_ec2).start_time()
        self.assertIsNone(result)

    def test_start_time_is_utc(self):
        mock_ec2 = MockEC2Instance(
            status="running",
            launch_time="2018-05-04 03:02:01"
        )
        result = EC2Schedulable(mock_ec2, mock_ec2).start_time()
        self.assertEqual(result.tzinfo, tz.utc)

    def test_stop_time_on_running(self):
        mock_ec2 = MockEC2Instance(
            status="running",
            state_transition_reason=""
        )
        result = EC2Schedulable(mock_ec2, mock_ec2).stop_time()
        self.assertIsNone(result)

    def test_stop_time_on_stopped(self):
        mock_ec2 = MockEC2Instance(
            status="stopped",
            state_transition_reason="User initiated (2018-05-04 03:02:01 GMT)"
        )
        result = EC2Schedulable(mock_ec2, mock_ec2).stop_time()
        self.assertEquals(result, datetime(2018, 5, 4, 3, 2, 1, tzinfo=tz.utc))

    def test_stop_time_is_utc(self):
        mock_ec2 = MockEC2Instance(
            status="stopped",
            state_transition_reason="User initiated (2018-05-04 03:02:01 GMT)"
        )
        result = EC2Schedulable(mock_ec2, mock_ec2).stop_time()
        self.assertEqual(result.tzinfo, tz.utc)

    """ start() and stop () """

    def test_start(self):
        mock_ec2 = MockEC2Instance()
        result = EC2Schedulable(mock_ec2, mock_ec2).start()
        self.assertEquals(result, True)

    def test_stop(self):
        mock_ec2 = MockEC2Instance()
        result = EC2Schedulable(mock_ec2, mock_ec2).start()
        self.assertEquals(result, True)


class RDSSchedulableTest(unittest.TestCase):

    """ Constructor """

    def test_constructor_client_none(self):
        with self.assertRaises(ValueError):
            result = RDSSchedulable(None, "")

    def test_constructor_instance_none(self):
        with self.assertRaises(ValueError):
            result = RDSSchedulable("", None)

    def test_constructor_not_none(self):
        mock_rds = MockRDSInstance()
        result = RDSSchedulable(mock_rds, mock_rds)
        self.assertIsNotNone(result)

    """ Various information """

    def test_instance_id(self):
        mock_rds = MockRDSInstance(db_resource_id="ABC")
        result = RDSSchedulable(mock_rds, mock_rds)
        self.assertEquals(result.id(), "ABC")

    def test_status_running(self):
        mock_rds = MockRDSInstance(db_instance_status="Available")      # It also checks lowercase conversion
        result = RDSSchedulable(mock_rds, mock_rds)
        self.assertEquals(result.status(), "running")

    def test_status_stopped(self):
        mock_rds = MockRDSInstance(db_instance_status="Stopped")        # It also checks lowercase conversion
        result = RDSSchedulable(mock_rds, mock_rds)
        self.assertEquals(result.status(), "stopped")

    def test_tags_empty(self):
        mock_rds = MockRDSInstance()
        result = RDSSchedulable(mock_rds, mock_rds)
        self.assertListEqual(result.tags(), [])

    def test_tags(self):
        mock_rds = MockRDSInstance(tags={'test_1': 'value_1', 'test_2': 'value_2'})
        result = RDSSchedulable(mock_rds, mock_rds)
        self.assertListEqual(result.tags(), [{
            'Key': 'test_1',
            'Value': 'value_1'
        }, {
            'Key': 'test_2',
            'Value': 'value_2'
        }])

    """ start_time() and stop_time() """

    def test_start_time_is_none(self):
        mock_rds = MockRDSInstance(db_instance_status="running",)
        result = RDSSchedulable(mock_rds, mock_rds).start_time()
        self.assertIsNone(result)

    def test_start_time_is_none(self):
        mock_rds = MockRDSInstance(db_instance_status="running",)
        result = RDSSchedulable(mock_rds, mock_rds).stop_time()
        self.assertIsNone(result)

    """ start() and stop () """

    def test_start(self):
        mock_rds = MockRDSInstance()
        result = RDSSchedulable(mock_rds, mock_rds).start()
        self.assertEquals(result, True)

    def test_stop(self):
        mock_rds = MockRDSInstance()
        result = RDSSchedulable(mock_rds, mock_rds).start()
        self.assertEquals(result, True)


# vim: ft=python:ts=4:sw=4