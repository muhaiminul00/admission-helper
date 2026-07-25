"""The one data shape every generator in this package produces.

A `ReminderJob` describes *what* should be sent and *why* - nothing
about how it gets rendered or delivered (that's `reminders/emails/`).
Keeping generation, rendering, and delivery on three separate data/
function boundaries is what Phase 9 asks for: none of these functions
know about SMTP, and swapping the email backend never touches this
module or any generator.
"""

from dataclasses import dataclass, field


@dataclass
class ReminderJob:
    user: object
    reminder_type: str
    reference_key: str
    context: dict = field(default_factory=dict)
