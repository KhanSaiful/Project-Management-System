
from django.contrib.auth import get_user_model
import datetime
from todo.models import MessageGroup, Message
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.utils import timezone
from todo.utils import staff_check


user = get_user_model()


@login_required
def conversation(request, id):
    group = get_object_or_404(MessageGroup, pk=id)
    context = {
        "user": request.user,
        "group": group,
        "message_names": group.combined_names(full=True)
    }
    if request.POST:
        message = request.POST.get('message')
        if message:
            msg = Message.objects.create(sender=request.user, group=group,
                                         body=message, date=timezone.now())
            group.messages.add(msg)
            group.save()
            # redirect to avoid the issues with reloading
            # sending the message again.
            return redirect('todo:conversation', group.pk)
    for message in group.messages.all():
        if request.user not in message.read_members.all():
            message.read_members.add(request.user)
            message.save()

    return render(request, 'todo/conversation.html', context)
