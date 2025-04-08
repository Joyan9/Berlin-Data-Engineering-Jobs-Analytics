variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "data-engg-job-analytics"
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default = "europe-west10"
}

variable "credentials_file" {
  description = "Path to the service account key file"
  type        = string
  default     = "~/terraform-service-account.json"
}