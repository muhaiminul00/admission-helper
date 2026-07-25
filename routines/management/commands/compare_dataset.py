"""Compare new CSVs against the current database state, without
importing anything (Milestone 10).

Usage:
    python manage.py compare_dataset [--dir DIR]

Reuses the exact same comparison engine `import_csv --preview` uses
(routines/services/dataset/comparison.py) - there is only one
comparison implementation.
"""

import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from routines.services.dataset.comparison import COMPARISON_SECTIONS, compare_all, detect_duplicates


class Command(BaseCommand):
    help = "Compare a directory of CSVs against the current database state."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir", default=str(settings.BASE_DIR),
            help="Directory containing the CSV files to compare (default: project root).",
        )

    def handle(self, *args, **options):
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

        base_dir = Path(options["dir"])

        duplicates = detect_duplicates(base_dir)
        if any(duplicates.values()):
            self.stdout.write(self.style.WARNING("Duplicate keys found in the new dataset:"))
            for entity, keys in duplicates.items():
                if keys:
                    self.stdout.write(f"  {entity}: {keys}")
            self.stdout.write("")

        diff = compare_all(base_dir)

        self.stdout.write("Dataset Comparison")
        self.stdout.write("=" * 32)
        self.stdout.write("")

        for key, label, _fn in COMPARISON_SECTIONS:
            section = diff[key]
            self.stdout.write(f"## {label}")
            self.stdout.write(
                f"  Added: {len(section['added'])}  "
                f"Modified: {len(section['modified'])}  "
                f"Removed: {len(section['removed'])}  "
                f"Unchanged: {len(section['unchanged'])}"
            )
            for entry in section["added"][:10]:
                self.stdout.write(f"    + {entry['key']}")
            for entry in section["modified"][:10]:
                self.stdout.write(f"    ~ {entry['key']}: {list(entry['changes'].keys())}")
            for entry in section["removed"][:10]:
                self.stdout.write(f"    - {entry['key']}")
            self.stdout.write("")

        events = diff["routine_events"]
        self.stdout.write("## Routine Events")
        self.stdout.write(
            f"  {events['total_rows']} total rows "
            f"({', '.join(f'{v} {k}' for k, v in events['by_event_type'].items())})"
        )
        self.stdout.write(
            f"  CLASS rows: {events['class_rows_added']} added, "
            f"{events['class_rows_modified']} modified, "
            f"{events['class_rows_removed']} removed, "
            f"{events['class_rows_unchanged']} unchanged"
        )
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Comparison complete. No changes were made."))
