# Known Issues

Deliberately deferred polish and open items as of v1.0.0. None of
these block release - each is a documented, bounded scope decision (see
`PROJECT_PROGRESS.md` for the full reasoning behind each one) rather
than an unnoticed gap. These should become individual GitHub issues
once the repository is public, not be worked in bulk.

## UI / Responsive

- **Navigation on medium-width screens hasn't been manually verified
  across every real device/browser combination.** The header switches
  from a full horizontal row to a single hamburger menu at Tailwind's
  `sm` breakpoint (640px); worth a dedicated pass on tablet-width
  viewports (640-1024px) to confirm the Staff Menu/User Menu dropdowns
  never crowd the main nav row before filing this as resolved.
- **Responsive header refinement** - the header is functional and
  tested at the breakpoint boundaries Tailwind provides, but hasn't
  had a dedicated design pass at every intermediate width.
- **Additional dashboard spacing polish** - the Dashboard widgets
  section works but wasn't given the same close spacing/hierarchy
  pass Milestone 15.2 gave Progress/Subject/Chapter/Analytics pages.
- **Minor dark mode refinements** - dark mode covers every shared
  component and template tag (Milestones 15.1/15.2), but any page
  markup that still hand-writes its own literal Tailwind color classes
  instead of going through a shared component will render light-only
  until migrated - see "Dark mode coverage" below.
- **Numeric table columns aren't right-aligned** (Milestone 13) -
  reviewed and deliberately not swept in; every table's primary
  numeric indicator (completion percentage) already flows through the
  progress meter's own layout. Worth a focused table-polish pass if
  ever prioritized.

## Dark Mode Coverage

Dark mode follows the Shared Component Rule, not a full page-by-page
sweep (Milestones 15.1/15.2): every file in `templates/components/`
and every `core.templatetags.ui_tags` function has `dark:` variants,
which covers most of the app since Milestone 13 already consolidated
most styling onto them. Any page that still hand-writes its own
`bg-white`/`text-gray-900`/etc. instead of using a shared component
will render light-only in dark mode until migrated onto the shared
system - the correct fix is migrating that page onto shared
components, not hand-patching `dark:` classes onto page-specific
markup.

## Reminders

- **No scheduler is configured yet.** The five `send_*` management
  commands exist and are scheduler-agnostic by design, but nothing
  currently invokes them on a cron-like cadence in production - this
  is an operational deployment step (see `docs/Deployment.md`, Section
  6), not a code change.
- **Exam-day/Daily-Agenda time gates are server-local time, not
  per-user.** `NotificationPreference.timezone` is captured and
  validated (a searchable IANA dropdown, Milestone 15.1) but no
  trigger condition reads it yet - every date/time comparison still
  uses the server's configured `TIME_ZONE`, matching every other date
  calculation in this app.
- **No unsubscribe-all / one-click-disable link inside the emails
  themselves** - turning a reminder type off requires visiting
  Notification Preferences while logged in. Acceptable for this
  project's single/few-user scope; would need a signed-token link for
  a multi-tenant product.
- **The Reminder Test Center's recipient selector is a plain
  `<select>` of every active user** - fine for a handful-to-dozens of
  users, would need a real filterable/paginated widget at a much
  larger user base.

## Deployment / Operations

- **Media persistence in production is the deployment platform's
  responsibility, not this codebase's** - the Routine Archive's
  `media/routines/` folder needs a persistent/attached disk on
  Render/Railway or an uploaded PDF disappears on the next redeploy.
- **No GitHub Actions caching for `pip`/`npm`** - `ci.yml` reinstalls
  both dependency sets from scratch on every run. Acceptable for this
  project's CI cadence; worth adding `actions/cache` if CI runtime
  ever becomes a real friction point.

## Component Hygiene

- **`templates/components/auth_card.html` is unused dead code** - it
  exists (presumably intended for Login/Register) but neither template
  ever adopted it; both still hand-roll their own card markup. Left
  as-is rather than restructure two auth-flow templates this late
  before release - a future pass should either adopt it or delete it.
- **`card_classes()`'s "dense"/"normal" density split is informal, not
  enforced** - nothing catches a future page hand-writing `p-4`/`p-3`
  instead of using the tag (no lint rule exists for this project's
  templates).

## Not Tracked Here

Anything already resolved is documented in `CHANGELOG.md`'s "Fixed"
section, not repeated in this file. Anything explicitly out of scope
for v1.0.0 (multi-user support beyond simple per-user data isolation,
PDF text parsing, a mobile app, a calendar view) is documented in the
README's "Version 1 Scope" section, not here - those aren't bugs or
deferred polish, they were never in scope.
