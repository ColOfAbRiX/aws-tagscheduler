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

    @staticmethod
    def build(sched_type, instance):
        if sched_type.lower() == StartStopScheduler.type():
            return StartStopScheduler(instance)
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


class TimerScheduler(Scheduler):
    """
    Find the appropriate action for the scheduler type "timer".

    The format of the tag is: "<action>/<time_span>"
     - "action" is start to start the instance or stop to stop the instance
     - "time_span" is a time duration in minutes, like 60 to indicate an hour
    """
    @staticmethod
    def type():
        return "timer"

    def check(self, tag_value):
        now_time = datetime.now().replace(tzinfo=None)
        split = tag_value.split("/")

        # Interpreting tag
        try:
            action = split[0].lower()
            max_duration = timedelta(minutes=int(split[1]))
        except Exception as e:
            return "error"

        # Instance up/down time
        if self._instance.status() == 'running':
            instance_time = self._instance.start_time()
        elif self._instance.status() == 'stopped':
            instance_time = self._instance.stop_time()
        else:
            return None

        if instance_time is None:
            return None

        # If the instance must be started or stopped
        if (now_time - instance_time) > max_duration:
            return action

        return None


class StartStopScheduler(Scheduler):
    """
    Find the appropriate action for the scheduler type "startstop"

    The format of the tag is: "<start_time>/<stop_time>/<week_days>"
     - "start_time" is the time at which the instance must start, in the format
        HHMM (24h format), like 0730. If omitted the instance will not be started
     - "stop_time" is the time at which the instance must stop, in the format
        HHMM (24h format), like 1800; If omitted the instance will not be stopped
     - "week_days" is a list of 3 letters names of the week separated by a dash
       like "mon-wed-sat". Also valid are "all" for all the days of the week,
       "weekdays" for days from Monday to Friday and "weekends" for just Saturday
       and Sunday.
    """
    @staticmethod
    def type():
        return "startstop"

    def check(self, tag_value):
        # Some useful info
        now_time = datetime.now().time()
        now_weekday = datetime.today().strftime("%a").lower()

        # Extract the parameters
        split = tag_value.split("/")

        try:
            # Time the instance has to start
            start_time = split[0].strip()
            if start_time == "":
                start_time = None
            else:
                start_time = datetime.strptime(start_time, '%H%M').time()

            # Time the instance has to stop
            stop_time = split[1].strip()
            if stop_time == "":
                stop_time = None
            else:
                stop_time = datetime.strptime(stop_time, '%H%M').time()

            # Days of the week the scheduler is active
            days_active = split[2].lower().strip()
            if days_active == "weekdays":
                days_active = ['mon', 'tue', 'wed', 'thu', 'fri']
            elif days_active == "weekends":
                days_active = ['sat', 'sun']
            elif days_active == "all" or days_active == "":
                days_active = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
            else:
                days_active = days_active.split("-")
        except Exception as e:
            return "error"

        # Check day of the week
        is_active_day = False
        for d in days_active:
            if d.lower() == now_weekday:
                is_active_day = True
        if not is_active_day:
            return None

        # No time range specified (weird...)
        if start_time is None and stop_time is None:
            return None

        # No start time
        if start_time is None:
            if now_time >= stop_time:
                return "stop"

        # No stop time
        if stop_time is None:
            if now_time < start_time:
                return "start"

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