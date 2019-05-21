
from django.contrib.auth import get_user_model

from django.contrib.auth.models import User, Group
from todo.models import MessageGroup, Message
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Max
from django.utils import dateparse
import datetime
import time


@login_required
def messages(request, error=None):

    recipients = User.objects.all()
    message_groups = request.user.messagegroup_set\
                            .annotate(max_date=Max('messages__date'))\
                            .order_by('-max_date').all()
    for group in message_groups:
        for message in group.messages.all():
            if request.user not in message.read_members.all():
                group.has_unread = True
                break
    context = {

        'user': request.user,
        'recipients': recipients,
        'groups': message_groups,
        'error_message': error
    }
    return render(request, 'todo/messages.html', context)
