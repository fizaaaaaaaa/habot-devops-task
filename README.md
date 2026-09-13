# HabotConnect Hiring Project — Junior Cloud & DevOps Engineer

**Submitted by:** [YOUR FULL NAME HERE]
**Contact:** [YOUR EMAIL HERE]
**Date:** [DATE]

## Scenario
A junior developer pushed unencrypted API credentials into raw application code
and caused a database schema mismatch that broke downstream analytics. This
project restores system integrity across three areas: infrastructure security,
automated build gates, and data validation.

---

## Folder structure
```
habot-devops-task/
├── README.md
├── task1-terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── schemas/
│       └── students_schema.json
├── task2-cicd/
│   ├── .github/workflows/build-gate.yml
│   ├── .gitleaks.toml
│   └── demo_bad_commit_example.py
└── task3-django/
    ├── dcyn.py
    ├── models.py
    ├── serializers.py
    ├── demo_run.py
    ├── sample_payload.json
    └── requirements.txt
```

---

## Task 1: Terraform Secure Staging Provisioning

Provisions, via Infrastructure-as-Code, a GCS "D0 Raw Landing" bucket and a
BigQuery "D1 Staged/Enforced" dataset, with:
- Customer-managed KMS encryption on the bucket
- `uniform_bucket_level_access` + `public_access_prevention = "enforced"` (no
  accidental public exposure)
- Least-privilege IAM: the ingestion service account can only create objects,
  not delete or list
- Row-Level Security on the `students` table: LSA staff can only see rows
  where they are the assigned LSA

**Deployed to project:** `habot-devops-task-508507`

**Verified outputs from a live `terraform apply`:**
```
raw_landing_bucket_name = "habot-devops-task-508507-d0-raw-landing"
raw_landing_bucket_url  = "gs://habot-devops-task-508507-d0-raw-landing"
staged_dataset_id       = "d1_staged_enforced"
students_table_id       = "habot-devops-task-508507.d1_staged_enforced.students"
```

**Demo-environment note:** In production, the Row-Level Security grantee and
dataset OWNER would be a real HabotConnect Google Workspace group/domain
(e.g. `lsa-staff@habot.io`). Since this project ran on a personal Google
account without Workspace admin access, the demo substitutes the developer's
own account email and the built-in `projectOwners` / `projectReaders` special
groups to prove the mechanism works end-to-end. The `main.tf` comments and
`variables.tf` descriptions call this out explicitly.

**To run:**
```bash
cd task1-terraform
terraform init
terraform plan
terraform apply
```

---

## Task 2: Poka-Yoke Automated CI/CD Build Gate

A GitHub Actions pipeline (`.github/workflows/build-gate.yml`) that runs on
every push/PR and is **fail-closed**: deployment only happens if every gate
passes cleanly.

Gates enforced:
1. **Lint/format** — Black + Flake8 on the Django code, `terraform fmt -check`
   and `terraform validate` on the Terraform code
2. **Secret scanning** — Gitleaks, with a custom rule set (`.gitleaks.toml`)
   tuned to catch hardcoded API keys and embedded GCP service-account keys
3. **Quarantine** — a dedicated job that only fires on any gate failure, to
   make the "halt and quarantine" behavior explicit in the Actions log
4. **Deploy** — only reachable if both prior jobs succeeded

**To run:**
1. Push this whole repo to GitHub, keeping `.github/workflows/build-gate.yml`
   at that exact path
2. Watch it run automatically under the repo's "Actions" tab

**To demonstrate the fail-closed behavior:**
1. In `demo_bad_commit_example.py`, uncomment the line with the fake
   `api_key = "sk_live_..."` value
2. Commit and push — screenshot the pipeline turning red on the
   `secret-scan` job and the `quarantine_on_failure` job triggering
3. Re-comment the line, push again — screenshot the clean green run
4. Include both screenshots in the presentation as before/after evidence

---

## Task 3: Schema Mapping and DCYN Validation

`dcyn.py` implements a single-purpose library that deconstructs any incoming
value into exactly `"YES"` or `"NO"` — anything ambiguous (blank, `"maybe"`,
`None`, partial values) is rejected outright rather than guessed at.

`serializers.py` is a Django REST Framework `ModelSerializer` that:
- Enforces exact field formats (e.g. `student_id` must match
  `STU-YYYY-NNNNN`, `date_of_birth` must imply an age ≤ 18)
- Runs every yes/no field in the incoming payload through `dcyn_batch()`
  as one atomic validation step
- Rejects the entire record if guardian consent is `"NO"` — a business rule
  enforced in code, not left to human review

**To run (proves it works without a full Django server):**
```bash
cd task3-django
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python demo_run.py
```
Expected output: all four DCYN fields normalized to `YES`/`NO`.

**To demonstrate the rejection path:** change any DCYN field in
`sample_payload.json` to an ambiguous value (e.g. `"maybe"`) and re-run —
it should be cleanly rejected with a clear error message, not silently
accepted.

---

## Submission checklist
- [ ] Name and contact info filled in at the top of `main.tf`,
      `build-gate.yml`, `serializers.py`, `dcyn.py`, and this README
- [ ] `terraform apply` screenshots (plan + final outputs)
- [ ] GCP Console screenshots (bucket, dataset/table, row access policy)
- [ ] GitHub Actions before/after screenshots (red fail-closed → green pass)
- [ ] Task 3 demo_run.py output screenshots (valid + rejected cases)
- [ ] Slide deck (max 15 slides) covering architecture, logic flow, and the
      fail-closed demonstration, with links to the code repo
- [ ] Submitted via the Google Form:
      https://forms.gle/qaTCAxi3YA8MCN196
- [ ] Submitted before the deadline: 13 September 2026
