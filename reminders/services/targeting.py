"""Which users a generator should consider (Milestone 15.1, Phase 5 -
Reminder Administration's recipient selector). Every generator
defaults to every active user, exactly as it did before this
milestone; `users` only ever narrows that set for a manual admin test
- it never changes *what* is due for whichever users are considered,
so generation logic itself is untouched.
"""

from django.contrib.auth import get_user_model


def target_users(users=None):
    if users is not None:
        return users
    User = get_user_model()
    return User.objects.filter(is_active=True)
