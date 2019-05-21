from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from todo.models import MessageGroup, Message
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import dateparse
import datetime
import time
from django.utils import timezone
from todo.utils import addition


@login_required
def add_group(request):
    message = None
    if request.POST:
        group, message = handle_add_group_form(request, request.POST)
        if group:
            addition(request, group)
            return redirect('todo:conversation', group.pk)
    return messages(request, error=message)


def handle_add_group_form(request, body):
    name = body.get('name')
    recipient_ids = body.getlist('recipient')
    message = body.get('message')

    if not all([name, recipient_ids, message]):
        return None, "All fields are required."
    if not [r for r in recipient_ids if r.isdigit()]:
        return None, "Invalid recipient."
    group = MessageGroup.objects.create(
        name=name
    )
    try:
        ids = [int(r) for r in recipient_ids]
        recipients = User.objects.filter(pk__in=ids)
    except User.DoesNotExist:
        return None, "Could not find user."
    group.members.add(request.user)
    for r in recipients:
        group.members.add(r)
    group.save()
    Message.objects.create(sender=request.user, body=message,
                           group=group, date=timezone.now())
    return group, None
