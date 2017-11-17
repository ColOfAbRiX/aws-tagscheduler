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

import json
import uuid
import boto3
import datetime
import traceback

from urllib2 import Request
from urllib2 import urlopen
from collections import Counter


def putCloudWatchMetric(region, instance_id, instance_state):
    cw = boto3.client('cloudwatch')
    cw.put_metric_data(
        Namespace='EC2Scheduler',
        MetricData=[{
            'MetricName': instance_id,
            'Value': instance_state,
            'Unit': 'Count',
            'Dimensions': [{
                'Name': 'Region',
                'Value': region
            }]
        }]

    )


def lambda_handler(event, context):
    print("Running EC2 Scheduler")

    ec2 = boto3.client('ec2')
    awsRegions = ec2.describe_regions()['Regions']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("EC2-Scheduler")
    response = table.get_item(Key={'SolutionName': 'EC2Scheduler'})

    # Configuration
    config = {
        'createMetrics': "Enabled",
        'customTagName': "scheduler-startstop",
        'defaultDaysActive': "all",
        'defaultStartTime': "0800",
        'defaultStopTime': "1800",
        'defaultTimeZone': "utc",
        'UUID': uuid.uuid4(),
    }
    if 'Item' in response:
        item = response['Item']
        config = {
            'createMetrics': str(item.get('CloudWatchMetrics', config['createMetrics'])).lower(),
            'customTagName': str(item.get('CustomTagName', config['customTagName'])),
            'defaultDaysActive': str(item.get('DefaultDaysActive', config['defaultDaysActive'])),
            'defaultStartTime': str(item.get('DefaultStartTime', config['defaultStartTime'])),
            'defaultStopTime': str(item.get('DefaultStopTime', config['defaultStopTime'])),
            'defaultTimeZone': str(item.get('DefaultTimeZone', config['defaultStopTime'])),
            'UUID': str(item.get('UUID', config['UUID'])),
        }

    customTagLen = len(config['customTagName'])
    TimeNow = datetime.datetime.utcnow().isoformat()
    TimeStamp = str(TimeNow)

    # Declare Dicts
    regionDict = {}
    allRegionDict = {}
    regionsLabelDict = {}
    postDict = {}

    for region in awsRegions:
        try:
            awsregion = region['RegionName']
            now = datetime.datetime.now().strftime("%H%M")
            nowMax = (datetime.datetime.now() - datetime.timedelta(minutes=59)).strftime("%H%M")
            nowDay = datetime.datetime.today().strftime("%a").lower()

            # Create connection to the EC2 using Boto3 resources interface
            ec2 = boto3.resource('ec2', region_name=region['RegionName'])

            # Declare Lists
            startList = []
            stopList = []
            runningStateList = []
            stoppedStateList = []

            # List all instances
            instances = ec2.instances.all()

            print("Creating %s instance lists...", region['RegionName'])

            for i in instances:
                if i.tags != None:
                    for t in i.tags:
                        if t['Key'][:customTagLen] == config['customTagName']:
                            print("Found tag " + t['Key'] + " with value " + str(t['Value']))
                            ptag = t['Value'].split("/")
                            print(ptag)

                            # Split out Tag & Set Variables to default
                            default1 = 'default'
                            default2 = 'true'
                            startTime = config['defaultStartTime']
                            stopTime = config['defaultStopTime']
                            timeZone = config['defaultTimeZone']
                            daysActive = config['defaultDaysActive']
                            state = i.state['Name']
                            itype = i.instance_type

                            # Post current state of the instances
                            if config['createMetrics'] == 'enabled':
                                if state == "running":
                                    putCloudWatchMetric(region['RegionName'], i.instance_id, 1)
                                if state == "stopped":
                                    putCloudWatchMetric(region['RegionName'], i.instance_id, 0)

                            # Parse tag-value
                            if len(ptag) >= 1:
                                if ptag[0].lower() in (default1, default2):
                                    startTime = config['defaultStartTime']
                                else:
                                    startTime = ptag[0]
                                    stopTime = ptag[0]
                            if len(ptag) >= 2:
                                stopTime = ptag[1]
                            if len(ptag) >= 3:
                                timeZone = ptag[2].lower()
                            if len(ptag) >= 4:
                                daysActive = ptag[3].lower()

                            isActiveDay = False

                            # Days Interpreter
                            if daysActive == "all":
                                isActiveDay = True
                            elif daysActive == "weekdays":
                                weekdays = ['mon', 'tue', 'wed', 'thu', 'fri']
                                if (nowDay in weekdays):
                                    isActiveDay = True
                            else:
                                daysActive = daysActive.split(",")
                                for d in daysActive:
                                    if d.lower() == nowDay:
                                        isActiveDay = True

                            # Append to start list
                            if startTime >= str(nowMax) and startTime <= str(now) and \
                                    isActiveDay == True and state == "stopped":
                                startList.append(i.instance_id)
                                print(i.instance_id, " added to START list")
                                if config['createMetrics'] == 'enabled':
                                    putCloudWatchMetric(region['RegionName'], i.instance_id, 1)

                            # Append to stop list
                            if stopTime >= str(nowMax) and stopTime <= str(now) and \
                                    isActiveDay == True and state == "running":
                                stopList.append(i.instance_id)
                                print(i.instance_id, " added to STOP list")
                                if config['createMetrics'] == 'enabled':
                                    putCloudWatchMetric(region['RegionName'], i.instance_id, 0)

                            if state == 'running':
                                runningStateList.append(itype)
                            if state == 'stopped':
                                stoppedStateList.append(itype)

            # Execute Start and Stop Commands
            if startList:
                print("Starting", len(startList), "instances", startList)
                ec2.instances.filter(InstanceIds=startList).start()
            else:
                print("No Instances to Start")

            if stopList:
                print("Stopping", len(stopList) ,"instances", stopList)
                ec2.instances.filter(InstanceIds=stopList).stop()
            else:
                print("No Instances to Stop")

        except Exception as e:
            print("Exception:")
            print("-" * 60)
            traceback.print_exc()
            print("-" * 60)
            continue

# vim: ft=python:ts=4:sw=4