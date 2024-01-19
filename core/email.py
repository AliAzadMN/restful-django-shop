from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage

from .utils import encode_uid


class PasswordResetEmail(BaseEmailMessage):
    template_name = "email/password_reset.html"

    def get_context_data(self, **kwargs):
        PASSWORD_RESET_CONFIRM_URL = "#/password-reset/{uid}/{token}"
        
        context = super().get_context_data()
        user = context.get("user")

        context["uid"] = encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = PASSWORD_RESET_CONFIRM_URL.format(**context)
        return context
    