"""UI consistency/accessibility tests (Milestone 11 - Design System &
UI Polish). Purely presentation-layer: no model, service, or business
logic is touched by this milestone, so these tests check markup/text,
not calculations (those remain covered by each app's existing tests).
"""

from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from core.test_utils import build_sample_dataset, create_user


class ComponentRenderingTests(TestCase):
    """Each shared component in templates/components/ renders correctly
    in isolation, independent of any page that happens to use it."""

    def test_page_header_renders_title_subtitle_and_action(self):
        html = render_to_string(
            "components/page_header.html",
            {"title": "Widgets", "subtitle": "All your widgets.", "action_label": "Refresh",
             "action_hx_get": "/widgets/refresh/", "action_hx_target": "#widgets"},
        )
        self.assertIn("Widgets", html)
        self.assertIn("All your widgets.", html)
        self.assertIn("Refresh", html)
        self.assertIn('hx-get="/widgets/refresh/"', html)

    def test_page_header_renders_plain_link_action_without_hx_get(self):
        html = render_to_string(
            "components/page_header.html",
            {"title": "Widgets", "action_label": "See more", "action_url": "/more/"},
        )
        self.assertIn('href="/more/"', html)
        self.assertNotIn("hx-get", html)

    def test_section_header_renders_count_and_sticky(self):
        html = render_to_string(
            "components/section_header.html", {"title": "Overdue", "count": 3, "sticky": True}
        )
        self.assertIn("Overdue", html)
        self.assertIn("(3)", html)
        self.assertIn("sticky", html)

    def test_metric_card_renders_value_total_and_unit(self):
        html = render_to_string(
            "components/metric_card.html",
            {"label": "Lectures", "value": 12, "total": 20, "sublabel": "completed"},
        )
        self.assertIn("Lectures", html)
        self.assertIn("12", html)
        self.assertIn("/ 20", html)
        self.assertIn("completed", html)

    def test_badge_renders_text_and_secondary(self):
        html = render_to_string(
            "components/badge.html",
            {"text": "Ready", "secondary": "92", "classes": "bg-emerald-100 text-emerald-800"},
        )
        self.assertIn("Ready", html)
        self.assertIn("92", html)
        self.assertIn("bg-emerald-100", html)

    def test_progress_bar_renders_percentage_and_label(self):
        html = render_to_string(
            "components/progress_bar.html", {"percentage": 42, "show_label": True}
        )
        self.assertIn("width: 42%", html)
        self.assertIn("42%", html)
        self.assertIn('role="progressbar"', html)

    def test_empty_state_renders_message_verbatim(self):
        # Django autoescapes the apostrophe (`&#x27;`) - correct, expected
        # behavior a browser renders back as "'"; assert against the
        # escaped form rather than the raw string.
        html = render_to_string(
            "components/empty_state.html", {"message": "You're all caught up."}
        )
        self.assertIn("You&#x27;re all caught up.", html)

    def test_filter_panel_renders_select_and_text_fields(self):
        html = render_to_string(
            "components/filter_panel.html",
            {
                "action": "/things/", "target": "#results",
                "fields": [
                    {"kind": "select", "name": "subject", "label": "Subject", "options": [("", "All"), ("P", "Physics")], "selected": "P"},
                    {"kind": "text", "name": "q", "label": "Search", "value": "vec", "placeholder": "Search..."},
                ],
            },
        )
        self.assertIn('name="subject"', html)
        self.assertIn('value="P" selected', html)
        self.assertIn('name="q"', html)
        self.assertIn('value="vec"', html)
        self.assertIn('hx-get="/things/"', html)
        self.assertIn('hx-target="#results"', html)

    def test_loading_skeleton_renders_configured_row_count(self):
        html = render_to_string("components/loading_skeleton.html", {"rows": 4})
        self.assertEqual(html.count("bg-gray-100 border"), 4)
        self.assertIn("htmx-indicator", html)


class ProgressMeterTests(TestCase):
    """Milestone 15.2, Parts 5-6 - the multi-dimensional progress
    component. Rendering adapts purely to `progress.total_units`
    (never a caller-chosen mode), per Part 5."""

    def _progress(self, topic_count, class_done=0, notes_done=0, revision_done=0, practice_done=0):
        completed = {"class_done": class_done, "notes_done": notes_done, "revision_done": revision_done, "practice_done": practice_done}
        dimensions, segments = {}, []
        for dim, meta in [
            ("class_done", ("Class", "bg-blue-500")), ("notes_done", ("Notes", "bg-emerald-500")),
            ("revision_done", ("Revision", "bg-amber-400")), ("practice_done", ("Practice", "bg-purple-500")),
        ]:
            label, color = meta
            pct = round(completed[dim] / topic_count * 100, 1) if topic_count else 0.0
            dimensions[dim] = {"label": label, "color_class": color, "completed": completed[dim], "total": topic_count, "percentage": pct}
            segments.append({"label": label, "color_class": color, "count": completed[dim], "total": topic_count, "percentage": pct})
        total_units = topic_count * 4
        completed_units = sum(completed.values())
        return {
            "topic_count": topic_count, "total_units": total_units, "completed_units": completed_units,
            "percentage": round(completed_units / total_units * 100, 1) if total_units else 0.0,
            "dimensions": dimensions, "segments": segments,
        }

    def test_small_entity_renders_individual_blocks(self):
        # 2 topics = 8 units (<=16) - Part 5's "small" tier: individual blocks.
        progress = self._progress(2, class_done=2, notes_done=1)
        html = render_to_string("components/progress_meter.html", {"progress": progress})
        self.assertEqual(html.count('<span class="rounded-sm inline-block'), 8)
        self.assertIn("bg-blue-500", html)
        self.assertIn("bg-emerald-500", html)

    def test_matches_the_specs_worked_example(self):
        # Part 3's own example: a chapter with 2 topics, 8 units total,
        # Class1/Class2/Notes1 done -> Blue Blue Green, rest empty.
        progress = self._progress(2, class_done=2, notes_done=1)
        self.assertEqual(progress["total_units"], 8)
        self.assertEqual(progress["completed_units"], 3)
        html = render_to_string("components/progress_meter.html", {"progress": progress})
        # 3 colored blocks (2 blue + 1 green), 5 empty.
        self.assertEqual(html.count("bg-blue-500"), 2)
        self.assertEqual(html.count("bg-emerald-500"), 1)
        self.assertEqual(html.count("bg-gray-200 dark:bg-slate-700"), 5)

    def test_medium_entity_uses_narrower_blocks(self):
        # 5 topics = 20 units (17-32) - Part 5's "medium" tier.
        progress = self._progress(5, class_done=3)
        html = render_to_string("components/progress_meter.html", {"progress": progress})
        self.assertIn("w-1.5", html)
        self.assertNotIn("w-3\"", html)

    def test_large_entity_renders_continuous_bar_not_dozens_of_blocks(self):
        # 9 topics = 36 units (>32) - Part 5's "large" tier: one
        # continuous 4-segment bar, never per-unit blocks.
        progress = self._progress(9, class_done=9, notes_done=4)
        html = render_to_string("components/progress_meter.html", {"progress": progress})
        self.assertEqual(html.count('<span class="rounded-sm inline-block'), 0)
        self.assertIn("width: 100.0%", html)  # class dimension, fully done

    def test_legend_optional(self):
        # tooltip=False so "Practice" can only come from the legend,
        # not a block's title attribute.
        progress = self._progress(1, class_done=1)
        without = render_to_string("components/progress_meter.html", {"progress": progress, "tooltip": False})
        with_legend = render_to_string(
            "components/progress_meter.html", {"progress": progress, "tooltip": False, "show_legend": True}
        )
        self.assertNotIn("Practice", without)
        self.assertIn("Practice", with_legend)

    def test_has_accessible_progressbar_role_and_label(self):
        progress = self._progress(1, class_done=1)
        html = render_to_string("components/progress_meter.html", {"progress": progress})
        self.assertIn('role="progressbar"', html)
        self.assertIn("aria-valuenow=", html)
        self.assertIn("1 of 4 study units complete", html)

    def test_tooltip_present_by_default(self):
        progress = self._progress(1, class_done=1)
        html = render_to_string("components/progress_meter.html", {"progress": progress})
        self.assertIn("title=", html)

    def test_tooltip_can_be_disabled(self):
        progress = self._progress(1, class_done=1)
        html = render_to_string("components/progress_meter.html", {"progress": progress, "tooltip": False})
        self.assertNotIn("title=", html)


class BaseLayoutTests(TestCase):
    """base.html's shared layout: skip link, active-nav marking,
    consistent container. Phase 2/3/10."""

    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

    def test_skip_link_present(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Skip to main content")
        self.assertContains(response, 'id="main-content"')

    def test_active_nav_link_has_aria_current(self):
        response = self.client.get(reverse("routine-list"))
        self.assertContains(response, 'aria-current="page"')

    def test_nav_marks_only_the_current_page(self):
        response = self.client.get(reverse("dashboard"))
        # Exactly one nav item should be marked current on any given page.
        self.assertEqual(response.content.decode().count('aria-current="page"'), 1)

    def test_nav_does_not_horizontally_scroll(self):
        # Milestone 15.1, Phase 2 - replaced overflow-x-auto/flex-nowrap
        # with flex-wrap so a crowded nav wraps onto another line
        # instead of scrolling.
        response = self.client.get(reverse("dashboard"))
        html = response.content.decode()
        self.assertNotIn("overflow-x-auto", html)
        self.assertNotIn("flex-nowrap", html)
        self.assertIn("flex-wrap", html)


class NavigationRedesignTests(TestCase):
    """Milestone 15.2, Part 1 - hamburger/User Menu/Staff Menu."""

    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

    def test_mobile_hamburger_present(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, 'aria-label="Menu"')

    def test_user_menu_contains_profile_and_logout(self):
        response = self.client.get(reverse("dashboard"))
        html = response.content.decode()
        self.assertIn(reverse("profile"), html)
        self.assertIn(reverse("logout"), html)

    def test_staff_menu_hidden_for_non_staff(self):
        response = self.client.get(reverse("dashboard"))
        self.assertNotContains(response, reverse("reminder-admin"))

    def test_staff_menu_shown_for_staff(self):
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, reverse("reminder-admin"))
        self.assertContains(response, ">Staff<")


class ThemeSystemTests(TestCase):
    """Milestone 15.1, Phase 9/10/11 - the Light/Dark/System selector
    is available on every page (not just Reminder pages), persists via
    localStorage (no database field), and is keyboard-accessible (a
    native <select>, not a custom widget). Milestone 15.2, Part 1
    moved it inside the header's User Menu/mobile menu (no longer a
    floating standalone control), which is why two instances now exist
    per authenticated page (desktop + mobile) with distinct ids -
    `theme_toggle.html` takes an `id` param for exactly this reason."""

    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

    def test_theme_toggle_present_on_dashboard(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, 'id="theme-select-desktop"')
        self.assertContains(response, "System")

    def test_theme_toggle_present_on_anonymous_pages_too(self):
        self.client.logout()
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'id="theme-select-anon"')

    def test_set_theme_function_defined_before_toggle_renders(self):
        response = self.client.get(reverse("dashboard"))
        html = response.content.decode()
        self.assertIn("window.setTheme", html)
        self.assertLess(html.index("window.setTheme"), html.index('id="theme-select-desktop"'))

    def test_theme_toggle_is_a_native_select_not_a_custom_widget(self):
        response = self.client.get(reverse("dashboard"))
        html = response.content.decode()
        self.assertIn('<select id="theme-select-desktop"', html)

    def test_no_database_field_for_theme(self):
        from django.contrib.auth import get_user_model
        field_names = {f.name for f in get_user_model()._meta.get_fields()}
        self.assertNotIn("theme", field_names)


class EmptyStateTests(TestCase):
    """Friendly, specific empty-state copy appears when there's nothing
    to show (Phase 6) - built against a genuinely empty dataset, not
    just an unauthenticated/missing-filter case."""

    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

    def test_revision_queue_empty_states(self):
        response = self.client.get(reverse("revision-queue"))
        self.assertContains(response, "No overdue revisions - you're on top of things.")
        self.assertContains(response, "Nothing due today.")
        self.assertContains(response, "No upcoming revisions scheduled yet.")
        self.assertContains(response, "No completed revisions yet.")

    def test_routine_timeline_empty_state(self):
        response = self.client.get(reverse("routine-list"))
        self.assertContains(response, "No lectures match these filters")

    def test_exam_timeline_empty_state(self):
        response = self.client.get(reverse("exam-timeline"))
        self.assertContains(response, "No exams match these filters")

    def test_dataset_history_empty_state(self):
        # Milestone 12, Phase 9: dataset management is staff-only now -
        # this test's user needs is_staff to reach the page at all
        # (see routines.tests_navigation.AdminVsStudentNavigationTests
        # for the permission behavior itself).
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse("dataset-history"))
        self.assertContains(response, "No dataset has been imported yet.")


class AccessibilityMarkupTests(TestCase):
    """Semantic HTML / ARIA additions that don't change behavior
    (Phase 10) - checkbox labels, table captions, progressbar roles."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_topic_checkboxes_have_aria_labels(self):
        lecture = self.data["lectures"]["p01"]
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        self.assertContains(response, "aria-label=")
        self.assertContains(response, "Class done for")

    def test_analytics_tables_have_captions(self):
        response = self.client.get(reverse("analytics-chapters"))
        self.assertContains(response, "<caption")

    def test_progress_bars_have_progressbar_role(self):
        response = self.client.get(reverse("progress-overview"))
        self.assertContains(response, 'role="progressbar"')


class NoLeakedTemplateCommentsTests(TestCase):
    """Milestone 11.1 incident: every `templates/components/*.html` file
    opened with a multi-line `{# ... #}` docstring comment. Django's
    shorthand `{# #}` comment tag cannot span multiple lines - if it
    does, Django silently emits it as literal text instead of raising a
    syntax error, so this reached real page output for weeks before
    anyone caught it (`{% comment %}...{% endcomment %}` was the fix -
    that block form has no such restriction). This guards against the
    same mistake recurring in any future component."""

    def setUp(self):
        self.data = build_sample_dataset()
        # Staff, so the Datasets pages checked below (staff-only since
        # Milestone 12, Phase 9) are actually reached rather than
        # trivially "passing" via a 403 that never renders their templates.
        self.data["user"].is_staff = True
        self.data["user"].save()
        self.client.force_login(self.data["user"])

    def test_no_page_leaks_a_django_comment_marker(self):
        urls = [
            reverse("dashboard"), reverse("routine-list"), reverse("exam-timeline"),
            reverse("revision-queue"), reverse("progress-overview"),
            reverse("analytics-subjects"), reverse("analytics-insights"),
            reverse("dataset-history"), reverse("dataset-compare"),
        ]
        for url in urls:
            response = self.client.get(url)
            html = response.content.decode()
            self.assertNotIn("{#", html, f"{url} leaked a Django comment marker")
            self.assertNotIn("#}", html, f"{url} leaked a Django comment marker")

    def test_no_component_template_has_a_multiline_comment_tag(self):
        """Static check independent of any page actually rendering the
        component - catches the mistake at the template-source level,
        before it ever reaches a browser."""
        components_dir = Path(settings.BASE_DIR) / "templates" / "components"
        offenders = []
        for path in components_dir.glob("*.html"):
            text = path.read_text(encoding="utf-8")
            start = text.find("{#")
            if start == -1:
                continue
            end = text.find("#}", start)
            if end != -1 and "\n" in text[start:end]:
                offenders.append(path.name)
        self.assertEqual(offenders, [], f"Multi-line {{# #}} comment(s) found in: {offenders}")


class CompiledCSSTests(TestCase):
    """Milestone 11.1 incident: the compiled Tailwind stylesheet was
    never rebuilt after Milestone 1's initial `tailwind install` -
    every class added in Milestones 2-11 was silently missing from the
    shipped CSS, so every page rendered as unstyled HTML despite every
    other automated test passing (the Django test client never loads
    CSS, so nothing caught this). This is not a test of Tailwind itself -
    it verifies our own build output actually contains what our
    templates need, so a stale/incomplete build fails loudly instead of
    silently.
    """

    REQUIRED_UTILITIES = [
        ".bg-white{", ".bg-slate-900{", ".border{", ".border-gray-200{",
        ".rounded-lg{", ".p-4{", ".px-4{", ".py-2{", ".text-gray-900{",
        ".text-gray-500{", ".text-blue-600{", ".grid{", ".gap-4{",
        "hover\\:bg-slate-800", "focus-visible\\:ring-2",
        # Milestone 12's sticky workspace layout (Phase 1) - added here
        # specifically because this exact class of bug (new classes
        # used in templates, stale compiled CSS) recurred once already
        # during Milestone 12's own development.
        ".sticky{", ".top-14{", ".top-36{",
        # Milestone 13's past-day dimming (Phase 5).
        ".opacity-75{",
        # Milestone 13's table/list-row hover state (Phase 9).
        "hover\\:bg-gray-50",
        # Milestone 15.1's nav-wrap fix (Phase 2) and global dark mode
        # (Phase 9/10) - `dark:` utilities only activate via the
        # `.dark` class (theme/static_src/src/styles.css's
        # `@custom-variant dark`), so a stale build would silently
        # leave every page unstyled in dark mode specifically, with
        # every *other* CSS test still passing (light mode unaffected).
        ".flex-wrap{", "dark\\:bg-slate-800", "dark\\:bg-slate-900",
        "dark\\:text-gray-100", "dark\\:border-slate-700",
        # Milestone 15.2 - the Progress Component's fixed dimension
        # colors (Part 2's permanent Class/Notes/Revision/Practice
        # palette), the analytics segmented tabs' active-chip shadow,
        # and the mobile nav hamburger's marker-hiding utility.
        ".bg-blue-500{", ".bg-purple-500{", ".bg-amber-400{", ".shadow-sm{",
        "w-1\\.5{",
    ]

    def test_compiled_stylesheet_contains_required_utilities(self):
        css_path = Path(settings.BASE_DIR) / "theme" / "static" / "css" / "dist" / "styles.css"
        self.assertTrue(
            css_path.exists(),
            "Compiled Tailwind CSS not found at theme/static/css/dist/styles.css - "
            "run `npm run build` inside theme/static_src/ before testing/deploying.",
        )
        css = css_path.read_text(encoding="utf-8")
        missing = [cls for cls in self.REQUIRED_UTILITIES if cls not in css]
        self.assertEqual(
            missing, [],
            "Compiled Tailwind CSS is missing utilities the templates require: "
            f"{missing}. The build is stale or template scanning is broken - "
            "run `npm run build` inside theme/static_src/ and re-check.",
        )

    def test_compiled_stylesheet_is_not_trivially_small(self):
        """A style sheet built from only the unused django-tailwind demo
        template (the exact failure mode this milestone fixed) is a few
        KB; a real build covering this app's ~50 templates is tens of KB
        even minified. Catches a stale/near-empty build without hardcoding
        an exact byte count that would break on legitimate content changes."""
        css_path = Path(settings.BASE_DIR) / "theme" / "static" / "css" / "dist" / "styles.css"
        if not css_path.exists():
            self.skipTest("styles.css missing - covered by test_compiled_stylesheet_contains_required_utilities")
        size = css_path.stat().st_size
        self.assertGreater(
            size, 15_000,
            f"Compiled styles.css is only {size} bytes - likely a stale/incomplete build "
            "(the demo-only build that caused this milestone was ~5.8 KB).",
        )


class SmartBackComponentTests(TestCase):
    """Milestone 12, Phase 7: components/smart_back.html - always
    renders a real fallback link (works with JS disabled / on a direct
    page load), plus the script that prefers real browser history when
    one exists. Nothing here touches the database."""

    def test_renders_fallback_link_and_label(self):
        html = render_to_string(
            "components/smart_back.html", {"fallback_url": "/routine/", "label": "Routine"}
        )
        self.assertIn('href="/routine/"', html)
        self.assertIn("Routine", html)
        self.assertIn("history.back()", html)

    def test_defaults_to_back_label(self):
        html = render_to_string("components/smart_back.html", {"fallback_url": "/routine/"})
        self.assertIn("Back", html)

    def test_appears_on_lecture_subject_chapter_exam_and_routine_week_pages(self):
        data = build_sample_dataset()
        self.client.force_login(data["user"])
        lecture = data["lectures"]["p01"]
        subject = data["subject_p"]
        chapter = data["chapters"]["p11"]
        exam = data["exams"]["we01"]

        for url in (
            reverse("lecture-detail", args=[lecture.lecture_code]),
            reverse("subject-detail", args=[subject.pk]),
            reverse("chapter-detail", args=[chapter.pk]),
            reverse("exam-detail", args=[exam.pk]),
        ):
            response = self.client.get(url)
            self.assertContains(response, "smart-back-link", msg_prefix=f"missing on {url}")


class WorkspaceLayoutTests(TestCase):
    """Milestone 12, Phase 1/11: Routine/Exam/Revision share the same
    sticky toolbar wrapper (`{% workspace_toolbar_classes %}`) - one
    definition, not three copies."""

    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

    def test_workspace_toolbar_classes_tag_renders_sticky_position(self):
        for url in (reverse("routine-list"), reverse("exam-timeline"), reverse("revision-queue")):
            response = self.client.get(url)
            self.assertContains(response, "sticky top-14", msg_prefix=f"missing sticky toolbar on {url}")


class CardAndBadgeConsistencyTests(TestCase):
    """Milestone 13, Phase 3/4: one canonical card wrapper and one
    canonical status-color mapping, both driven by
    core/templatetags/ui_tags.py, not hand-picked per page."""

    def test_card_classes_tag_default_and_dense(self):
        from django.template import Context, Template

        template = Template("{% load ui_tags %}{% card_classes %}|{% card_classes 'dense' %}")
        normal, dense = template.render(Context({})).split("|")
        self.assertIn("p-4", normal)
        self.assertIn("p-3", dense)
        self.assertIn("bg-white border border-gray-200 rounded-lg", normal)
        self.assertIn("bg-white border border-gray-200 rounded-lg", dense)

    def test_card_classes_variants(self):
        # Milestone 15.2, Part 9 - three reusable card variants.
        from django.template import Context, Template

        template = Template(
            "{% load ui_tags %}"
            "{% card_classes variant='primary' %}|"
            "{% card_classes variant='secondary' %}|"
            "{% card_classes variant='metric' %}"
        )
        primary, secondary, metric = template.render(Context({})).split("|")
        self.assertIn("bg-white", primary)
        self.assertIn("bg-gray-50", secondary)
        self.assertIn("bg-white", metric)
        self.assertIn("dark:bg-slate-900", secondary)

    def test_status_badge_classes_tag_covers_every_variant(self):
        from django.template import Context, Template

        template = Template(
            "{% load ui_tags %}"
            "{% status_badge_classes 'positive' %}|"
            "{% status_badge_classes 'warning' %}|"
            "{% status_badge_classes 'danger' %}|"
            "{% status_badge_classes 'info' %}|"
            "{% status_badge_classes 'neutral' %}"
        )
        positive, warning, danger, info, neutral = template.render(Context({})).split("|")
        self.assertIn("emerald", positive)
        self.assertIn("amber", warning)
        self.assertIn("red", danger)
        self.assertIn("blue", info)
        self.assertIn("gray", neutral)

    def test_unknown_variant_falls_back_to_neutral(self):
        from django.template import Context, Template

        template = Template("{% load ui_tags %}{% status_badge_classes 'not-a-real-variant' %}")
        self.assertIn("gray", template.render(Context({})))


class RevisionUpcomingBadgeRegressionTests(TestCase):
    """Milestone 13: the Revision Queue's "Upcoming" section badge used
    `text="due "|add:schedule.due_date|stringformat:"s"` - Django's
    `add` filter can't concatenate a string with a date object (it
    silently returns '' rather than raising), so this badge rendered
    completely empty in production. Caught during this milestone's
    badge-consistency audit, not by any prior test - none of them
    asserted on the *content* of the Upcoming badge, only that the
    section rendered. Fixed by using badge.html's `text`/`secondary`
    parameters instead of filter concatenation (the same fix already
    applied once before - see Milestone 11's Architectural Decisions)."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_upcoming_revision_badge_shows_due_date_not_empty(self):
        from django.utils import timezone

        from progress.models import RevisionSchedule
        from progress.services.revision import Level

        lecture = self.data["lectures"]["p01"]
        due_date = timezone.localdate() + timedelta(days=30)
        RevisionSchedule.objects.create(
            user=self.data["user"], lecture=lecture, revision_level=Level.FIRST, due_date=due_date,
        )
        response = self.client.get(reverse("revision-queue"))
        from django.template.defaultfilters import date as date_filter

        # Django's default date rendering ("Aug. 24, 2026"), not the raw
        # ISO string - this is what badge.html's `{{ secondary }}`
        # (no explicit |date: filter) actually produces.
        expected_fragment = f"Due &middot; {date_filter(due_date)}</span>"
        self.assertContains(response, expected_fragment)
        # The old bug rendered a completely empty badge - guard against
        # that exact regression explicitly.
        self.assertNotIn('font-medium bg-blue-100 text-blue-800"></span>', response.content.decode())
