##  Lambda Function  ##

locals {
  code_zip_file       = "${path.module}/tag-scheduler.zip"
  scheduler_name      = "TagScheduler"
}

resource "aws_lambda_function" "tag_scheduler" {
  tags {
    Name              = "${local.scheduler_name}"
    Terraform         = "True"
    TagScheduler      = "True"
  }
  function_name       = "${local.scheduler_name}"
  description         = "Scheduler to start and stop resources based on tags."
  role                = "${aws_iam_role.tag_scheduler.arn}"
  handler             = "tagscheduler.lambda_handler"
  runtime             = "python2.7"
  memory_size         = "128"
  timeout             = "240"
  filename            = "${local.code_zip_file}"
  source_code_hash    = "${base64sha256(file(local.code_zip_file))}"
  environment {
    variables {
      RUN_ON_REGIONS  = "${join(",", var.run_on_regions)}"
    }
  }
}

##  Scheduled event  ##

resource "aws_cloudwatch_event_rule" "tag_scheduler" {
  name                = "${local.scheduler_name}"
  description         = "Rule to trigger ${local.scheduler_name} function on a schedule"
  schedule_expression = "rate(5 minutes)"
  depends_on          = ["aws_lambda_function.tag_scheduler"]
}

resource "aws_cloudwatch_event_target" "tag_scheduler" {
  rule                = "${aws_cloudwatch_event_rule.tag_scheduler.name}"
  target_id           = "${local.scheduler_name}"
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
  name                = "${local.scheduler_name}Role"
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
      "rds:StartDBInstance",
      "rds:StopDBInstance",
      "rds:DescribeDBInstances",
      "rds:ListTagsForResource"
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
