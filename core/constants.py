from django.utils.translation import gettext_lazy as _


class Messages:
    PASSWORD_MISMATCH_ERROR = _("The two password fields didn't match.")
    CANNOT_CREATE_USER_ERROR = _("Unable to create account.")
    INVALID_PASSWORD_ERROR = _("Invalid password.")
    EMAIL_NOT_FOUND = _("User with given email does not exist.")
    INVALID_TOKEN_ERROR = _("Invalid token for given user.")
    INVALID_UID_ERROR = _("Invalid user id or user doesn't exist.")
