from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models

from teamwork_hub import settings


class Direction(models.Model):
    DIRECTIONS = [
        ("frontend", "Frontend"),
        ("backend", "Backend"),
        ("design", "Design"),
        ("management", "Project Management"),
        ("qa", "Quality Assurance"),
        ("lead", "Team Lead")
    ]
    direction = models.CharField(max_length=30)

    def __str__(self):
        return self.direction


class TaskType(models.Model):
    name = models.CharField(max_length=55)


class Command(models.Model):
    name = models.CharField(max_length=155)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="commands_lead")
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(10)]
    )


class Worker(AbstractUser):
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True)
    command = models.ForeignKey(Command, on_delete=models.SET_NULL, null=True, related_name="workers")
    is_leader = models.BooleanField(default=False)


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=512)
    start_date = models.DateTimeField(blank=True, null=True)


class Task(models.Model):
    STATUS_CHOICES = [
        ("to_do", "To Do"),
        ("in_progress", "In Progress"),
        ("code_review", "Code Review"),
        ("done", "Already Done"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=512)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, related_name="tasks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    assigned_to = models.ForeignKey(Worker, on_delete=models.SET_NULL, default=None, null=True, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, related_name="tasks")
    deadline = models.DateField(null=True, blank=True)
    github_link = models.CharField(max_length=155, null=True, blank=True)
