# Tag Scheduler

Custom and extensible AWS scheduler for EC2 and RDS based on tags.

## Description

_Tag Scheduler_ uses instance tags to schedule starting and stopping of EC2 and RDS instances on AWS.

The package comes with the following type of schedulers:

- **DailyScheduler:** starts or stop an instance based on the specified time each one of the specified week days. It also supports time zones;
- **TimerScheduler:** starts or stop an instance after a predetermined amount of time;
- **IgnoreScheduler:** this scheduler is meant to do no work on the instances, useful for debugging, maintenance or safety;
- **FixedScheduler:** keeps an instance always started or stopped, useful for debugging or safety.

The _Tag Scheduler_ keeps a log on CloudWatch of the operations being done.

## Terraform Input Variables

### run_on_regions

The list of AWS regions where to run the schedulers, if omitted it will run on every available AWS region.

### scheduler_interval

The interval of execution of the scheduler. The default is every 5 minutes

# Scheduler Usage

The _Tag Scheduler_ looks for instance tags in the format `scheduler-<scheduler_type>[-<name>]` and will take different **actions** based on the `<scheduler_type>`. A scheduler can have 3 possible actions on an instance:

- **start**: it starts the instance only when the instance is stopped;
- **stop**: it stops the instance only when the instance is running;
- **nothing**: when no action is required on the instance (e.g. no need to start a running instance).

The field `<name>` is optional and it's used to sort the schedulers when using multiple schedulers on the same instance. It's a way of assign priorities.
Schedulers will be sorted alphabetically based on the name. For instance, given 3 schedulers named `scheduler-daily-a`, `scheduler-timer-00` `scheduler-daily` they will have the following priority:

- `scheduler-daily`, action is **nothing**;
- `scheduler-timer-00` action is **start**;
- `scheduler-daily-a` action is **nothing**.

The last scheduler to have an action different than _nothing_ for the instance will have its action executed. In the example above the instance will be started by the scheduler named `scheduler-timer-00`.

## Daily Scheduler

Tag name format: `scheduler-daily[-<name>]`
Tag value format: `<start_time>/<stop_time>[/<week_days>[/<timezone>]]`

- `start_time` is the time at which the instance must start, in the format HHMM (24h format), like 0730. If omitted the instance will not be started but it will keep its state as it is;
- `stop_time` is the time at which the instance must stop, in the format HHMM (24h format), like 1800; If omitted the instance will not be stopped but it will keep its state as it is;
- `week_days` is a list of 3 letters names of the week separated by a dot like "mon.wed.sat". Also valid are "all" for all the days of the week, "weekdays" for days from Monday to Friday and "weekends" for just Saturday and Sunday;
- `timezone` is the time zone in TZ Database format, like EST or Canada-Yukon (note that `-` must be used as separator instead of `/`). If not specified, the default is UTC.

### Examples:

To run an instance every evening:

`scheduler-daily-evening`: `1800/2100`

To run an instance during office hours in London:

`scheduler-daily-office`: `0800/1800/weekdays/Europe-London`

To make sure the instance is started every Monday and Wednesday morning, not caring when it stops:

`scheduler-daily`: `0800//mon.wed`

To make sure the instance is always stopped on weekends:

`scheduler-daily-stop_for_weekends`: `/0000/sat`

## Timer Scheduler

Tag name format: `scheduler-timer[-<name>]`
Tag value format: `<action>/<time_span>`

- `<action>` is `start` to start the instance or `stop` to stop the instance after `time_span` minutes have passed;
- `<time_span>` is a time duration in minutes, like 60 to indicate an hour.

### Examples:

To stop an instance after 2 hours it's been running:

`scheduler-timer-only_scheduler`: `stop/120`

To start an instance after 5 minutes it's been stopped:

`scheduler-timer-only_scheduler`: `start/5`

## Ignore Scheduler

Tag name format: `scheduler-ignore[-<name>]`
Tag value format: `ignore`

### Examples

To ignore every other scheduler:

`scheduler-ignore-temporary`: `ignore`

## Fixed Scheduler

Tag name format: `scheduler-fixed[-<name>]`
Tag value format: `[start|stop]`

- `start` keeps the instance always started;
- `stop` keeps the instance always stopped.

### Examples

To keep an RDS always stopped and circumvent the 7 days limitation:

`scheduler-fixed`: `stop`

## License

MIT

## Author Information

[Fabrizio Colonna](colofabrix@tin.it)
