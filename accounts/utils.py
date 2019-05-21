from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.conf import settings

class MailSend:

    def __init__(self):
        self.from_email = settings.EMAIL_HOST_USER

    def sending_mail(self, *args, **kwargs):
        subject = 'Your Subject'
        to = kwargs['to']
        from_email = self.from_email
        message = render_to_string('email/email.html', kwargs['ctx'])
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
        return 'Submitted Successfully'
