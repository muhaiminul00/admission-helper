# Coding Standards

**Project:** Varsity Admission Tracker\
**Document:** 08_Coding_Standards.md\
**Version:** 1.0\
**Status:** Locked for Version 1

------------------------------------------------------------------------

# 1. Purpose

This document defines the coding standards for Version 1 to keep the
codebase clean, consistent, and easy to maintain.

The guiding principle is:

> Write code that is easy to understand six months from now.

------------------------------------------------------------------------

# 2. General Principles

-   Prefer readability over cleverness.
-   Keep solutions simple.
-   Follow Django conventions whenever possible.
-   Avoid duplicate code.
-   Write small, focused functions.
-   Remove unused code before merging.

------------------------------------------------------------------------

# 3. Project Structure

The Django app structure is locked.

``` text
core/
dashboard/
subjects/
lectures/
progress/
routines/
reminders/
```

Each app should contain only code related to its feature.

------------------------------------------------------------------------

# 4. Python Style

-   Follow PEP 8.
-   Use 4 spaces for indentation.
-   Maximum line length: 88 characters.
-   Use type hints where practical.
-   Keep imports grouped:
    1.  Standard library
    2.  Third-party packages
    3.  Local imports

Example:

``` python
from datetime import date

from django.shortcuts import render

from lectures.models import Lecture
```

------------------------------------------------------------------------

# 5. Naming Conventions

## Files

-   snake_case.py

## Classes

-   PascalCase

Example:

``` text
LectureTopic
ProgressService
```

## Functions

-   snake_case()

Example:

``` python
def import_routine():
    ...
```

## Variables

-   snake_case

Example:

``` python
lecture_date
subject_code
```

## Constants

UPPER_CASE

Example:

``` python
DEFAULT_PAGE_SIZE = 20
```

------------------------------------------------------------------------

# 6. Django Guidelines

-   Keep views thin.
-   Put business logic in services or model methods when appropriate.
-   Keep models focused on data.
-   Use Django ORM instead of raw SQL.
-   Prefer class-based or function-based views consistently within a
    feature.

------------------------------------------------------------------------

# 7. Templates

-   Use a shared `base.html`.
-   Reuse template partials.
-   Keep business logic out of templates.
-   Use HTMX for partial page updates where it improves the user
    experience.

------------------------------------------------------------------------

# 8. Database

-   Never modify the database directly.
-   Use Django migrations.
-   Add indexes only when justified.
-   Preserve foreign key relationships.
-   Do not duplicate stored data unnecessarily.

------------------------------------------------------------------------

# 9. Forms & Validation

-   Validate all user input.
-   Display clear error messages.
-   Never trust uploaded CSV data.
-   Reject invalid imports rather than partially importing data.

------------------------------------------------------------------------

# 10. Error Handling

-   Fail safely.
-   Return meaningful error messages.
-   Log unexpected exceptions.
-   Avoid exposing internal errors to users.

------------------------------------------------------------------------

# 11. Git Workflow

Branch names:

``` text
feature/dashboard
feature/csv-import
fix/progress
docs/database
```

Commit messages:

``` text
Add lecture topic importer
Fix dashboard progress calculation
Update database documentation
```

Each commit should represent one logical change.

------------------------------------------------------------------------

# 12. Testing

Test every new feature.

Minimum areas:

-   Models
-   CSV import
-   Progress updates
-   Dashboard calculations
-   Reminder logic

Fix failing tests before adding new features.

------------------------------------------------------------------------

# 13. Documentation

-   Document non-obvious logic.
-   Keep README updated.
-   Update design documents if architecture changes.
-   Remove outdated comments.

Comments should explain **why**, not **what**.

------------------------------------------------------------------------

# 14. Dependencies

Before adding a package:

-   Check if Django already provides the feature.
-   Prefer mature, well-maintained libraries.
-   Avoid unnecessary dependencies.

Keep the dependency list small.

------------------------------------------------------------------------

# 15. Security

-   Never commit secrets.
-   Store configuration in environment variables.
-   Validate uploaded files.
-   Escape template output where appropriate.
-   Follow Django security best practices.

------------------------------------------------------------------------

# 16. Performance

-   Optimize only after measuring.
-   Avoid unnecessary database queries.
-   Use `select_related()` and `prefetch_related()` when appropriate.
-   Keep pages responsive.

------------------------------------------------------------------------

# 17. Version 1 Constraints

Do not introduce:

-   Microservices
-   Redis
-   Celery
-   Complex caching
-   Generic repository patterns
-   Premature abstractions

Keep the architecture simple.

------------------------------------------------------------------------

# 18. Definition of Done

A task is complete when:

-   Code works as intended.
-   Code follows these standards.
-   Tests pass.
-   No obvious bugs remain.
-   Documentation is updated if needed.
-   Changes are committed with a clear message.

------------------------------------------------------------------------

# 19. Final Principles

-   Simplicity over complexity.
-   Consistency over personal preference.
-   Maintainability over shortcuts.
-   Working software over unnecessary features.
