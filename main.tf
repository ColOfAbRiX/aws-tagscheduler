resource "aws_dynamodb_table" "ec2_scheduler" {
  tags {
    Name           = "EC2-Scheduler"
    Terraform      = "True"
    Scheduler      = "True"
  }
  name             = "EC2-Scheduler"
  read_capacity    = 1
  write_capacity   = 1
  hash_key         = "SolutionName"
  attribute {
    name           = "SolutionName"
    type           = "S"
  }
}
