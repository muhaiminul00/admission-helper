# Product Requirements Document (PRD)

**Project:** Varsity Admission Tracker\
**Version:** 1.1

## 1. Introduction

Varsity Admission Tracker is a personal web application for managing
Bangladesh university admission preparation based on coaching routines.
It answers: 1. What do I have today? 2. What should I study next? 3. How
far have I progressed?

## 2. Scope (MVP)

-   Dashboard
-   Subject & chapter tracking
-   Lecture tracking
-   Progress tracking
-   CSV routine import
-   Exam management
-   Email reminders

## 3. Problem Statement

Students forget classes, exams, notes, revisions, and coaching lectures
rarely align with textbook chapters. The app bridges lecture-based
coaching and chapter-based books.

## 4. Product Goals

-   Prevent missed classes/exams
-   Organize study around lectures
-   Auto-calculate chapter progress
-   Minimize manual work
-   Keep the app simple

## 5. Non-Goals

-   AI features
-   Analytics
-   Mobile app
-   PDF parsing
-   Messaging integrations
-   Calendar sync

## 6. Product Philosophy

-   Admission syllabus is permanent.
-   Coaching routines are temporary.
-   Routine is the scheduling source.
-   Minimal manual work.
-   Progress is tracked per lecture topic.
-   Separate permanent data (Subjects, Chapters) from temporary data
    (Routines, Lectures, Exams).

## 7. Core Concepts

### Static Data

Subjects and Chapters.

### Dynamic Data

Lectures, Lecture Topics and Exams.

### Progress

Each lecture topic tracks: - Class - Notes - Revision - Practice

## 8. User Workflow

1.  Configure syllabus.
2.  Prepare predefined CSV files.
3.  Upload CSVs.
4.  Validate data.
5.  Import lectures, topics and exams.
6.  Dashboard updates.
7.  Update progress daily.

## 9. MVP Features

-   Dashboard
-   Subject Page
-   Lecture Page
-   Email Reminders
-   CSV Import

## 10. Functional Requirements

### FR-01 Dashboard

Show today's classes, exams, pending work and Continue Studying.

### FR-02 Subject Page

Display chapter cards with automatically calculated progress.

### FR-03 Lecture Page

Display lecture topics with independent progress.

### FR-04 Reminder System

Support daily, weekly and monthly email reminders.

### FR-05 CSV Import

Import: - routine.csv - lecture_topics.csv - exams.csv

Validate relationships before saving.

### FR-06 Progress Tracking

Progress belongs to lecture topics. Chapter progress is calculated
automatically.

## 11. Constraints & Assumptions

-   Personal project
-   Single primary user
-   Static syllabus
-   Email notifications only
-   Only predefined CSV templates accepted
-   PDFs converted externally
-   No manual chapter progress editing
-   Lecture-topic mapping comes from CSV

## 12. Data Ownership

### Source Data

-   routine.csv
-   lecture_topics.csv
-   exams.csv

### Application Data

-   Progress
-   Completion timestamps
-   Reminder history

Application can always be rebuilt by re-importing CSV files.

## 13. Success Criteria

-   Daily usage
-   No missed classes
-   No missed exams
-   Pending work immediately visible
-   New routine imported in under five minutes

## 14. Future Vision

AI recommendations, analytics, mobile app, PDF extraction, calendar
sync.

## 15. Design Principles

Simple. Fast. Focused. Reliable.

> Does this help today's preparation?
