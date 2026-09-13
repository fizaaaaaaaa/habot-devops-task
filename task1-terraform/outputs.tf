output "raw_landing_bucket_name" {
  description = "Name of the D0 raw landing GCS bucket"
  value       = google_storage_bucket.raw_landing.name
}

output "raw_landing_bucket_url" {
  description = "gsutil URL for the bucket"
  value       = google_storage_bucket.raw_landing.url
}

output "staged_dataset_id" {
  description = "BigQuery dataset ID for D1 Staged/Enforced"
  value       = google_bigquery_dataset.staged_enforced.dataset_id
}

output "students_table_id" {
  description = "Fully qualified students table"
  value       = "${var.gcp_project_id}.${google_bigquery_dataset.staged_enforced.dataset_id}.${google_bigquery_table.students.table_id}"
}
