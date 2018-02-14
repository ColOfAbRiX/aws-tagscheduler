# Tag Scheduler

Terraform module for a custom and extensible tags-based AWS scheduler for EC2 and RDS.

## Description

_Tag Scheduler_ uses instance tags to schedule starting and stopping of EC2 and RDS instances on AWS.

The package comes with the following type of schedulers:

- **DailyScheduler:** starts or stop an instance based on the specified time each one of the specified week days. It also supports time zones;
- **TimerScheduler:** starts or stop an instance after a predetermined amount of time;
- **IgnoreScheduler:** this scheduler is meant to do no work on the instances, useful for debugging, maintenance or safety;
- **FixedScheduler:** keeps an instance always started or stopped, useful for debugging or safety.

The _Tag Scheduler_ keeps a log on CloudWatch of the operations being done.

## Terraform

This terraform module can be used as any other [Terraform modules](https://www.terraform.io/docs/modules/index.html). Here is an example implementation:

```HCL
provider "aws" {
  access_key         = "${var.aws_access_key}"
  secret_key         = "${var.aws_secret_key}"
  region             = "${var.aws_region}"
}

module "scheduler" {
  source             = "github.com/ColOfAbRiX/aws-tagscheduler"
  run_on_regions     = [""]
  scheduler_interval = "5 minutes"
}
```

### Terraform Input Variables

#### run_on_regions

The list of AWS regions where to run the schedulers, if omitted it will run on every available AWS region.

#### scheduler_interval

The interval of execution of the scheduler. The default is every 5 minutes

# Scheduler Usage

## Basics

Schedulers are assigned to instances creating tags with specific names and values.

An instance can have multiple independent schedulers.

On regular intervals _Tag Scheduler_ will scan all available instances, it will execute all the schedulers assigned to each instance and determine the final action to take for that specific instance.

When executed, each scheduler can have 3 possible actions:

- **start**: it requests a start of the instance;
- **stop**: it requests a stops of the instance;
- **nothing**: when no action is requested (e.g. no need to start a running instance).

When multiple schedulers are present they are sorted alphabetically based on their name (see later for a description of the name fields) and executed one after each other. The action to be executed is the last one that has a value different than **nothing**.

## Tags

_Tag Scheduler_ will scan the instances looking for tag names that respect the format: `scheduler-<scheduler_type>[-<name>]`. It will then execute the associated `<scheduler_type>` (scheduler types are described below).

The field `<name>` is optional and it's used to sort the schedulers: the schedulers are first sorted alphabetically, based on their `<name>` and then executed.

For instance, given 3 schedulers named `scheduler-daily-a`, `scheduler-timer-00` `scheduler-daily` they will be executed in the following order:

- `scheduler-daily`, which action is **start**;
- `scheduler-timer-00` which action is **nothing**;
- `scheduler-daily-a` which action is **stop**.

The action that each scheduler would execute is written in the list above. The last one to have an action different than _nothing_ will have its action executed. In this example `scheduler-timer-a` will be the one to execute the **stop** action.

## Scheduler types

This section describes the format of the tag names and values and the behaviour of the various schedulers.

### Daily Scheduler

Tag name format: `scheduler-daily[-<name>]`

Tag value format: `<start_time>/<stop_time>[/<week_days>[/<timezone>]]`

- `start_time` is the time at which the instance must start, in the format HHMM (24h format), like 0730. If omitted the instance will not be started but it will keep its state as it is;
- `stop_time` is the time at which the instance must stop, in the format HHMM (24h format), like 1800; If omitted the instance will not be stopped but it will keep its state as it is;
- `week_days` is a list of 3 letters names of the week separated by a dot like "mon.wed.sat". Also valid are "all" for all the days of the week, "weekdays" for days from Monday to Friday and "weekends" for just Saturday and Sunday;
- `timezone` is the time zone in TZ Database format, like EST or Canada-Yukon (note that `-` must be used as separator instead of `/`). If not specified, the default is UTC.

#### Examples:

To run an instance every evening:

`scheduler-daily-evening`: `1800/2100`

To run an instance during office hours in London:

`scheduler-daily-office`: `0800/1800/weekdays/Europe-London`

To make sure the instance is started every Monday and Wednesday morning, not caring when it stops:

`scheduler-daily`: `0800//mon.wed`

To make sure the instance is always stopped on weekends:

`scheduler-daily-stop_for_weekends`: `/0000/sat`

### Timer Scheduler

Tag name format: `scheduler-timer[-<name>]`

Tag value format: `<action>/<time_span>`

- `<action>` is `start` to start the instance or `stop` to stop the instance after `time_span` minutes have passed;
- `<time_span>` is a time duration in minutes, like 60 to indicate an hour.

#### Examples:

To stop an instance after 2 hours it's been running:

`scheduler-timer-only_scheduler`: `stop/120`

To start an instance after 5 minutes it's been stopped:

`scheduler-timer-only_scheduler`: `start/5`

### Ignore Scheduler

Tag name format: `scheduler-ignore[-<name>]`

Tag value format: `ignore`

#### Examples

To ignore every other scheduler:

`scheduler-ignore-temporary`: `ignore`

### Fixed Scheduler

Tag name format: `scheduler-fixed[-<name>]`

Tag value format: `[start|stop]`

- `start` keeps the instance always started;
- `stop` keeps the instance always stopped.

#### Examples

To keep an RDS always stopped and circumvent the 7 days limitation:

`scheduler-fixed`: `stop`

## Changing the code

If you wish to make any change to the [Python code](src/tagscheduler) of the _Tag Scheduler_ you have to re-create the associated [ZIP file](tag-scheduler.zip) before running Terraform. This can be done running the [shell script](pack.sh) that will take care of installing the dependencies, run the unit tests and pack the final result.

## License

MIT

## Author Information

[Fabrizio Colonna](mailto:colofabrix@tin.it)

## Contributors

Issues, feature requests, ideas, suggestions, etc. are appreciated and can be posted in the Issues section.

Pull requests are also very welcome. Please create a topic branch for your proposed changes. If you don't, this will create conflicts in your fork after the merge.
