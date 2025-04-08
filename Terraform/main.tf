provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(pathexpand(var.credentials_file))
}

# Create GCS bucket for data backups
resource "google_storage_bucket" "data_bucket" {
  name     = "${var.project_id}-data-bucket"
  location = var.region
  force_destroy = true
  
  versioning {
    enabled = true
  }
}

# Create BigQuery dataset
resource "google_bigquery_dataset" "raw_data" {
  dataset_id  = "raw_data"
  description = "Raw data from job APIs"
  location    = var.region
}

resource "google_bigquery_dataset" "transformed_data" {
  dataset_id  = "transformed_data"
  description = "Transformed data models"
  location    = var.region
}
