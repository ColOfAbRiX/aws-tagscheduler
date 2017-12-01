variable "run_on_regions" {
  type        = "list"
  default     = [""]
  description = "The list of AWS regions where to run the schedulers."
}
