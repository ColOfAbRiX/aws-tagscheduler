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

from mocked_objects import *
from tagscheduler.tagscheduler import *


class ProcessInstanceTest(unittest.TestCase):

    def setUp(self):
        self.bis_mock_patch = patch('tagscheduler.tagscheduler.build_instance_schedulers')
        self.bis_mock = self.bis_mock_patch.start()

    def tearDown(self):
        self.bis_mock_patch.stop()

    def test_no_actions(self):
        with self.assertRaises(Exception):
            process_instance(None)

    def test_no_schedulers(self):
        self.bis_mock.return_value = []
        result = process_instance(MockSchedulable())
        self.assertIsNone(result)

    def test_scheduler_bad(self):
        self.bis_mock.return_value = []
        result = process_instance(MockSchedulable())
        self.assertIsNone(result)

    """ start action """

    def test_scheduler_start_onstarted(self):
        self.bis_mock.return_value = [MockScheduler(check_result="start")]
        result = process_instance(MockSchedulable(status="running"))
        self.assertIsNone(result)

    def test_scheduler_start_onstopped(self):
        self.bis_mock.return_value = [MockScheduler(check_result="start")]
        result = process_instance(MockSchedulable(status="stopped"))
        self.assertEqual(result, "start")

    """ stop action """

    def test_scheduler_stop_onstarted(self):
        self.bis_mock.return_value = [MockScheduler(check_result="stop")]
        result = process_instance(MockSchedulable(status="running"))
        self.assertEqual(result, "stop")

    def test_scheduler_stop_onstopped(self):
        self.bis_mock.return_value = [MockScheduler(check_result="stop")]
        result = process_instance(MockSchedulable(status="stopped"))
        self.assertIsNone(result)

    """ ignore action """

    def test_scheduler_ignore_onstarted(self):
        self.bis_mock.return_value = [MockScheduler(check_result="ignore")]
        result = process_instance(MockSchedulable(status="running"))
        self.assertIsNone(result)

    def test_scheduler_ignore_onstopped(self):
        self.bis_mock.return_value = [MockScheduler(check_result="ignore")]
        result = process_instance(MockSchedulable(status="stopped"))
        self.assertIsNone(result)

    def test_scheduler_ignore_suppresses(self):
        self.bis_mock.return_value = [
            MockScheduler(check_result="start"),
            MockScheduler(check_result="ignore"),
            MockScheduler(check_result="start")
        ]
        result = process_instance(MockSchedulable(status="stopped"))
        self.assertIsNone(result)

    """ error action """

    def test_scheduler_error_onstarted(self):
        self.bis_mock.return_value = [MockScheduler(check_result="error")]
        result = process_instance(MockSchedulable(status="running"))
        self.assertIsNone(result)

    def test_scheduler_error_onstopped(self):
        self.bis_mock.return_value = [MockScheduler(check_result="error")]
        result = process_instance(MockSchedulable(status="stopped"))
        self.assertIsNone(result)

    def test_scheduler_error_skipped(self):
        self.bis_mock.return_value = [
            MockScheduler(check_result="start"),
            MockScheduler(check_result="error"),
            MockScheduler(check_result="start")
        ]
        result = process_instance(MockSchedulable(status="stopped"))
        self.assertEqual(result, "start")

    """ no action """

    def test_scheduler_none_onstarted(self):
        self.bis_mock.return_value = [MockScheduler(check_result=None)]
        result = process_instance(MockSchedulable(status="running"))
        self.assertIsNone(result)

    def test_scheduler_none_onstopped(self):
        self.bis_mock.return_value = [MockScheduler(check_result=None)]
        result = process_instance(MockSchedulable(status="stopped"))
        self.assertIsNone(result)

    """ multiple actions """

    def test_scheduler_multiple_stop(self):
        self.bis_mock.return_value = [
            MockScheduler(check_result="stop"),
            MockScheduler(check_result="start"),
            MockScheduler(check_result="stop")
        ]
        result = process_instance(MockSchedulable(status="running"))
        self.assertEqual(result, "stop")

    def test_scheduler_multiple_start(self):
        self.bis_mock.return_value = [
            MockScheduler(check_result="start"),
            MockScheduler(check_result="stop"),
            MockScheduler(check_result="start")
        ]
        result = process_instance(MockSchedulable(status="stopped"))
        self.assertEqual(result, "start")


class BuildInstanceSchedulersTest(unittest.TestCase):

    def test_no_instance(self):
        with self.assertRaises(Exception):
            build_instance_schedulers(None)

    def test_no_tags(self):
        mock_ec2 = MockSchedulable()
        result = build_instance_schedulers(mock_ec2)
        self.assertListEqual(result, [])

    def test_bad_tag(self):
        schedulers = [{'Key': 'test_1', 'Value': 'value_1'}]
        mock_ec2 = MockSchedulable(tags=schedulers)
        result = build_instance_schedulers(mock_ec2)
        self.assertListEqual(result, [])

    def test_unknown_scheduler(self):
        schedulers = [{'Key': 'scheduler-unknown', 'Value': 'ignore'}]
        mock_ec2 = MockSchedulable(tags=schedulers)
        result = build_instance_schedulers(mock_ec2)
        self.assertListEqual(result, [])

    def test_one_scheduler(self):
        schedulers = [{'Key': 'scheduler-ignore_all', 'Value': 'ignore'}]
        mock_ec2 = MockSchedulable(tags=schedulers)
        result = build_instance_schedulers(mock_ec2)
        self.assertEqual(len(result), 1)

    def test_more_schedulers(self):
        schedulers = [
            {'Key': 'scheduler-ignore_all', 'Value': 'ignore'},
            {'Key': 'scheduler-ignore_all', 'Value': 'ignore'},
            {'Key': 'scheduler-ignore_all', 'Value': 'ignore'}
        ]
        mock_ec2 = MockSchedulable(tags=schedulers)
        result = build_instance_schedulers(mock_ec2)
        self.assertEqual(len(result), 3)

    def test_sorting(self):
        schedulers = [
            {'Key': 'scheduler-ignore_all', 'Value': 'ignore'},
            {'Key': 'scheduler-ignore_all-0', 'Value': 'ignore'},
            {'Key': 'scheduler-ignore_all-1', 'Value': 'ignore'},
            {'Key': 'scheduler-fixed', 'Value': 'start'},
            {'Key': 'scheduler-fixed-2', 'Value': 'start'}
        ]
        expected = [
            {'type': 'ignore_all', 'name': ''},
            {'type': 'fixed', 'name': ''},
            {'type': 'ignore_all', 'name': '0'},
            {'type': 'ignore_all', 'name': '1'},
            {'type': 'fixed', 'name': '2'}
        ]
        mock_ec2 = MockSchedulable(tags=schedulers)
        result = build_instance_schedulers(mock_ec2)
        result = [{'name': s.name, 'type': s.type()} for s in result]
        self.assertListEqual(result, expected)


class ExecuteActionsTest(unittest.TestCase):

    def setUp(self):
        self.empty_list = []

        self.one_instance_start = [(MockSchedulable(), "start")]
        self.one_instance_stop = [(MockSchedulable(), "stop")]
        self.one_instance_none = [(MockSchedulable(), None)]

        self.instances_mixed = [
            (MockSchedulable(), "start"),
            (MockSchedulable(), "stop"),
            (MockSchedulable(), "stop"),
            (MockSchedulable(), None),
            (MockSchedulable(), "start")
        ]

        self.schedulable_start_patch = patch.object(MockSchedulable, 'start', return_value=MockSchedulable())
        self.schedulable_start = self.schedulable_start_patch.start()

        self.schedulable_stop_patch = patch.object(MockSchedulable, 'stop', return_value=MockSchedulable())
        self.schedulable_stop = self.schedulable_stop_patch.start()

    def tearDown(self):
        self.schedulable_stop_patch.stop()
        self.schedulable_start_patch.stop()

    """ With an empty list """

    def test_empty_list(self):
        try:
            execute_actions(self.empty_list)
        except:
            self.fail()
        self.schedulable_start.assert_not_called()
        self.schedulable_stop.assert_not_called()

    """ With one instance """

    def test_nothing_on_single_instance(self):
        execute_actions(self.one_instance_none)
        self.schedulable_start.assert_not_called()
        self.schedulable_stop.assert_not_called()

    def test_start_single_instance(self):
        execute_actions(self.one_instance_start)
        self.schedulable_start.assert_called_once_with()
        self.schedulable_stop.assert_not_called()

    def test_stop_single_instance(self):
        execute_actions(self.one_instance_stop)
        self.schedulable_start.assert_not_called()
        self.schedulable_stop.assert_called_once_with()

    """ More than one instance and actions """

    def test_stop_single_mixed(self):
        execute_actions(self.instances_mixed)
        self.assertEquals(self.schedulable_start.call_count, 2)
        self.assertEquals(self.schedulable_stop.call_count, 2)


# vim: ft=python:ts=4:sw=4