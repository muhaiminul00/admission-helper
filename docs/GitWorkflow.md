# Git Workflow

Adopted at Milestone 15.3, ahead of the v1.0.0 release. Everything
below applies from v1.0.0 onward - history before the tag was a
single-track, milestone-by-milestone build-out and is not rewritten to
fit this model retroactively.

---

## Branches

| Branch        | Purpose                                              | Lives forever? |
| -------------- | ----------------------------------------------------- | --------------- |
| `main`         | Production-ready code only. Every commit on `main` is deployable and (after v1.0.0) corresponds to a tagged release. | Yes |
| `develop`      | Integration branch for work in progress between releases. | Yes |
| `feature/*`    | One new feature or improvement, branched from `develop`. | No - merged and deleted |
| `bugfix/*`     | A non-urgent fix, branched from `develop`.            | No - merged and deleted |
| `hotfix/*`     | An urgent production fix, branched from `main`.       | No - merged and deleted |
| `release/*`    | Final stabilization for a release (version bump, changelog, last-minute fixes only) before tagging, branched from `develop`. | No - merged and deleted |

Naming: `feature/short-description`, `bugfix/short-description`,
`hotfix/short-description`, `release/1.1.0` (version number, no `v`
prefix on the branch name - the tag itself carries the `v`).

## The Rule From v1.0.0 Onward

**Once `main` is tagged `v1.0.0`, it represents production. No direct
commits to `main`.** Every change, however small, follows:

```text
develop
   │
   ▼
feature/xyz or bugfix/xyz
   │
   ▼
Pull Request into develop
   │
   ▼
Tests pass, review, merge
   │
   ▼
(when ready to release) release/x.y.z branched from develop
   │
   ▼
Final checks (RELEASE_CHECKLIST.md), merge into main AND back into develop
   │
   ▼
Tag vX.Y.Z on main
   │
   ▼
Deploy
```

A `hotfix/*` branch is the only exception to "always branch from
`develop`" - a production-breaking bug is fixed directly against
`main`, merged into `main` (and immediately tagged, e.g. `v1.0.1`),
and then also merged into `develop` so the fix isn't lost on the next
regular release.

## Pull Requests

- Every PR targets `develop` (or `main`, for a `hotfix/*` PR only).
- Every PR must pass the full test suite and `manage.py check` before
  merge (see `.github/workflows/ci.yml`).
- Squash or merge commit, either is fine for this project's size - just
  keep `main`'s history readable.

## Tags

Tags are created only on `main`, only after `RELEASE_CHECKLIST.md` is
fully satisfied, and always follow Semantic Versioning (see
`CHANGELOG.md` for the version policy). Example:

```bash
git checkout main
git tag -a v1.0.0 -m "Version 1.0.0 - first production release"
git push origin main --tags   # once a remote exists
```

## Commit Messages

No strict format is enforced, but a commit message should say *why*,
not just *what* (this project's existing convention throughout
`PROJECT_PROGRESS.md`). Reference the milestone or issue where useful.
