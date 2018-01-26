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

# Ugly hack to allow import from the code folder. Please forgive the heresy.
from sys import path
from os.path import dirname, join
path.append(join(dirname(path[0]), "tagscheduler"))

from tagscheduler import *
from datetime import datetime, time


class MockSchedulable:
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
    def __init__(self, schtype="mockscheduler", instance=MockSchedulable(), name="mock", value="", check_result=True):
        super(self.__class__, self).__init__(instance, name, value)
        self.check_result = check_result
        self.schtype = schtype

    def __str__(self):
        return "MockScheduler"

    def type(self):
        return self.schtype

    def check(self):
        return self.check_result


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


class MockEC2Instance:
    """
    Mock of boto3 EC2.Instance
    """
    def __init__(self, start_return=True, stop_return=True, instance_id="", launch_time="", state_transition_reason="", client=None, status="", tags={}):
        self.start_return = start_return
        self.stop_return = stop_return
        self.instance_id = instance_id
        self.launch_time = datetime.strptime(launch_time, '%Y-%m-%d %H:%M:%S') if launch_time != "" else ""
        self.state_transition_reason = state_transition_reason
        self.client = client
        self.state = {'Name': status}
        self.tags = [{'Key': key, 'Value': val} for key, val in tags.iteritems()]

    def start(self):
        return self.start_return

    def stop(self):
        return self.stop_return


class MockRDSInstance:
    """
    Mock of boto3 RDS.Client RDS instance information
    """
    def __init__(self, start_return=True, stop_return=True, db_resource_id="", db_instance_status="", tags={}):
        self.start_return = start_return
        self.stop_return = stop_return
        self.db_resource_id = db_resource_id
        self.db_instance_status = db_instance_status
        self.tags = {
            'TagList': [{'Key': key, 'Value': val} for key, val in tags.iteritems()]
        }

    def __getitem__(self, key):
        if key == 'DBInstanceArn':
            return "random_string"
        elif key == 'DBInstanceStatus':
            return self.db_instance_status
        elif key == 'DbiResourceId':
            return self.db_resource_id
        return None

    def start_db_instance(self, DBInstanceIdentifier):
        return self.start_return

    def stop_db_instance(self, DBInstanceIdentifier):
        return self.stop_return

    def list_tags_for_resource(self, ResourceName):
        return self.tags


# vim: ft=python:ts=4:sw=4