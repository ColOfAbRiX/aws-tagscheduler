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

    def __init__(self, instance, name, value):
        if instance is None:
            raise ValueError

        self._instance = instance
        self.name = name.strip() if name is not None else ""
        self.value = value.strip() if value is not None else ""
        self._mock_now_time = None

    @abstractmethod
    def __str__(self):
        """ A text representation of the scheduler """
        raise NotImplementedError()

    @abstractmethod
    def type():
        """ A string that identifies the scheduler """
        raise NotImplementedError()

    @abstractmethod
    def check(self):
        """ Checks what a scheduler would do on the instance given the tag """
        raise NotImplementedError()

    def now_utc(self):
        """ Current or mock time in UTC """
        if self._mock_now_time is not None:
            return self._mock_now_time
        return datetime.utcnow().replace(tzinfo=tz.utc)

    @staticmethod
    def build(instance, sched_type, name, value):
        if sched_type is None:
            return None

        if sched_type.lower() == DailyScheduler.type():
            return DailyScheduler(instance, name, value)

        elif sched_type.lower() == TimerScheduler.type():
            return TimerScheduler(instance, name, value)

        elif sched_type.lower() == IgnoreScheduler.type():
            return IgnoreScheduler(instance, name, value)

        elif sched_type.lower() == FixedScheduler.type():
            return FixedScheduler(instance, name, value)

        return None

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
        """ Parses a string time as UTC time """
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
            time = timezone.localize(time, is_dst=None).astimezone(tz.utc)

        # Only return time
        return time.time().replace(tzinfo=tz.utc)

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

    The format of the tag value is: "<action>/<time_span>"
     - "action" is "start" to start the instance or "stop" to stop the instance
        after time_span minutes have passed
     - "time_span" is a time duration in minutes, like 60 to indicate an hour
    """
    def __init__(self, instance, name, value):
        super(self.__class__, self).__init__(instance, name, value)
        self._error = False

        # Check for bad values
        if self.value is None or self.value == "":
            print("None or empty value", file=sys.stderr)
            self._error = True
            return

        fields = self.value.split("/")

        # Check fields
        if len(fields) != 2:
            print("Wrong number of fields", file=sys.stderr)
            self._error = True
            return

        # Interpreting tag
        try:
            self.action = fields[0].lower()
            if self.action not in ["start", "stop"]:
                self._error = True
                return
            minutes = int(fields[1] if fields[1] != "" else "0")
            self.timer = timedelta(minutes=minutes)
        except Exception as e:
            print("Exception: %s" % e.message, file=sys.stderr)
            self._error = True
            return

    def __str__(self):
        if self._error:
            return "TimerScheduler: ERROR"

        return "TimerScheduler, Name: \"%s\", Action: %s, Timer: %s" % (
            self.name, self.action, self.timer
        )

    @staticmethod
    def type():
        return "timer"

    def check(self):
        if self._error:
            return "error"

        # Instance up/down time
        if self._instance.status() == 'running':
            instance_time = self._instance.start_time()
            if self.action == "start":
                self.action = None
        elif self._instance.status() == 'stopped':
            instance_time = self._instance.stop_time()
            if self.action == "stop":
                self.action = None
        else:
            return None

        # Cases when the time is not defined
        if instance_time is None:
            return None

        # If the instance must be started or stopped
        if (self.now_utc() - instance_time) > self.timer:
            return self.action

        return None


class DailyScheduler(Scheduler):
    """
    Find the appropriate action for the scheduler type "daily"

    The format of the tag value is: "<start_time>/<stop_time>[/<week_days>[/<timezone>]]"
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
       specified, the default is UTC. Instead of using the "/" as separator, use
       "-", for instance use "Europe-London" instead of "Europe/London"
    """
    def __init__(self, instance, name, value):
        super(self.__class__, self).__init__(instance, name, value)
        self._error = False

        # Check for bad values
        if self.value is None or self.value == "":
            print("None or empty value", file=sys.stderr)
            self._error = True
            return

        # Extract the parameters
        fields = self.value.split("/")

        # Check fields
        if len(fields) < 2 or len(fields) > 4:
            print("Wrong number of fields", file=sys.stderr)
            self._error = True
            return

        try:
            # Time zone
            self.time_zone = fields[3] if len(fields) > 3 and fields[3] != "" else "UTC"

            # Time the instance has to start
            self.start_time = Scheduler.parse_time(fields[0], self.time_zone)

            # Time the instance has to stop
            self.stop_time = Scheduler.parse_time(fields[1], self.time_zone)

            # Parsing day
            days_active = fields[2] if len(fields) > 2 else "all"
            self.days_active = Scheduler.parse_day(days_active)

        except Exception as e:
            print("-" * 80, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print("-" * 80, file=sys.stderr)
            self._error = True
            return

    def __str__(self):
        if self._error:
            return "DailyScheduler: ERROR"

        return "DailyScheduler, Name: \"%s\", Start: %sUTC, Stop: %sUTC, Days: %s" % (
            self.name,
            self.start_time,
            self.stop_time,
            ','.join(self.days_active)
        )

    @staticmethod
    def type():
        return "daily"

    def check(self):
        # Protection in case of None value
        if self._error:
            return "error"

        # Check day of the week
        now_weekday = self.now_utc().strftime("%a").lower()
        if now_weekday not in self.days_active:
            return None

        now_time = self.now_utc().time().replace(tzinfo=tz.utc)

        # No time range specified (weird...)
        if self.start_time is None and self.stop_time is None:
            return None

        # No start time
        if self.start_time is None:
            if now_time >= self.stop_time:
                return "stop"
            return None

        # No stop time
        if self.stop_time is None:
            if now_time < self.start_time:
                return "start"
            return None

        # When the start is after the stop
        if self.start_time > self.stop_time:
            self.start_time, self.stop_time = self.stop_time, self.start_time

        if now_time >= self.start_time and now_time < self.stop_time:
            return "start"
        elif now_time >= self.stop_time:
            return "stop"

        # Something else
        return None


class IgnoreScheduler(Scheduler):
    """
    This scheduler always returns "ignore", useful for debugging or safety.

    The format of the tag value is: "ignore"
    """
    def __init__(self, instance, name, value):
        super(self.__class__, self).__init__(instance, name, value)

        self._error = False
        if self.value != "ignore":
            self._error = True

    def __str__(self):
        return "IgnoreScheduler: ignore all scheduler tags"

    @staticmethod
    def type():
        return "ignore_all"

    def check(self):
        if self._error:
            return "error"
        return "ignore"


class FixedScheduler(Scheduler):
    """
    This scheduler keeps an instance always started or stopped, useful for
    debugging or safety.

    The format of the tag value is: "[start|stop]"
     - "start" keeps the instance always started.
     - "stop" keeps the instance always stopped.
    """
    def __init__(self, instance, name, value):
        super(self.__class__, self).__init__(instance, name, value)

        self._error = False
        if self.value not in ['start', 'stop']:
            self._error = True

    def __str__(self):
        if self._error:
            return "FixedScheduler: ERROR"
        if self.value == 'start':
            return "FixedScheduler: keep the instance started"
        elif self.value == 'stop':
            return "FixedScheduler: keep the instance stopped"

    @staticmethod
    def type():
        return "fixed"

    def check(self):
        if self._error:
            return "error"
        return self.value

# vim: ft=python:ts=4:sw=4