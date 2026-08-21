"""Shared UI class-string helpers (Milestone 11 - Design System).

Small `simple_tag`s that return canonical Tailwind class strings for
interactive elements repeated across many templates (buttons, form
inputs). These exist alongside `templates/components/` for the cases
that don't fit an includable component - a `<button>`'s classes need
to combine with page-specific `hx-*` attributes that vary per call
site, so a plain class-string tag is simpler than an include here.
Keeping the string in one place means every button/input across the
app looks and focuses identically without copy-pasting a long
Tailwind class list into dozens of templates.
"""

from django import template

register = template.Library()

BUTTON_VARIANTS = {
    "primary": "bg-accent text-accent-ink hover:bg-accent-strong focus-visible:ring-accent",
    "secondary": "border border-line text-ink hover:bg-surface-quiet focus-visible:ring-accent",
    "danger": "bg-danger text-danger-ink hover:opacity-90 focus-visible:ring-danger",
}

FIELD_CLASSES = (
    "border border-line bg-surface text-ink rounded px-2 py-1.5 text-sm w-full "
    "focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
)


@register.simple_tag
def button_classes(variant="secondary", size="md"):
    base = "inline-flex items-center justify-center rounded font-medium transition-colors " \
           "focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
    padding = "px-3 py-1.5 text-sm" if size == "md" else "px-4 py-2 text-sm"
    return f"{base} {padding} {BUTTON_VARIANTS.get(variant, BUTTON_VARIANTS['secondary'])}"


@register.simple_tag
def field_classes():
    return FIELD_CLASSES


@register.simple_tag
def class_if_positive(value, class_name):
    """`{% class_if_positive count "text-red-600" %}` - applies a class
    only when a count is truthy/positive, e.g. an "Overdue" metric tile
    that should only turn red once there's actually something overdue."""
    try:
        return class_name if value and value > 0 else ""
    except TypeError:
        return ""


@register.filter
def pct_color(percentage):
    """Three-tier completion color (matches the shade the Routine
    Timeline cards used before componentization): full/high/low."""
    try:
        pct = float(percentage)
    except (TypeError, ValueError):
        pct = 0
    if pct >= 100:
        return "bg-success"
    if pct >= 40:
        return "bg-accent"
    return "bg-warning"


@register.simple_tag
def times(count):
    """`{% times 3 as rows %}` then `{% for _ in rows %}` - Django
    templates have no built-in range/loop-N-times tag."""
    try:
        return range(int(count))
    except (TypeError, ValueError):
        return range(0)


STATUS_BADGE_VARIANTS = {
    "positive": "bg-success-wash text-success",
    "warning": "bg-warning-wash text-warning",
    "danger": "bg-danger-wash text-danger",
    "info": "bg-info-wash text-info",
    "neutral": "bg-surface-quiet text-ink-muted",
}


@register.simple_tag
def status_badge_classes(variant):
    """Canonical badge color for one of five semantic tiers (Milestone
    13, Phase 4 - "Better Status System"): "positive" (Done/Completed/
    Active/Exam Ready), "warning" (Pending/Due/today), "danger"
    (Overdue/Missed/In upcoming exam), "info" (Upcoming/general
    informational), "neutral" (Inactive/no status). Template-authored
    badges (status text baked into a template, not computed by a
    service) should use this instead of a hand-picked color, so
    "Pending" (for example) is never amber on one page and gray on
    another. Badges whose color is itself the *result* of a service
    calculation - `analytics.readiness_badge_class`,
    `advanced_analytics`'s confidence badges - are unaffected; this
    tag only standardizes colors chosen in templates, never business
    logic thresholds."""
    return STATUS_BADGE_VARIANTS.get(variant, STATUS_BADGE_VARIANTS["neutral"])


CARD_VARIANTS = {
    # Milestone 20 - "Indigo Study" visual identity. `surface`/`line`
    # are theme-aware tokens (styles.css), so this single class list
    # is correct in light and dark with no `dark:` sibling needed.
    "primary": "bg-surface border border-line",
    # A visually quieter surface for content nested *inside* a primary
    # card (e.g. a sub-section that shouldn't compete with the card
    # around it) - same border weight, softer fill.
    "secondary": "bg-surface-quiet border border-line",
    # Semantically distinct from "primary" for stat-tile call sites
    # (metric_card.html), even though it shares primary's surface -
    # naming the variant, not restyling it, is what Part 9 asks for.
    "metric": "bg-surface border border-line",
}


@register.simple_tag
def card_classes(density="normal", variant="primary"):
    """Canonical card wrapper classes (Milestone 13, Phase 3 - "Card
    System Refinement"; Milestone 15.2, Part 9 added `variant`; Milestone
    20 moved the surface colors onto theme-aware tokens). One definition
    for every bordered card in the app, so a future spacing/radius/
    border/surface tweak changes every card at once instead of needing
    a page-by-page sweep.

    `density` controls padding only: "normal" (p-4, the default - stat
    tiles, content sections, canonical-page boxes) or "dense" (p-3 -
    list-item-style cards where many rows stack close together, e.g.
    the Dashboard's Today's Routine list, Routine/Exam Timeline event
    cards). This is a deliberate two-tier system, not an inconsistency
    left unresolved - see PROJECT_PROGRESS.md, Milestone 13.

    `variant` controls surface: "primary" (default card), "secondary"
    (a quieter nested surface), "metric" (identical surface to
    primary, named separately so a stat-tile call site self-documents
    what kind of card it is)."""
    padding = "p-3" if density == "dense" else "p-4"
    base = CARD_VARIANTS.get(variant, CARD_VARIANTS["primary"])
    return f"{base} rounded-lg {padding}"


@register.simple_tag
def workspace_toolbar_classes():
    """Milestone 12, Phase 1/11: the sticky wrapper every workspace page
    (Routine/Exam/Revision) puts its page header + filters in, so the
    toolbar stays visible while only the timeline/queue content below it
    scrolls. `top-14` matches base.html's nav bar height (`py-3` around
    a `text-lg` logo). One definition shared by all three pages rather
    than three copies of the same class string, per Phase 11's "no
    duplicated layouts" instruction."""
    return "sticky top-14 z-20 bg-bg pt-4 pb-3 -mx-4 px-4 sm:mx-0 sm:px-0"
