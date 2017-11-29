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
import traceback

from awsobjects import *
from schedulers import *
from schedulable import *


# Prefix of all tags that are schedulers
SCHEDULER_PREFIX="scheduler"


def lambda_handler(event, context):
    """ AWS Lambda Function entry point """
    run_on_regions = filter(None, os.environ.get('RUN_ON_REGIONS', "").split(','))
    run_tagscheduler(run_on_regions)


def run_tagscheduler(run_on_regions=[]):
    """
    Runs the schedulers on the resources of various regions
    """
    print("Running Tag Scheduler")

    # Going through all the AWS regions
    try:
        if run_on_regions == []:
            run_on_regions = get_all_regions()

        for region in run_on_regions:
            print("\nWorking on region \"%s\":" % region)

            all_instances = get_all_instances(region)
            instance_actions = {}

            for i_type, i_list in all_instances.iteritems():
                print("  Checking %s instances:" % i_type)
                for instance in i_list:
                    try:
                        instance_actions.update(
                            process_instance(instance)
                        )

                    except Exception as e:
                        print("-" * 80)
                        print("Instance Exception")
                        traceback.print_exc()
                        print("-" * 80)

            # Execute the requested scheduling actions
            execute_actions(instance_actions)

    except Exception as e:
        print("-" * 80)
        print("Region Exception")
        traceback.print_exc()
        print("-" * 80)


def process_instance(instance):
    """
    Process the tags of a single instance and decides what to do with it
    """
    print("    Instance \"%s\" state is \"%s\"" % (instance.id(), instance.status()))

    actions = {
        instance.id(): {
            'instance_ref': instance,
            'action': None
        }
    }

    # Execute the schedulers
    for s in build_instance_schedulers(instance):
        print("      - Found scheduler tag with value: \"%s\":" % s['value'])
        print("        Scheduler type is: %s" % s['type'])
        if s['type'] == 'unknown':
            continue

        # Find what the scheduler would do on the instance
        tag_action = s['scheduler'].check(s['value'])
        if tag_action is None:
            tag_action = "nothing"
        print("        Tag action is: %s" % tag_action)
        print("        Scheduler action is: ", end='')

        # Actions "start"
        if tag_action == "start" and instance.status() == "stopped":
            actions[instance.id()].update({
                'action': "start"
            })
            print("start.")

        # Actions "stop"
        elif tag_action == "stop" and instance.status() == "running":
            actions[instance.id()].update({
                'action': "stop"
            })
            print("stop.")

        # Actions "ignore"
        elif tag_action == "ignore":
            actions[instance.id()].update({
                'action': None
            })
            print("ignore all schedulers.\n      Stop processing schedulers for this instance.")
            break

        # Actions "error"
        elif tag_action == "error":
            print("error.\n      ERROR from the scheduler.")
            break

        # Errors
        else:
            print("nothing required.")

    return actions


def build_instance_schedulers(instance):
    """
    Build the list of schedulers
    """
    schedulers = []

    print("      Building and sorting list of schedulers.")
    for t_key, t_value in [(t['Key'], t['Value']) for t in instance.tags()]:

        # Extract the information in the Key
        t_key_split = t_key.split("-")
        if len(t_key_split) < 2:
            continue

        # Check it's a scheduler
        scheduler_tag = t_key_split[0]
        if scheduler_tag != SCHEDULER_PREFIX:
            continue

        # Get the scheduler type
        scheduler_type = t_key_split[1]
        scheduler = Scheduler.build(scheduler_type, instance)
        if scheduler == None:
            scheduler_type = "unknown"

        # Get the scheduler name, if any
        scheduler_name = t_key_split[2] if len(t_key_split) > 2 else ""

        # Add the scheduler
        schedulers.append({
            'type': scheduler_type,
            'name': scheduler_name,
            'value': t_value,
            'scheduler': scheduler
        })

    # Sort the schedulers by their name
    return sorted(schedulers, key=lambda s: s['name'])


def execute_actions(instance_actions):
    """
    Executes the start/stop actions on the required instances
    """
    print("  Execute scheduling actions:")
    executed = 0
    for i_id, info in instance_actions.iteritems():
        instance, action = (info['instance_ref'], info['action'])

        if action is None:
            continue

        elif action == "start":
            print("    START instance %s" % i_id)
            instance.start()
            executed += 1

        elif action == "stop":
            print("    STOP instance %s" % i_id)
            instance.stop()
            executed += 1

    if executed == 0:
        print("    No instances to start or stop.")


if __name__ == '__main__':
    """ Console entry point """
    print("Execution from Command Line\n")

    run_on_regions = filter(None, os.environ.get('RUN_ON_REGIONS', "").split(','))
    run_tagscheduler(run_on_regions)

# vim: ft=python:ts=4:sw=4