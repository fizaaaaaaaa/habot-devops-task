"""
HabotConnect Hiring Project — Task 3: Django Model
Submitted by: [YOUR FULL NAME HERE]
Contact: [YOUR EMAIL HERE]
"""

from django.db import models


class Student(models.Model):
    """
    Mirrors the BigQuery 'students' table schema from Task 1
    (see task1-terraform/schemas/students_schema.json) so the Django app and
    the analytics warehouse never drift apart.
    """

    student_id = models.CharField(max_length=20, unique=True, primary_key=True)
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    assigned_lsa_email = models.EmailField()
    learning_needs = models.TextField(blank=True, null=True)

    # Stored as clean 'YES'/'NO' strings only — enforced by DCYN at the
    # serializer layer before this model is ever saved.
    guardian_consent_given = models.CharField(max_length=3)
    requires_one_on_one_support = models.CharField(max_length=3)
    has_prior_iep_or_504_plan = models.CharField(max_length=3)
    data_sharing_consent = models.CharField(max_length=3)

    onboarding_status = models.CharField(max_length=3, default="NO")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "contenttypes"  # piggybacks on an already-installed app for this standalone demo
        db_table = "students"
