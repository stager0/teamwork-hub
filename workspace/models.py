from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
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

    def __str__(self):
        return self.name


class Command(models.Model):
    name = models.CharField(max_length=155)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="commands_lead")
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(10)]
    )

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True)
    command = models.ForeignKey(Command, on_delete=models.SET_NULL, null=True, related_name="workers")
    is_leader = models.BooleanField(default=False)


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=512)
    start_date = models.DateField(blank=True, null=True)
    command = models.ForeignKey(Command, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title} {self.description} {self.start_date}"


class Task(models.Model):
    class StageOfExecution(models.IntegerChoices):
        TWENTY_FIVE = 25, '25%'
        FIFTY = 50, '50%'
        SEVENTY_FIVE = 75, '75%'
        ONE_HUNDRED = 100, '100%'


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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="To Do")
    stage_of_execution = models.IntegerField(
        choices=StageOfExecution.choices,
        default="25",
        null=True,
    )
    execution_status = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ], default="0", null=True
    )
    assigned_to = models.ForeignKey(Worker, on_delete=models.SET_NULL, default=None, null=True, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, related_name="tasks")
    deadline = models.DateField(null=True, blank=True)
    github_link = models.CharField(max_length=155, null=True, blank=True)
    link_to_solution = models.TextField(max_length=512, null=True)


class Archive(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    end_date = models.DateField(auto_now_add=True, null=True)


