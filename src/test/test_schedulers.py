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
sys.path.append(os.path.join(os.getcwd(), "tagscheduler"))
sys.stderr = open('/dev/null', 'w')
import unittest

from tagscheduler.schedulers import *
from tagscheduler.schedulable import *


class MockInstance(Schedulable):
    def id(self):
        return "abc"

    def start_time(self):
        return None

    def stop_time(self):
        return None

    def status(self):
        return ""

    def tags(self):
        return []

    def start(self):
        return True

    def stop(self):
        return True


class DailySchedulerTest(unittest.TestCase):
    """
    Tests for DailyScheduler
    """

    def setUp(self):
        self.mock = MockInstance()
        self.type = DailyScheduler.type()
        self.all_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    def test_type(self):
        self.assertEqual(DailyScheduler.type(), "daily")

    def test_string(self):
        # With empty values
        result = str(Scheduler.build(self.mock, self.type, "", "//"))
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "")

    def test_build_bad_value(self):
        # None value
        result = Scheduler.build(self.mock, self.type, "", None)
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

        # Empty string value
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

        # Random string value
        result = Scheduler.build(self.mock, self.type, "", "asdfghj")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

    def test_build_empty_fields(self):
        # Empty 3-fields in the value
        result = Scheduler.build(self.mock, self.type, "", "//")
        self.assertIsNotNone(result)
        self.assertIsNone(result.start_time)
        self.assertIsNone(result.stop_time)
        self.assertEqual(result.time_zone, "UTC")
        self.assertEqual(result.days_active, self.all_days)

        # Empty 4-fields in the value
        result = Scheduler.build(self.mock, self.type, "", "///")
        self.assertIsNotNone(result)
        self.assertIsNone(result.start_time)
        self.assertIsNone(result.stop_time)
        self.assertEqual(result.time_zone, "UTC")
        self.assertEqual(result.days_active, self.all_days)

    def test_build_bad_fields(self):
        # Not enough fields in the value
        result = Scheduler.build(self.mock, self.type, "", "/")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

        # Too many fields in the value
        result = Scheduler.build(self.mock, self.type, "", "////")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

    def test_build_empty_name(self):
        # None name
        result = Scheduler.build(self.mock, self.type, None, "//")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "")

        # Empty name
        result = Scheduler.build(self.mock, self.type, "", "//")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "")

    def test_build_empty_instance(self):
        # None value
        with self.assertRaises(ValueError):
            Scheduler.build(None, DailyScheduler.type(), "", "//")


class TimerSchedulerTest(unittest.TestCase):
    """
    Tests for TimerScheduler
    """
    def setUp(self):
        self.mock = MockInstance()
        self.type = TimerScheduler.type()

    def test_type(self):
        self.assertEqual(TimerScheduler.type(), "timer")

    def test_build_bad_value(self):
        # None value
        result = Scheduler.build(self.mock, self.type, "", None)
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

        # Empty string value
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

        # Random string value
        result = Scheduler.build(self.mock, self.type, "", "asdfghj")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

    def test_build_empty_fields(self):
        # Empty 2-fields in the value
        result = Scheduler.build(self.mock, self.type, "", "/")
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.action)
        self.assertIsNotNone(result.timer)

    def test_build_bad_fields(self):
        # Not enough fields in the value
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

        # Too many fields in the value
        result = Scheduler.build(self.mock, self.type, "", "//")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")


class IgnoreSchedulerTest(unittest.TestCase):
    """
    Tests for IgnoreScheduler
    """
    def setUp(self):
        self.mock = MockInstance()
        self.type = IgnoreScheduler.type()

    def test_type(self):
        self.assertEqual(IgnoreScheduler.type(), "ignore_all")

    def test_build_bad_value(self):
        # None value
        result = Scheduler.build(self.mock, self.type, "", None)
        self.assertIsNotNone(result)

        # Empty string value
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)

        # Random string value
        result = Scheduler.build(self.mock, self.type, "", "asdfghj")
        self.assertIsNotNone(result)

    def test_check(self):
        result = Scheduler.build(self.mock, self.type, "", "").check()
        self.assertEqual(result, "ignore")


class FixedSchedulerTest(unittest.TestCase):
    """
    Tests for IgnoreScheduler
    """
    def setUp(self):
        self.mock = MockInstance()
        self.type = FixedScheduler.type()

    def test_type(self):
        self.assertEqual(FixedScheduler.type(), "fixed")

    def test_build_bad_value(self):
        # None value
        result = Scheduler.build(self.mock, self.type, "", None)
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

        # Empty string value
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

        # Random string value
        result = Scheduler.build(self.mock, self.type, "", "asdfghj")
        self.assertIsNotNone(result)
        self.assertTrue(result._error)
        self.assertEqual(result.check(), "error")

    def test_start(self):
        result = Scheduler.build(self.mock, self.type, "", "start").check()
        self.assertEqual(result, "start")

    def test_stop(self):
        result = Scheduler.build(self.mock, self.type, "", "stop").check()
        self.assertEqual(result, "stop")


# vim: ft=python:ts=4:sw=4