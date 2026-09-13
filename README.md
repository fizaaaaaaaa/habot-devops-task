# HabotConnect Hiring Project — Junior Cloud & DevOps Engineer

**Submitted by:** [YOUR FULL NAME HERE]
**Contact:** [YOUR EMAIL HERE]
**Date:** [DATE]
**Repository:** [YOUR GITHUB REPO LINK HERE]

## What this project is
A take-home hiring project simulating a real staging incident: a junior developer
left unencrypted API credentials in code and caused a database schema mismatch.
This submission restores system integrity across three areas — secure cloud
infrastructure, an automated build gate, and strict data validation.

---

## Full folder structure

```
habot-devops-task/
├── README.md                         This file
├── .gitleaks.toml                    Secret-scanning rules used by the Task 2 pipeline
├── .github/
│   └── workflows/
│       └── build-gate.yml            The actual Task 2 CI/CD pipeline (GitHub Actions)
├── task1-terraform/                  Task 1: Infrastructure as Code
│   ├── main.tf                       Provisions the GCS bucket, BigQuery dataset/table, KMS, IAM, Row-Level Security
│   ├── variables.tf                  Configurable inputs (project ID, region, service account, etc.)
│   ├── outputs.tf                    Values printed after a successful `terraform apply`
│   ├── .gitignore                    Excludes local Terraform state and cache from git
│   ├── .terraform.lock.hcl           Locks the exact provider version (safe/expected to commit)
│   └── schemas/
│       └── students_schema.json      BigQuery table schema for the `students` table
├── task2-secret-scan-demo/           Task 2: supporting demo file only
│   └── demo_bad_commit_example.py    File used to intentionally trigger the fail-closed gate for evidence
├── task3-django/                     Task 3: Django/DRF schema validation
│   ├── dcyn.py                       The Deconstructed Yes/No (DCYN) validation library
│   ├── models.py                     Django `Student` model
│   ├── serializers.py                DRF serializer enforcing exact field limits + DCYN validation
│   ├── demo_run.py                   Standalone script proving the serializer works, no server needed
│   ├── sample_payload.json           Example incoming student-onboarding JSON payload
│   ├── requirements.txt              Python dependencies (Django, djangorestframework)
│   └── .gitignore                    Excludes the local virtual environment and Python cache from git
├── documents/                        Final submission deliverables
│   ├── HabotConnect_Fiza.pptx        Presentation (max 15 slides, architecture + evidence)
│   ├── HabotConnectfiza.pdf          PDF export of the presentation (backup format)
│   └── HabotConnect_Schema_Mapping.xlsx   Task 3 field-mapping spreadsheet (Wrap Text enabled, full field names)
└── screenshots/                      Raw evidence screenshots (also embedded in the presentation)
    ├── Terraform_Apply.png           Task 1 — successful `terraform apply` output
    ├── Gcp_console_1.png             Task 1 — GCS bucket in the GCP console
    ├── Gcp_console_2.png             Task 1 — BigQuery dataset/table in the GCP console
    ├── git-leak-1.png                Task 2 — Gitleaks detecting the intentional bad commit (fail)
    ├── git-leak-2.png                Task 2 — Quarantine job triggering on that failure
    ├── no-leak-detected.png          Task 2 — clean pipeline run, no secrets detected
    ├── Correct_demo_run.png          Task 3 — valid payload, all DCYN fields normalized
    ├── maybe_correct_demo_run.png    Task 3 — ambiguous value correctly rejected
    └── incorrect_demo_run.png        Task 3 — missing guardian consent correctly rejected
```

---

## Task 1: Terraform Secure Staging Provisioning

**What it does:** Provisions a GCS "D0 Raw Landing" bucket and a BigQuery "D1
Staged/Enforced" dataset with encryption, least-privilege IAM, and Row-Level
Security so LSA staff can only see their own assigned students.

**How to run it:**
```powershell
cd task1-terraform
terraform init
terraform plan
terraform apply
```

**Verified output (see `screenshots/Terraform_Apply.png`):**
```
raw_landing_bucket_name = "habot-devops-task-508507-d0-raw-landing"
staged_dataset_id       = "d1_staged_enforced"
students_table_id       = "habot-devops-task-508507.d1_staged_enforced.students"
```

**Demo note:** The Row-Level Security grantee and dataset owner use a personal
Google account and the built-in `projectOwners`/`projectReaders` special
groups, standing in for a real HabotConnect Workspace group (e.g.
`lsa-staff@habot.io`) that would exist in production.

---

## Task 2: Poka-Yoke Automated CI/CD Build Gate

**What it does:** A GitHub Actions pipeline (`.github/workflows/build-gate.yml`)
that runs on every push. It lints and formats the code, scans for hardcoded
secrets using Gitleaks, and only allows deployment if every check passes —
"fail-closed" by design.

**How to see it run:** Push any commit to the repository and check the
**Actions** tab on GitHub.

**How the fail-closed demo was captured:**
1. Uncommented the fake key in `task2-secret-scan-demo/demo_bad_commit_example.py`
2. Pushed — Gitleaks failed and the Quarantine job printed
   `"This commit is QUARANTINED and is blocked from deploying."`
   (see `screenshots/git-leak-1.png` and `git-leak-2.png`)
3. Reverted the commit — the pipeline passed cleanly again
   (see `screenshots/no-leak-detected.png`)

---

## Task 3: Schema Mapping and DCYN Validation

**What it does:** `dcyn.py` normalizes any incoming yes/no value to exactly
`"YES"` or `"NO"`, rejecting anything ambiguous. `serializers.py` is a Django
REST Framework serializer that enforces exact field formats and runs every
yes/no field through DCYN before accepting a student-onboarding record.

**How to run it:**
```powershell
cd task3-django
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python demo_run.py
```

**Three scenarios verified (see `screenshots/`):**
- `Correct_demo_run.png` — a fully valid payload, all fields normalized
- `maybe_correct_demo_run.png` — an ambiguous value (e.g. `"maybe"`) correctly rejected
- `incorrect_demo_run.png` — missing guardian consent correctly rejected

---

## Submission checklist
- [x] Terraform, YAML, and Python code delivered in a structured folder layout
- [x] Presentation (max 15 slides) with architecture overview and logic flow
- [x] Fail-closed gate demonstrated with before/after evidence
- [x] Schema-mapping spreadsheet uses Wrap Text and full field names throughout
- [ ] Name and contact info filled in on this README, the presentation, and the answer document
- [ ] Submitted via the Google Form: https://forms.gle/qaTCAxi3YA8MCN196
- [ ] Submitted before the deadline: 13 September 2026
