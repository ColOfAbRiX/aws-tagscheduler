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

import pytz as tz
from schedulers import *
from schedulable import Schedulable
from datetime import datetime, time


class MockSchedulable(Schedulable):
    def __init__(self, start_time=None, stop_time=None, status="", tags=[]):
        self._start_time = start_time
        self._stop_time = stop_time
        self._status = status
        self._tags = tags

    def id(self):
        return "mock_schedulable"

    def start_time(self):
        return self._start_time

    def stop_time(self):
        return self._stop_time

    def status(self):
        return self._status

    def tags(self):
        return self._tags

    def start(self):
        return True

    def stop(self):
        return True


class MockScheduler(Scheduler):
    def __init__(self):
        super(self.__class__, self).__init__("", "", "")

    def __str__(self):
        return "MockScheduler"

    def type():
        return "mockscheduler"

    def check(self):
        return True


class SchedulerTest(unittest.TestCase):
    """
    Tests for concrete methods of Scheduler
    """

    """ now_utc() """

    def test_now_utc_is_utc(self):
        result = MockScheduler().now_utc()
        self.assertEqual(result.tzinfo, tz.utc)

    """ parse_timezone() """

    def test_parse_none_timezone(self):
        result = Scheduler.parse_timezone(None)
        self.assertEqual(result, tz.timezone("UTC"))

    def test_parse_empty_timezone(self):
        result = Scheduler.parse_timezone("UTC")
        self.assertEqual(result, tz.timezone("UTC"))

    def test_parse_test_timezone(self):
        result = Scheduler.parse_timezone("Canada-Yukon")
        self.assertEqual(result, tz.timezone("Canada/Yukon"))

    """ parse_time() """

    def test_parse_none_time(self):
        result = Scheduler.parse_time(None, None)
        self.assertIsNone(result)

    def test_parse_empty_time(self):
        result = Scheduler.parse_time("", None)
        self.assertIsNone(result)

    def test_parse_time(self):
        result = Scheduler.parse_time("1122", None)
        self.assertEqual(result, time(11, 22, tzinfo=tz.utc))

    def test_parse_time_is_utc(self):
        result = Scheduler.parse_time("1122", None)
        self.assertEqual(result.tzinfo, tz.utc)

    def test_parse_time_withtz(self):
        # UTC is 0 hour ahead of Yukon
        result = Scheduler.parse_time("1122", "Canada-Yukon")
        self.assertEqual(result, time(20, 22, tzinfo=tz.utc))

    """ parse_day() """

    def test_parse_none_day(self):
        result = Scheduler.parse_day(None)
        self.assertIsNone(result)

    def test_parse_empty_day(self):
        result = Scheduler.parse_day("")
        self.assertEqual(result, ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])

    def test_parse_all_day(self):
        result = Scheduler.parse_day("all")
        self.assertEqual(result, ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])

    def test_parse_weekdays_day(self):
        result = Scheduler.parse_day("weekdays")
        self.assertEqual(result, ['mon', 'tue', 'wed', 'thu', 'fri'])

    def test_parse_weekends_day(self):
        result = Scheduler.parse_day("weekends")
        self.assertEqual(result, ['sat', 'sun'])

    def test_parse_single_day(self):
        result = Scheduler.parse_day("mon")
        self.assertEqual(result, ['mon'])

    def test_parse_list_day(self):
        result = Scheduler.parse_day("tue.thu")
        self.assertEqual(result, ['tue', 'thu'])

    def test_parse_range_day(self):
        result = Scheduler.parse_day("tue-thu")
        # Not implemented

    def test_parse_reverserange_day(self):
        result = Scheduler.parse_day("thu-tue")
        # Not implemented


class DailySchedulerTest(unittest.TestCase):
    """
    Tests for DailyScheduler
    """
    def setUp(self):
        self.mock = MockSchedulable()
        self.type = DailyScheduler.type()
        self.all_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    """ Identifier """

    def test_type(self):
        self.assertEqual(DailyScheduler.type(), "daily")

    def test_string_empty_value(self):
        result = str(Scheduler.build(self.mock, self.type, "", "//"))
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "")

    """ Builder of the scheduler"""

    def test_build_none_value(self):
        result = Scheduler.build(self.mock, self.type, "", None)
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_empty_string_value(self):
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_random_string_value(self):
        result = Scheduler.build(self.mock, self.type, "", "asdfghj")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_empty_value_3fields(self):
        result = Scheduler.build(self.mock, self.type, "", "//")
        self.assertIsNotNone(result)
        self.assertIsNone(result.start_time)
        self.assertIsNone(result.stop_time)
        self.assertEqual(result.time_zone, "UTC")
        self.assertEqual(result.days_active, self.all_days)

    def test_build_empty_value_4fields(self):
        result = Scheduler.build(self.mock, self.type, "", "///")
        self.assertIsNotNone(result)
        self.assertIsNone(result.start_time)
        self.assertIsNone(result.stop_time)
        self.assertEqual(result.time_zone, "UTC")
        self.assertEqual(result.days_active, self.all_days)

    def test_build_toomany_value_fields(self):
        result = Scheduler.build(self.mock, self.type, "", "////")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_none_name(self):
        result = Scheduler.build(self.mock, self.type, None, "//")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "")

    def test_build_empy_name(self):
        result = Scheduler.build(self.mock, self.type, "", "//")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "")

    def test_build_empty_instance(self):
        with self.assertRaises(ValueError):
            Scheduler.build(None, DailyScheduler.type(), "", "//")

    """ Scheduler check """

    def test_check_outofday(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1122/2211/mon")
        scheduler._mock_now_time = datetime(2018, 2, 1, 12, 34, 56)  # It's a Thursday
        self.assertIsNone(scheduler.check())

    def test_check_singleday(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1300/1500/thu")
        scheduler._mock_now_time = datetime(2018, 2, 1, 14)
        self.assertEqual(scheduler.check(), "start")

    def test_check_listofdays(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1300/1500/wed.thu.fri")
        scheduler._mock_now_time = datetime(2018, 2, 1, 14)
        self.assertEqual(scheduler.check(), "start")

    def test_check_shortcutdays(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1300/1500/weekdays")
        scheduler._mock_now_time = datetime(2018, 2, 1, 14)
        self.assertEqual(scheduler.check(), "start")

    def test_nostarttime_before_stoptime(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "/1400")
        scheduler._mock_now_time = datetime(2018, 2, 1, 10)
        self.assertIsNone(scheduler.check())

    def test_nostarttime_after_stoptime(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "/1400")
        scheduler._mock_now_time = datetime(2018, 2, 1, 18)
        self.assertEqual(scheduler.check(), "stop")

    def test_nostoptime_before_starttime(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1400/")
        scheduler._mock_now_time = datetime(2018, 2, 1, 10)
        self.assertEqual(scheduler.check(), "start")

    def test_nostoptime_after_starttime(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1400/")
        scheduler._mock_now_time = datetime(2018, 2, 1, 18)
        self.assertIsNone(scheduler.check())

    def test_before_starttime(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1300/1500")
        scheduler._mock_now_time = datetime(2018, 2, 1, 10)
        self.assertIsNone(scheduler.check())

    def test_between_startstoptime(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1300/1500")
        scheduler._mock_now_time = datetime(2018, 2, 1, 14)
        self.assertEqual(scheduler.check(), "start")

    def test_after_stoptime(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1300/1500")
        scheduler._mock_now_time = datetime(2018, 2, 1, 18)
        self.assertEqual(scheduler.check(), "stop")

    def test_before_starttime_reversed(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1500/1300")
        scheduler._mock_now_time = datetime(2018, 2, 1, 10)
        self.assertIsNone(scheduler.check())

    def test_between_startstoptime_reversed(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1500/1300")
        scheduler._mock_now_time = datetime(2018, 2, 1, 14)
        self.assertEqual(scheduler.check(), "start")

    def test_after_stoptime_reversed(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1500/1300")
        scheduler._mock_now_time = datetime(2018, 2, 1, 18)
        self.assertEqual(scheduler.check(), "stop")

    def test_different_timezone(self):
        scheduler = Scheduler.build(MockSchedulable(), self.type, "", "1300/1500//Canada-Yukon")
        scheduler._mock_now_time = datetime(2018, 2, 1, 5)
        self.assertEqual(scheduler.check(), "start")


class TimerSchedulerTest(unittest.TestCase):
    """
    Tests for TimerScheduler
    """
    def setUp(self):
        self.mock = MockSchedulable()
        self.type = TimerScheduler.type()
        # Some useful times
        now = datetime.utcnow().replace(tzinfo=tz.utc)
        self.now_minus5 = now - timedelta(minutes = 5)
        self.now_minus15 = now - timedelta(minutes = 15)


    """ Identifier """

    def test_type(self):
        self.assertEqual(TimerScheduler.type(), "timer")

    """ Builder of the scheduler"""

    def test_build_none_value(self):
        result = Scheduler.build(self.mock, self.type, "", None)
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_empty_string_value(self):
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_random_string_value(self):
        result = Scheduler.build(self.mock, self.type, "", "asdfghj")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_empty_value_2fields(self):
        result = Scheduler.build(self.mock, self.type, "", "/")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_missing_value_fields(self):
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_toomany_value_fields(self):
        result = Scheduler.build(self.mock, self.type, "", "//")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    """ Scheduler check """

    def test_check_start_onrunningfor5_donothing(self):
        mock = MockSchedulable(status="running", start_time=self.now_minus5)
        result = Scheduler.build(mock, self.type, "", "start/10").check()
        self.assertIsNone(result)

    def test_check_start_onrunningfor15_donothing(self):
        mock = MockSchedulable(status="running", start_time=self.now_minus15)
        result = Scheduler.build(mock, self.type, "", "start/10").check()
        self.assertIsNone(result)

    def test_check_stop_onrunningfor5_donothing(self):
        mock = MockSchedulable(status="running", start_time=self.now_minus5)
        result = Scheduler.build(mock, self.type, "", "stop/10").check()
        self.assertIsNone(result)

    def test_check_stop_onrunningfor15_actionit(self):
        mock = MockSchedulable(status="running", start_time=self.now_minus15)
        result = Scheduler.build(mock, self.type, "", "stop/10").check()
        self.assertEqual(result, "stop")

    def test_check_start_onstoppedfor5_donothing(self):
        mock = MockSchedulable(status="stopped", stop_time=self.now_minus5)
        result = Scheduler.build(mock, self.type, "", "start/10").check()
        self.assertIsNone(result)

    def test_check_start_onstoppedfor15_actionit(self):
        mock = MockSchedulable(status="stopped", stop_time=self.now_minus15)
        result = Scheduler.build(mock, self.type, "", "start/10").check()
        self.assertEqual(result, "start")

    def test_check_stop_stoppedfor5_donothing(self):
        mock = MockSchedulable(status="stopped", stop_time=self.now_minus5)
        result = Scheduler.build(mock, self.type, "", "stop/10").check()
        self.assertIsNone(result)

    def test_check_stop_stoppedfor15_donothing(self):
        mock = MockSchedulable(status="stopped", stop_time=self.now_minus15)
        result = Scheduler.build(mock, self.type, "", "stop/10").check()
        self.assertIsNone(result)

    """ Missing times """

    def test_start_without_stoptime(self):
        mock = MockSchedulable(status="stopped")
        result = Scheduler.build(mock, self.type, "", "start/10").check()
        self.assertIsNone(result)

    def test_stop_without_starttime(self):
        mock = MockSchedulable(status="running")
        result = Scheduler.build(mock, self.type, "", "stop/10").check()
        self.assertIsNone(result)


class IgnoreSchedulerTest(unittest.TestCase):
    """
    Tests for IgnoreScheduler
    """
    def setUp(self):
        self.mock = MockSchedulable()
        self.type = IgnoreScheduler.type()

    """ Identifier """

    def test_type(self):
        self.assertEqual(IgnoreScheduler.type(), "ignore_all")

    """ Builder of the scheduler"""

    def test_build_none_value(self):
        result = Scheduler.build(self.mock, self.type, "", None)
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_empty_string_value(self):
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_random_string_valueandom_string_value(self):
        result = Scheduler.build(self.mock, self.type, "", "asdfghj")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    """ Scheduler check """

    def test_check(self):
        result = Scheduler.build(self.mock, self.type, "", "ignore").check()
        self.assertEqual(result, "ignore")


class FixedSchedulerTest(unittest.TestCase):
    """
    Tests for IgnoreScheduler
    """
    def setUp(self):
        self.mock = MockSchedulable()
        self.type = FixedScheduler.type()

    """ Identifier """

    def test_type(self):
        self.assertEqual(FixedScheduler.type(), "fixed")

    """ Builder of the scheduler"""

    def test_build_none_value(self):
        result = Scheduler.build(self.mock, self.type, "", None)
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_empty_string_value(self):
        result = Scheduler.build(self.mock, self.type, "", "")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    def test_build_random_string_value(self):
        result = Scheduler.build(self.mock, self.type, "", "asdfghj")
        self.assertIsNotNone(result)
        self.assertEqual(result.check(), "error")

    """ Scheduler check """

    def test_start(self):
        result = Scheduler.build(self.mock, self.type, "", "start").check()
        self.assertEqual(result, "start")

    def test_stop(self):
        result = Scheduler.build(self.mock, self.type, "", "stop").check()
        self.assertEqual(result, "stop")


if __name__ == '__main__':
    unittest.main()

# vim: ft=python:ts=4:sw=4