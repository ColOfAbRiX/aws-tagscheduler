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

import sys
import traceback
import pytz as tz
import schedulable

from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta, time


class Scheduler(object):
    """
    A base type for any scheduler
    """
    __metaclass__ = ABCMeta

    def __init__(self, instance):
        self._instance = instance
        self._mock_now_time = None

    @staticmethod
    def build(sched_type, instance):
        if sched_type.lower() == DailyScheduler.type():
            return DailyScheduler(instance)
        elif sched_type.lower() == TimerScheduler.type():
            return TimerScheduler(instance)
        elif sched_type.lower() == IgnoreScheduler.type():
            return IgnoreScheduler(instance)
        return None

    @abstractmethod
    def type():
        """ A string that identifies the scheduler """
        raise NotImplementedError()

    @abstractmethod
    def check(self, tag_value):
        """ Checks what a scheduler would do on the instance given the tag """
        raise NotImplementedError()

    def now_utc(self):
        """ Current or mock time in UTC """
        if self._mock_now_time is not None:
            return self._mock_now_time
        return datetime.now().utcnow()

    @staticmethod
    def parse_timezone(timezone):
        """ Parses a string Time Zone """
        if timezone is None or timezone == "":
            timezone = "UTC"

        return tz.timezone(
            timezone.strip().replace('-', '/')
        )

    @staticmethod
    def parse_time(str_time, timezone):
        """ Parses a string time """
        if str_time is None:
            return None
        str_time = str_time.strip()
        if str_time == "":
            return None

        # Parsing
        time = datetime.strptime(str_time, '%H%M')

        # Timezone
        timezone = Scheduler.parse_timezone(timezone)
        if timezone is not None:
            time = timezone.localize(time, is_dst=None)
            time = time.astimezone(tz.utc)

        # Only return time
        return time.time()

    @staticmethod
    def parse_day(days):
        """ Parses a string day of the week into a list """
        if days is None:
            return None
        days = days.strip().lower()
        if days == "":
            days = "all"

        if days == "weekdays":
            return ['mon', 'tue', 'wed', 'thu', 'fri']
        elif days == "weekends":
            return ['sat', 'sun']
        elif days == "all":
            return ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

        return days.split(".")


class TimerScheduler(Scheduler):
    """
    Find the appropriate action for the scheduler type "timer".

    The format of the tag is: "<action>/<time_span>"
     - "action" is "start" to start the instance or "stop" to stop the instance
        after time_span minutes have passed
     - "time_span" is a time duration in minutes, like 60 to indicate an hour
    """
    @staticmethod
    def type():
        return "timer"

    def check(self, tag_value):
        # Protection in case of None value
        if tag_value is None or tag_value.strip() == "":
            return "error"

        now_time = self.now_utc().time()
        tag_split = tag_value.split("/")

        # Check fields
        if len(tag_split) != 2:
            return "error"

        # Interpreting tag
        try:
            action = tag_split[0].lower()
            max_duration = timedelta(minutes=int(tag_split[1]))
        except Exception as e:
            return "error"

        # Instance up/down time
        if self._instance.status() == 'running':
            instance_time = self._instance.start_time()
        elif self._instance.status() == 'stopped':
            instance_time = self._instance.stop_time()
        else:
            return None

        # Cases when the time is not defined
        if instance_time is None:
            return None

        # If the instance must be started or stopped
        if (now_time - instance_time) > max_duration:
            return action

        return None


class DailyScheduler(Scheduler):
    """
    Find the appropriate action for the scheduler type "daily"

    The format of the tag is: "<start_time>/<stop_time>[/<week_days>[/<timezone>]]"
     - "start_time" is the time at which the instance must start, in the format
        HHMM (24h format), like 0730. If omitted the instance will not be started
        but it will keep the instance as it is.
     - "stop_time" is the time at which the instance must stop, in the format
        HHMM (24h format), like 1800; If omitted the instance will not be stopped
        but it will keep the instance as it is.
     - "week_days" is a list of 3 letters names of the week separated by a dot
       like "mon.wed.sat". Also valid are "all" for all the days of the week,
       "weekdays" for days from Monday to Friday and "weekends" for just Saturday
       and Sunday.
     - "timezone" is the time zone in 3 letter format, like EST or GMT. If not
       specified, the default is UTC
    """
    @staticmethod
    def type():
        return "daily"

    @staticmethod
    def action(now_time, start_time, stop_time):
        # No time range specified (weird...)
        if start_time is None and stop_time is None:
            return None

        # No start time
        if start_time is None:
            if now_time >= stop_time:
                return "stop"
            return None

        # No stop time
        if stop_time is None:
            if now_time < start_time:
                return "start"
            return None

        # Start and stop time defined
        if start_time < stop_time:
            if now_time >= start_time and now_time < stop_time:
                return "start"
            elif now_time >= stop_time:
                return "stop"
        else:
            if now_time >= stop_time and now_time < start_time:
                return "stop"
            elif now_time >= start_time:
                return "start"

        # Something else
        return None

    def check(self, tag_value):
        # Protection in case of None value
        if tag_value is None:
            return "error"

        # Some useful info
        now_time = self.now_utc().time()
        now_weekday = datetime.today().strftime("%a").lower()

        # Extract the parameters
        tag_split = tag_value.split("/")

        # Check fields
        if len(tag_split) < 3:
            return "error"

        try:
            # Time zone
            time_zone = tag_split[3] if len(tag_split) > 3 else "UTC"

            # Time the instance has to start
            start_time = Scheduler.parse_time(tag_split[0], time_zone)

            # Time the instance has to stop
            stop_time = Scheduler.parse_time(tag_split[1], time_zone)

            # Parsing day
            days_active = tag_split[2] if len(tag_split) else "all"
            days_active = Scheduler.parse_day(days_active)

        except Exception as e:
            print("-" * 80)
            traceback.print_exc()
            print("-" * 80)
            return "error"

        # Check day of the week
        is_active_day = False
        for d in days_active:
            if d.lower() == now_weekday:
                is_active_day = True
        if not is_active_day:
            return None

        return DailyScheduler.action(now_time, start_time, stop_time)


class IgnoreScheduler(Scheduler):
    """
    This scheduler always returns "ignore"
    """
    @staticmethod
    def type():
        return "ignore_all"

    def check(self, tag_value):
        return "ignore"

# vim: ft=python:ts=4:sw=4