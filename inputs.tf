variable "run_on_regions" {
  type        = "list"
  default     = [""]
  description = "The list of AWS regions where to run the schedulers."
}

variable "scheduler_interval" {
  type        = "string"
  default     = "5 minutes"
  description = "The interval of execution of the scheduler."
}
