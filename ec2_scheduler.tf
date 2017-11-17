##  Lambda Function  ##

resource "aws_lambda_function" "ec2_scheduler" {
  tags {
    Name              = "EC2Scheduler"
    Terraform         = "True"
    Scheduler         = "True"
  }
  function_name       = "EC2Scheduler"
  description         = "Lambda function for automatically starting and stopping EC2 instances."
  role                = "${aws_iam_role.ec2_scheduler.arn}"
  handler             = "ec2-scheduler.lambda_handler"
  runtime             = "python2.7"
  memory_size         = "128"
  timeout             = "300"
  filename            = "${path.module}/ec2-scheduler.zip"
}

##  Scheduled event  ##

resource "aws_cloudwatch_event_rule" "ec2_scheduler" {
  name                = "EC2Scheduler"
  description         = "Rule to trigger EC2Scheduler function on a schedule"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "ec2_scheduler" {
  rule                = "${aws_cloudwatch_event_rule.ec2_scheduler.name}"
  target_id           = "EC2Scheduler"
  arn                 = "${aws_lambda_function.ec2_scheduler.arn}"
}

##  Function permissions  ##

resource "aws_lambda_permission" "ec2_scheduler" {
  statement_id        = "AllowExecutionFromCloudWatch"
  action              = "lambda:InvokeFunction"
  function_name       = "${aws_lambda_function.ec2_scheduler.function_name}"
  principal           = "events.amazonaws.com"
  source_arn          = "${aws_cloudwatch_event_rule.ec2_scheduler.arn}"
}


##  Role  ##

resource "aws_iam_role" "ec2_scheduler" {
  name                = "EC2SchedulerRole"
  assume_role_policy  = "${data.aws_iam_policy_document.ec2_scheduler_assume_role.json}"
}

##  Assume Role Policy  ##

data "aws_iam_policy_document" "ec2_scheduler_assume_role" {
  statement {
    actions           = ["sts:AssumeRole"]
    principals {
      type            = "Service"
      identifiers     = ["lambda.amazonaws.com"]
    }
  }
}

##  Scheduler permissions  ##

data "aws_iam_policy_document" "ec2_scheduler_permissions" {
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
      "ec2:StartInstances",
      "ec2:StopInstances",
      "ec2:DescribeRegions",
      "ec2:DescribeInstances",
      "kms:CreateGrant",
      "cloudwatch:PutMetricData",
      "cloudformation:DescribeStacks"
    ]
    resources         = ["*"]
  }
}

resource "aws_iam_policy" "ec2_scheduler_permissions" {
  name                = "ec2_scheduler_permissions"
  path                = "/"
  policy              = "${data.aws_iam_policy_document.ec2_scheduler_permissions.json}"
}

resource "aws_iam_role_policy_attachment" "ec2_scheduler_permissions" {
  role                = "${aws_iam_role.ec2_scheduler.name}"
  policy_arn          = "${aws_iam_policy.ec2_scheduler_permissions.arn}"
}
