from django.contrib import admin

from workspace.models import Worker, Direction, Archive, Project, TaskType, Task, Command

# Register your models here.

admin.site.register(Direction)

admin.site.register(TaskType)

@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ("task", "worker", "project", "end_date")
    ordering = ("end_date",)
    search_fields = ("project",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "start_date", "command",)
    ordering = ("start_date",)
    search_fields = ("title",)
    list_filter = ("command",)


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display =  ("username", "first_name", "last_name", "email", "direction", "command", "is_leader")
    search_fields = ("username",)
    ordering = ("username",)
    list_filter = ("direction",)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "status", "task_type", "project", "assigned_to", "execution_status", "stage_of_execution", "created_at", "deadline", "link_to_solution")
    search_fields = ("title", "stage_of_execution",)
    ordering = ("created_at",)
    list_filter = ("status",)

@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_at", "leader",)
    ordering = ("created_at",)
    search_fields = ("name",)
    list_filter = ("name",)
