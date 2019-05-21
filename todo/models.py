from __future__ import unicode_literals
import datetime

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
from django.utils import timezone


class TaskList(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(default="")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now, blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    archive_project = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Task Lists"

        # Prevents (at the database level) creation of two lists with the same slug in the same group
        unique_together = ("group", "slug")



class Task(models.Model):
    title = models.CharField(max_length=140)
    task_list = models.ForeignKey(
        TaskList, on_delete=models.CASCADE, null=True)
    created_date = models.DateField(
        default=timezone.now, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="todo_created_by", on_delete=models.CASCADE
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="todo_assigned_to",
        on_delete=models.CASCADE,
    )
    note = models.TextField(blank=True, null=True)
    priority = models.PositiveIntegerField()

    # Has due date for an instance of this object passed?
    def overdue_status(self):
        "Returns whether the Tasks's due date has passed or not."
        if self.due_date and datetime.date.today() > self.due_date:
            return True

    def __str__(self):
        return self.title



    def get_absolute_url(self):
        return reverse("todo:task_detail", kwargs={"task_id": self.id})

    # Auto-set the Task creation from datetime / completed date
    def save(self, **kwargs):
        # If Task is being marked complete, set the completed_date
        if self.completed:
            self.completed_date = datetime.datetime.now()
        super(Task, self).save()

    class Meta:
        ordering = ["priority"]

    @property
    def get_html_url(self):
        url = reverse('todo:task_detail', args=(self.id,))
        return f'<a href="{url}"> {self.title} (End) </a>'


class Comment(models.Model):
    """
    Not using Django's built-in comments because we want to be able to save
    a comment and change task details at the same time. Rolling our own since it's easy.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    body = models.TextField(blank=True)

    def snippet(self):
        # Define here rather than in __str__ so we can use it in the admin list_display
        return "{author} - {snippet}...".format(author=self.author, snippet=self.body[:35])

    def __str__(self):
        return self.snippet()

# Message Handle


class MessageGroup(models.Model):
    name = models.CharField(max_length=140)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL)

    def latest_message(self):
        if self.messages.count() == 0:
            return None
        return self.messages.order_by('-date').first()

    def combined_names(self, full=False):
        names_count = self.members.count()
        extras = names_count - 3
        members = self.members.all()
        if not full:
            members = members[:3]
        names = ", ".join([m.get_full_name() for m in members])
        if extras > 0 and not full:
            names += " and %d other%s" % (extras, "" if extras == 1 else "s")
        return names


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    group = models.ForeignKey(
        MessageGroup, related_name='messages', on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField()
    read_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='read_messages')

    def preview_text(self):
        return (self.body[:100] + "...") if len(self.body) > 100 else self.body
