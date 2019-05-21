from django.contrib import admin
from todo.models import Task, TaskList, Comment, Message, MessageGroup


class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "task_list", "completed", "priority", "due_date")
    list_filter = ("task_list",)
    ordering = ("priority",)
    search_fields = ("name",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "date", "snippet")


admin.site.register(TaskList)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Message)
admin.site.register(MessageGroup)
