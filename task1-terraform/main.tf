# =============================================================================
# HabotConnect Hiring Project — Task 1: Terraform Secure Staging Provisioning
# Submitted by: [YOUR FULL NAME HERE]
# Contact: [YOUR EMAIL HERE]
#
# Purpose: Provisions a "D0 Raw Landing" GCS bucket and a "D1 Staged/Enforced"
# BigQuery dataset, with least-privilege IAM, encryption at rest, and a
# Row-Level Security policy restricting LSA staff to only their own students.
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.40.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# -----------------------------------------------------------------------------
# Encryption: a dedicated KMS key so the bucket is not relying on Google's
# default encryption — this is called "Customer-Managed Encryption Key" (CMEK)
# -----------------------------------------------------------------------------
resource "google_kms_key_ring" "habot_keyring" {
  name     = "habot-staging-keyring"
  location = var.gcp_region
}

resource "google_kms_crypto_key" "bucket_key" {
  name     = "d0-bucket-key"
  key_ring = google_kms_key_ring.habot_keyring.id

  lifecycle {
    prevent_destroy = true # never allow Terraform to accidentally delete the key
  }
}

# GCS's own service agent needs permission to use the KMS key to encrypt/decrypt
data "google_storage_project_service_account" "gcs_account" {}

resource "google_kms_crypto_key_iam_member" "gcs_can_use_key" {
  crypto_key_id = google_kms_crypto_key.bucket_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
}

# -----------------------------------------------------------------------------
# Task 1a: D0 Raw Landing bucket (GCS)
# -----------------------------------------------------------------------------
resource "google_storage_bucket" "raw_landing" {
  name                        = "${var.gcp_project_id}-d0-raw-landing"
  location                    = var.gcp_region
  uniform_bucket_level_access = true  # forces IAM-only access control, no legacy per-object ACLs
  force_destroy               = false # safety net: refuses to delete a non-empty bucket

  versioning {
    enabled = true # protects against accidental overwrite/delete of raw files
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.bucket_key.id
  }

  public_access_prevention = "enforced" # hard-blocks any public access, even by mistake

  depends_on = [google_kms_crypto_key_iam_member.gcs_can_use_key]
}

# Least privilege: the ingestion service account can only CREATE objects,
# not delete or list the whole bucket
resource "google_storage_bucket_iam_member" "raw_landing_writer" {
  bucket = google_storage_bucket.raw_landing.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.ingestion_service_account}"
}

# -----------------------------------------------------------------------------
# Task 1b: D1 Staged/Enforced dataset (BigQuery)
# ----------------------------------------------------------------------------
resource "google_bigquery_dataset" "staged_enforced" {
  dataset_id                  = "d1_staged_enforced"
  friendly_name               = "D1 Staged Enforced"
  location                    = var.gcp_region
  description                 = "Schema-validated, access-controlled student and LSA data"
  default_table_expiration_ms = null # this data is permanent, not temporary

  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  access {
    role          = "WRITER"
    user_by_email = var.ingestion_service_account
  }
}

resource "google_bigquery_table" "students" {
  dataset_id          = google_bigquery_dataset.staged_enforced.dataset_id
  table_id            = "students"
  deletion_protection = true

  schema = file("${path.module}/schemas/students_schema.json")
}

# -----------------------------------------------------------------------------
# Task 1c: Row-Level Security — LSA staff only see rows for students assigned
# to them, even though they have READ access to the table itself
# -----------------------------------------------------------------------------
resource "google_bigquery_row_access_policy" "lsa_own_students_only" {
  project          = var.gcp_project_id
  dataset_id       = google_bigquery_dataset.staged_enforced.dataset_id
  table_id         = google_bigquery_table.students.table_id
  policy_id        = "lsa_scope"
  filter_predicate = "assigned_lsa_email = SESSION_USER()"
  grantees         = ["user:${var.lsa_group_email}"]

}
