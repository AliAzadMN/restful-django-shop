from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode
from templated_mail.mail import BaseEmailMessage


def encode_uid(pk):
    return force_str(urlsafe_base64_encode(force_bytes(pk)))


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
    