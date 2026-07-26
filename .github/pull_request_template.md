## Summary

What does this PR change, and why?

## Branch Type

- [ ] `feature/*` (branched from `develop`)
- [ ] `bugfix/*` (branched from `develop`)
- [ ] `hotfix/*` (branched from `main` - production-breaking issue only)
- [ ] `release/*` (branched from `develop`, final stabilization only)

See `docs/GitWorkflow.md` if you're unsure which applies.

## Checklist

- [ ] `python manage.py test` passes locally.
- [ ] `python manage.py check` passes locally.
- [ ] `python manage.py makemigrations --check --dry-run` reports no
      changes (or a migration is included in this PR).
- [ ] `npm run build` re-run in `theme/static_src/` if any template
      changed (new Tailwind classes need a rebuilt, committed-nowhere
      but CI-verified stylesheet).
- [ ] `CHANGELOG.md` updated if this is user-facing.
- [ ] `PROJECT_PROGRESS.md` updated if this changes architecture.
- [ ] No direct commits to `main` - this PR targets `develop` (or
      `main`, for a `hotfix/*` only).

## Related Issues

Closes #
