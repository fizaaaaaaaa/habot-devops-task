variable "gcp_project_id" {
  description = "GCP project ID that resources will be created in"
  type        = string
  default     = "habot-devops-task-508507"
}

variable "gcp_region" {
  description = "GCP region for regional resources (bucket, dataset, keyring)"
  type        = string
  default     = "us-central1"
}

variable "ingestion_service_account" {
  description = "Service account email allowed to write into the raw landing bucket (least privilege: write-only, no delete/list)"
  type        = string
  default     = "habot-ingestion@habot-devops-task-508507.iam.gserviceaccount.com"
}

variable "lsa_group_email" {
  description = "Identity the Row-Level Security policy is scoped to. In production this would be a real Google Workspace group (e.g. lsa-staff@habot.io); for this demo, use your own Google account email so Terraform can verify the identity actually exists."
  type        = string
  # Replace with YOUR OWN Google account email for the demo to succeed.
  default     = "fizahello01@gmail.com"
}
