##  Lambda Function  ##

resource "aws_lambda_function" "tag_scheduler" {
  tags {
    Name              = "TagScheduler"
    Terraform         = "True"
    Scheduler         = "True"
  }
  function_name       = "TagScheduler"
  description         = "Lambda function for automatically starting and stopping EC2 instances."
  role                = "${aws_iam_role.tag_scheduler.arn}"
  handler             = "tag-scheduling.lambda_handler"
  runtime             = "python2.7"
  memory_size         = "128"
  timeout             = "240"
  filename            = "${path.module}/tag-scheduler.zip"
}

##  Scheduled event  ##

resource "aws_cloudwatch_event_rule" "tag_scheduler" {
  name                = "TagScheduler"
  description         = "Rule to trigger TagScheduler function on a schedule"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "tag_scheduler" {
  rule                = "${aws_cloudwatch_event_rule.tag_scheduler.name}"
  target_id           = "TagScheduler"
  arn                 = "${aws_lambda_function.tag_scheduler.arn}"
}

##  Function permissions  ##

resource "aws_lambda_permission" "tag_scheduler" {
  statement_id        = "AllowExecutionFromCloudWatch"
  action              = "lambda:InvokeFunction"
  function_name       = "${aws_lambda_function.tag_scheduler.function_name}"
  principal           = "events.amazonaws.com"
  source_arn          = "${aws_cloudwatch_event_rule.tag_scheduler.arn}"
}

##  Role  ##

resource "aws_iam_role" "tag_scheduler" {
  name                = "TagSchedulerRole"
  assume_role_policy  = "${data.aws_iam_policy_document.tag_scheduler_assume_role.json}"
}

##  Assume Role Policy  ##

data "aws_iam_policy_document" "tag_scheduler_assume_role" {
  statement {
    actions           = ["sts:AssumeRole"]
    principals {
      type            = "Service"
      identifiers     = ["lambda.amazonaws.com"]
    }
  }
}

##  Scheduler permissions  ##

data "aws_iam_policy_document" "tag_scheduler_permissions" {
  statement {
    actions           = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources         = ["arn:aws:logs:*:*:log-group:/aws/lambda/*"]
  }
  statement {
    actions           = [
      # To list the available regions
      "ec2:DescribeRegions",
      # To work with Tag
      "ec2:StartInstances",
      "ec2:StopInstances",
      "ec2:DescribeInstances",
      # To work with RDS
      "rds:StartDBInstances",
      "rds:StopDBInstances",
      "rds:DescribeDBInstances",
      # Who knows
      "kms:CreateGrant"
    ]
    resources         = ["*"]
  }
}

resource "aws_iam_policy" "tag_scheduler_permissions" {
  name                = "tag_scheduler_permissions"
  path                = "/"
  policy              = "${data.aws_iam_policy_document.tag_scheduler_permissions.json}"
}

resource "aws_iam_role_policy_attachment" "tag_scheduler_permissions" {
  role                = "${aws_iam_role.tag_scheduler.name}"
  policy_arn          = "${aws_iam_policy.tag_scheduler_permissions.arn}"
}
