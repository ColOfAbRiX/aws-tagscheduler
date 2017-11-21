##  Lambda Function  ##

resource "aws_lambda_function" "rds_scheduler" {
  tags {
    Name              = "RDSScheduler"
    Terraform         = "True"
    Scheduler         = "True"
  }
  function_name       = "RDSScheduler"
  description         = "Lambda function for automatically starting and stopping RDS instances."
  role                = "${aws_iam_role.rds_scheduler.arn}"
  handler             = "rds-scheduler.lambda_handler"
  runtime             = "python2.7"
  memory_size         = "128"
  timeout             = "120"
  filename            = "${path.module}/rds-scheduler.zip"
}

##  Scheduled event  ##

resource "aws_cloudwatch_event_rule" "rds_scheduler" {
  name                = "RDSScheduler"
  description         = "Rule to trigger RDSScheduler function on a schedule"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "rds_scheduler" {
  rule                = "${aws_cloudwatch_event_rule.rds_scheduler.name}"
  target_id           = "RDSScheduler"
  arn                 = "${aws_lambda_function.rds_scheduler.arn}"
}

##  Function permissions  ##

resource "aws_lambda_permission" "rds_scheduler" {
  statement_id        = "AllowExecutionFromCloudWatch"
  action              = "lambda:InvokeFunction"
  function_name       = "${aws_lambda_function.rds_scheduler.function_name}"
  principal           = "events.amazonaws.com"
  source_arn          = "${aws_cloudwatch_event_rule.rds_scheduler.arn}"
}


##  Role  ##

resource "aws_iam_role" "rds_scheduler" {
  name                = "RDSSchedulerRole"
  assume_role_policy  = "${data.aws_iam_policy_document.rds_scheduler_assume_role.json}"
}

##  Assume Role Policy  ##

data "aws_iam_policy_document" "rds_scheduler_assume_role" {
  statement {
    actions           = ["sts:AssumeRole"]
    principals {
      type            = "Service"
      identifiers     = ["lambda.amazonaws.com"]
    }
  }
}

##  Scheduler permissions  ##

data "aws_iam_policy_document" "rds_scheduler_permissions" {
  statement {
    actions           = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources         = ["arn:aws:logs:*:*:log-group:/aws/lambda/*"]
  }
  statement {
    actions           = ["dynamodb:GetItem"]
    resources         = ["arn:aws:dynamodb:*:*:table/*"]
  }
  statement {
    actions           = [
      "ec2:DescribeRegions",
      "rds:StartDBInstances",
      "rds:StopDBInstances",
      "rds:DescribeDBInstances",
      "kms:CreateGrant"
    ]
    resources         = ["*"]
  }
}

resource "aws_iam_policy" "rds_scheduler_permissions" {
  name                = "rds_scheduler_permissions"
  path                = "/"
  policy              = "${data.aws_iam_policy_document.rds_scheduler_permissions.json}"
}

resource "aws_iam_role_policy_attachment" "rds_scheduler_permissions" {
  role                = "${aws_iam_role.rds_scheduler.name}"
  policy_arn          = "${aws_iam_policy.rds_scheduler_permissions.arn}"
}
