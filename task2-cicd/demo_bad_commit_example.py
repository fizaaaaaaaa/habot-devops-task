# DEMO FILE — used only to demonstrate the fail-closed gate in your presentation.
# Do NOT commit real secrets like this. This file exists purely so you can show
# the pipeline turning RED and blocking a bad commit, then show it fixed.

# --- BAD (this is what the gate should catch) ---
# api_key = "REPLACE_ME_HARDCODED_SECRET_abcdef1234567890"

# --- GOOD (how it should actually be done) ---
import os

api_key = os.environ.get("HABOT_API_KEY")  # pulled from a secret manager / env var, never hardcoded
