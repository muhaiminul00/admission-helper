"""Shared helper for resolving the single imported Routine.

Routine has no natural unique key (per 02.1_Database_Model_Contract_v1.0.md,
only `id`), so a fixed name is used to keep repeated `import_csv` runs
idempotent - every run resolves to the same Routine row rather than
creating a new one each time.
"""

ROUTINE_NAME = "Imported Routine"


def get_or_create_routine():
    from routines.models import Routine

    routine, _ = Routine.objects.update_or_create(
        name=ROUTINE_NAME, defaults={"active": True}
    )
    return routine
