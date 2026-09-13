"""
HabotConnect Hiring Project — Task 3: Schema Mapping and DCYN Validation
Submitted by: [YOUR FULL NAME HERE]
Contact: [YOUR EMAIL HERE]

Purpose
-------
Takes the raw incoming student-onboarding JSON payload and validates it with
exact field limits (no vague "any string is fine"), then runs every yes/no
field through the DCYN library so nothing ambiguous ever reaches the model.
"""

from datetime import date

from rest_framework import serializers

try:
    from .dcyn import DCYNValidationError, dcyn_batch
    from .models import Student
except ImportError:
    # Falls back to a plain import when run as a standalone script (e.g.
    # demo_run.py) rather than as part of an installed Django app package.
    from dcyn import DCYNValidationError, dcyn_batch
    from models import Student

# Fields in the incoming payload that MUST be binary yes/no decisions.
DCYN_FIELDS = [
    "guardian_consent_given",
    "requires_one_on_one_support",
    "has_prior_iep_or_504_plan",
    "data_sharing_consent",
]


class StudentOnboardingSerializer(serializers.ModelSerializer):
    # Exact field validation limits — no placeholders, no "trust the client"
    student_id = serializers.RegexField(
        regex=r"^STU-\d{4}-\d{5}$",
        max_length=20,
        error_messages={
            "invalid": "student_id must exactly match format STU-YYYY-NNNNN "
            "(e.g. STU-2026-00417)."
        },
    )
    full_name = serializers.CharField(min_length=2, max_length=150, trim_whitespace=True)
    date_of_birth = serializers.DateField()
    assigned_lsa_email = serializers.EmailField()
    learning_needs = serializers.CharField(
        max_length=1000, required=False, allow_blank=True, allow_null=True
    )

    # These four come in as loose strings ("Yes", "true", "N", "1", ...) and
    # get normalized to exactly "YES"/"NO" in validate() below via DCYN.
    guardian_consent_given = serializers.CharField(write_only=False)
    requires_one_on_one_support = serializers.CharField(write_only=False)
    has_prior_iep_or_504_plan = serializers.CharField(write_only=False)
    data_sharing_consent = serializers.CharField(write_only=False)

    class Meta:
        model = Student
        fields = [
            "student_id",
            "full_name",
            "date_of_birth",
            "assigned_lsa_email",
            "learning_needs",
            "guardian_consent_given",
            "requires_one_on_one_support",
            "has_prior_iep_or_504_plan",
            "data_sharing_consent",
        ]

    def validate_date_of_birth(self, value: date) -> date:
        """A student onboarding record must belong to a real, currently-a-minor child."""
        today = date.today()
        age_years = (today - value).days / 365.25
        if age_years < 0:
            raise serializers.ValidationError("date_of_birth cannot be in the future.")
        if age_years > 18:
            raise serializers.ValidationError(
                "date_of_birth implies an age over 18 — outside expected LSA program range."
            )
        return value

    def validate(self, attrs: dict) -> dict:
        """
        Runs every DCYN field through the deconstruction library as one
        atomic step. If ANY field is ambiguous, the whole record is rejected
        — fail closed, matching the Task 2 pipeline philosophy.
        """
        try:
            normalized = dcyn_batch(attrs, DCYN_FIELDS)
        except DCYNValidationError as exc:
            raise serializers.ValidationError({"dcyn_validation": str(exc)})

        attrs.update(normalized)

        # Business rule enforced in code, not left to human judgment:
        # data cannot be onboarded at all without guardian consent.
        if attrs["guardian_consent_given"] == "NO":
            raise serializers.ValidationError(
                {"guardian_consent_given": "Cannot onboard a student without guardian consent."}
            )

        return attrs
