variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "The target AWS region for deployment"
}

variable "instance_type" {
  type        = string
  default     = "t2.micro" # t2.micro is standard for AWS Free Tier
  description = "Free-tier eligible compute instance size"
}