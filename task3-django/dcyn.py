"""
HabotConnect Hiring Project — Task 3: DCYN (Deconstructed Yes/No) Library
Submitted by: [YOUR FULL NAME HERE]
Contact: [YOUR EMAIL HERE]

Purpose
-------
"DCYN" = Deconstruct into a Clean Yes/No binary logic library.

The idea: instead of letting ambiguous values ("true", "1", "yes", "Y", True,
"maybe", blank, etc.) flow into the database and be interpreted differently
in different places, every incoming field that represents a yes/no decision
gets passed through ONE function that returns exactly "YES", "NO", or raises
an error. There is no third option and no silent guessing — this is what
"entirely eliminates human judgment" means in the task brief.
"""

from __future__ import annotations


class DCYNValidationError(ValueError):
    """Raised when a value cannot be deconstructed into a clean Yes/No."""


# The ONLY values this library will ever accept as valid input.
# Anything not in this map is rejected outright — no guessing, no fuzzy match.
_TRUTHY = {"yes", "y", "true", "1", True, 1}
_FALSY = {"no", "n", "false", "0", False, 0}


def to_dcyn(value, *, field_name: str = "field") -> str:
    """
    Deconstructs an arbitrary incoming value into exactly 'YES' or 'NO'.

    Raises DCYNValidationError for anything ambiguous (None, blank string,
    'maybe', 'n/a', partial values, etc.) rather than guessing.
    """
    if isinstance(value, str):
        normalized = value.strip().lower()
    else:
        normalized = value

    if normalized in _TRUTHY:
        return "YES"
    if normalized in _FALSY:
        return "NO"

    raise DCYNValidationError(
        f"'{field_name}' has an ambiguous value ({value!r}) that cannot be "
        f"deconstructed into YES/NO. Reject and quarantine this record — "
        f"do not guess."
    )


def dcyn_batch(payload: dict, yes_no_fields: list[str]) -> dict:
    """
    Runs to_dcyn() across a whole incoming payload for a defined list of
    fields that must be binary Yes/No. Returns a new dict with those fields
    normalized to 'YES'/'NO'. Raises on the FIRST ambiguous field found —
    fail closed, don't partially process a bad record.
    """
    result = dict(payload)
    for field in yes_no_fields:
        if field not in payload:
            raise DCYNValidationError(f"Required DCYN field '{field}' is missing.")
        result[field] = to_dcyn(payload[field], field_name=field)
    return result
