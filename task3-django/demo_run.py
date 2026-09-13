"""
Run this to prove Task 3 works, without needing a full Django server running.
Usage:  python demo_run.py
"""

import json
import os

import django
from django.conf import settings

# Minimal in-memory Django setup so the serializer can be exercised standalone
if not settings.configured:
    settings.configure(
        INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
    )
    django.setup()

from serializers import StudentOnboardingSerializer  # noqa: E402

with open(os.path.join(os.path.dirname(__file__), "sample_payload.json")) as f:
    payload = json.load(f)

serializer = StudentOnboardingSerializer(data=payload)

if serializer.is_valid():
    print("VALID. Normalized DCYN fields:")
    for field in [
        "guardian_consent_given",
        "requires_one_on_one_support",
        "has_prior_iep_or_504_plan",
        "data_sharing_consent",
    ]:
        print(f"  {field}: {serializer.validated_data[field]}")
else:
    print("REJECTED:")
    print(json.dumps(serializer.errors, indent=2))
