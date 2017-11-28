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
import unittest

sys.path.append(os.path.join(os.getcwd(), "tagscheduler"))
from tagscheduler.schedulers import *

class StartStopSchedulerTest(unittest.TestCase):
    """
    Tests for StartStopScheduler
    """

    def setUp(self):
        self.scheduler = Scheduler.build(StartStopScheduler.type(), None)

    def test_build(self):
        self.assertEqual(isinstance(self.scheduler, StartStopScheduler), True)

    def test_wrongTag(self):
        # None value
        self.assertEqual(self.scheduler.check(None), "error")

        # Empty string
        self.assertEqual(self.scheduler.check(""), "error")

    def test_emptyTag(self):
        # Empty fields
        self.assertEqual(self.scheduler.check("//"), None)
        self.assertEqual(self.scheduler.check("///"), None)

#     def test_startTime(self):
#         pass

#     def test_stopTime(self):
#         pass

#     def test_startStopTime(self):
#         pass

#     def test_daysShortcut(self):
#         pass

#     def test_startDay(self):
#         pass

#     def test_timezone(self):
#         pass


class TimerSchedulerTest(unittest.TestCase):
    """
    Tests for TimerScheduler
    """

    def setUp(self):
        self.scheduler = Scheduler.build(TimerScheduler.type(), None)

    def test_build(self):
        self.assertEqual(isinstance(self.scheduler, TimerScheduler), True)

    def test_wrongTag(self):
        # None value
        self.assertEqual(self.scheduler.check(None), "error")

        # Empty string
        self.assertEqual(self.scheduler.check(""), "error")

        # Empty fields
        self.assertEqual(self.scheduler.check("/"), "error")

#     def test_startTime(self):
#         pass

#     def test_stopTime(self):
#         pass


class IgnoreSchedulerTest(unittest.TestCase):
    """
    Tests for IgnoreScheduler
    """

    def setUp(self):
        self.scheduler = Scheduler.build(IgnoreScheduler.type(), None)

    def test_build(self):
        self.assertEqual(isinstance(self.scheduler, IgnoreScheduler), True)

    def test_empty(self):
        # None value
        self.assertEqual(self.scheduler.check(None), "ignore")

        # Empty string
        self.assertEqual(self.scheduler.check(""), "ignore")

    def test_ignore(self):
        # Random value
        self.assertEqual(self.scheduler.check("wasd"), "ignore")


# vim: ft=python:ts=4:sw=4