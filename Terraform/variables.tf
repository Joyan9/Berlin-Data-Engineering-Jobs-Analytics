variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "data-engg-job-analytics" # CHANGE TO YOUR PROJECT ID
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default = "europe-west10" # CHANGE TO YOUR DATASET LOCATION
}

variable "credentials_file" {
  description = "Path to the service account key file"
  type        = string
  default     = "/home/joyan/Berlin-Data-Engineering-Jobs-Analytics/Terraform/credentials/service_account.json" # CHANGE TO YOUR CREDS PATH
}