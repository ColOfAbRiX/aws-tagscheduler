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

import re
import pytz as tz
from datetime import datetime
from abc import ABCMeta, abstractmethod


class Schedulable(object):
    """
    Any object that can be scheduled to start and stop
    """
    __metaclass__ = ABCMeta

    def __init__(self, client, instance):
        if client is None:
            raise ValueError("Client cannot be None.")
        if instance is None:
            raise ValueError("Instance cannot be None.")

        self._client = client
        self._instance = instance

    @abstractmethod
    def id(self):
        """ Amazon ID of the resource """
        raise NotImplementedError()

    @abstractmethod
    def start_time(self):
        """ The UTC time the resource has been started """
        raise NotImplementedError()

    @abstractmethod
    def stop_time(self):
        """ The UTC time the resource has been stopped """
        raise NotImplementedError()

    @abstractmethod
    def status(self):
        """ The current status of the resource, either running or stopped """
        raise NotImplementedError()

    @abstractmethod
    def tags(self):
        """ List of tags of the resource sorted by tag name """
        raise NotImplementedError()

    @abstractmethod
    def start(self):
        """ Start the instance """
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        """ Stop the instance """
        raise NotImplementedError()


class EC2Schedulable(Schedulable):
    """
    Representation of an EC2 instance being schedulable
    """
    def __init__(self, client, instance):
        super(self.__class__, self).__init__(client, instance)

    def id(self):
        return self._instance.instance_id

    def start_time(self):
        if self.status() == "running":
            return tz.timezone('UTC').localize(
                self._instance.launch_time,
                is_dst=None
            )
        return None

    def stop_time(self):
        if self.status() == "stopped":
            reason = self._instance.state_transition_reason
            stop_time = re.findall('.*\((.*)\)', reason)[0]
            stop_time = datetime.strptime(stop_time, '%Y-%m-%d %H:%M:%S %Z')
            return tz.timezone('UTC').localize(stop_time, is_dst=None)
        return None

    def status(self):
        return self._instance.state['Name'].lower()

    def tags(self):
        return sorted(self._instance.tags, key=lambda x: x['Key'])

    def start(self):
        self._instance.start()
        return True

    def stop(self):
        self._instance.stop()
        return True


class RDSSchedulable(Schedulable):
    """
    Representation of an RDS instance being schedulable
    """

    def __init__(self, client, instance):
        super(self.__class__, self).__init__(client, instance)

    def id(self):
        return self._instance['DbiResourceId']

    def start_time(self):
        # Not applicable for RDS
        return None

    def stop_time(self):
        # Not applicable for RDS
        return None

    def status(self):
        status = self._instance['DBInstanceStatus'].lower()
        if status == "available":
            return "running"
        elif status == "stopped":
            return "stopped"
        return None

    def tags(self):
        tags = self._client.list_tags_for_resource(
            ResourceName=self._instance['DBInstanceArn']
        )
        return sorted(tags['TagList'], key=lambda x: x['Key'])

    def start(self):
        self._client.start_db_instance(
            DBInstanceIdentifier=self._instance['DBInstanceIdentifier']
        )
        return True

    def stop(self):
        self._client.stop_db_instance(
            DBInstanceIdentifier=self._instance['DBInstanceIdentifier']
        )
        return True

# vim: ft=python:ts=4:sw=4