# UI/UX Specification

**Project:** Varsity Admission Tracker\
**Document:** 05_UI_UX_Specification.md\
**Version:** 1.0\
**Status:** Locked for Version 1

------------------------------------------------------------------------

# 1. Purpose

This document defines the user interface and user experience guidelines
for Version 1.

The objective is to create an interface that is:

-   Simple
-   Fast
-   Distraction-free
-   Consistent

The UI should help users focus on studying rather than learning how to
use the application.

------------------------------------------------------------------------

# 2. Design Principles

-   Minimal clicks
-   Clean layouts
-   Consistent components
-   Mobile-friendly
-   Fast loading
-   No unnecessary animations

------------------------------------------------------------------------

# 3. Visual Style

## Theme

-   Light theme by default
-   Soft neutral colors
-   Blue as primary action color
-   Green for completed progress
-   Orange for pending work
-   Red only for important warnings

## Typography

-   Clear sans-serif font
-   Large page titles
-   Medium section headings
-   Readable body text

## Spacing

-   Consistent spacing using a simple 8px scale
-   Cards separated with comfortable whitespace

------------------------------------------------------------------------

# 4. Layout Structure

Every page follows the same structure.

``` text
+--------------------------------------+
| Header                               |
+--------------------------------------+
| Navigation                           |
+--------------------------------------+
| Main Content                         |
|                                      |
|                                      |
+--------------------------------------+
| Footer (optional)                    |
+--------------------------------------+
```

------------------------------------------------------------------------

# 5. Navigation

Primary navigation:

-   Dashboard
-   Subjects
-   Routine
-   Exams
-   Settings

The active page should always be highlighted.

------------------------------------------------------------------------

# 6. Common Components

## Buttons

Primary - Save - Import - Continue

Secondary - Cancel - Back

Danger - Delete (future use)

------------------------------------------------------------------------

## Cards

Used for:

-   Subject
-   Chapter
-   Lecture
-   Exam
-   Dashboard summaries

Each card should contain:

-   Title
-   Status
-   Key information
-   Primary action

------------------------------------------------------------------------

## Status Badges

Possible statuses:

-   Not Scheduled
-   Scheduled
-   In Progress
-   Completed

Colors should remain consistent across the application.

------------------------------------------------------------------------

## Progress Checklist

Lecture Topics display four checkboxes:

-   Class
-   Notes
-   Revision
-   Practice

Checking a box should save immediately without requiring an extra Save
button.

------------------------------------------------------------------------

# 7. Screen Specifications

## Dashboard

Purpose:

Provide a complete overview of today's work.

Sections:

-   Today's Classes
-   Today's Exams
-   Continue Studying
-   Pending Tasks
-   Subject Progress
-   Upcoming Exams

The Dashboard is always the landing page.

------------------------------------------------------------------------

## Subjects

Display subjects as cards.

Each card shows:

-   Subject name
-   Overall progress
-   Total chapters
-   Next lecture

Selecting a card opens Subject Details.

------------------------------------------------------------------------

## Subject Details

Display chapter cards.

Each chapter card contains:

-   Chapter name
-   Status
-   Progress
-   Related lectures

------------------------------------------------------------------------

## Chapter Details

Display:

-   Chapter information
-   Related lecture topics
-   Timeline of lectures

------------------------------------------------------------------------

## Lecture Details

Primary study page.

Display:

-   Lecture code
-   Date
-   Lecture topics
-   Progress checklist

This is the only page where study progress is updated.

------------------------------------------------------------------------

## Routine

Display:

-   Current routine
-   Import CSV button
-   Previous imports

Importing should show:

-   Validation progress
-   Success summary
-   Error messages if applicable

------------------------------------------------------------------------

## Exams

Display:

-   Upcoming exams
-   Exam type
-   Date

Selecting an exam opens its details.

------------------------------------------------------------------------

## Settings

Display only:

-   Email address
-   Reminder preferences
-   Application version

Version 1 intentionally keeps this page minimal.

------------------------------------------------------------------------

# 8. User Experience Rules

-   Maximum three clicks to reach any study page.
-   Important information should be visible without scrolling where
    practical.
-   Progress updates should feel instant.
-   Error messages should clearly explain how to fix problems.
-   Empty pages should display helpful guidance.

------------------------------------------------------------------------

# 9. Responsive Design

Support:

-   Desktop
-   Tablet
-   Mobile

On smaller screens:

-   Cards stack vertically.
-   Navigation collapses into a menu.
-   Tables become card layouts where appropriate.

------------------------------------------------------------------------

# 10. Accessibility

-   Sufficient color contrast.
-   Keyboard-friendly forms.
-   Labels for all inputs.
-   Icons accompanied by text where needed.
-   Do not rely on color alone to communicate status.

------------------------------------------------------------------------

# 11. Future UI Features (Excluded)

Not included in Version 1:

-   Dark mode
-   Drag-and-drop
-   Charts
-   Calendar view
-   Advanced filters
-   Custom themes

------------------------------------------------------------------------

# 12. Design Decisions

-   Dashboard-first workflow.
-   Lecture Details is the primary action page.
-   Cards are preferred over dense tables.
-   Immediate progress saving reduces user effort.
-   Minimal settings keep maintenance simple.
-   Consistent layouts reduce learning time.
