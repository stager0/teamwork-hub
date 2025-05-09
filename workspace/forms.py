from click import command
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

from workspace.models import Command, Direction, Task, Project


class WorkerCreationForm(UserCreationForm):
    DIRECTION_CHOICES = [
        ("frontend", "Frontend"),
        ("backend", "Backend"),
        ("design", "Design"),
        ("management", "Project Management"),
        ("qa", "Quality Assurance"),
        ("lead", "Team Lead")
    ]
    direction = forms.ModelChoiceField(
        required=True,
        queryset=Direction.objects.all(),
        empty_label="Chose your direction"
    )
    command_code = forms.CharField(
        label="Command Code",
        min_length=10,
        max_length=10,
        required=True,
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "first_name", "last_name", "email", "password1", "password2", "direction", "command_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Repeat Password"
        self.fields["last_name"].widget.attrs["placeholder"] = "Last Name"
        self.fields["first_name"].widget.attrs["placeholder"] = "First Name"
        self.fields["command_code"].widget.attrs["placeholder"] = "TeamCode (length - 10)"
        self.fields["direction"].widget.attrs["placeholder"] = "Direction"
        self.fields["email"].widget.attrs["placeholder"] = "Email"

    def save(self, commit=True):
        worker = super().save(commit=False)
        direction_name = self.cleaned_data["direction"]
        code = self.cleaned_data["command_code"]

        direction_object = Direction.objects.get(
            direction=direction_name
        )
        worker.direction = direction_object

        command, created = Command.objects.get_or_create(
            code=code,
        )
        worker.command = command
        worker.is_leader = created

        if commit:
            worker.save()

        if created:
            command.name = "New Command"
            command.leader_id = worker
            command.save()

        return worker


class WorkerLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["password"].widget.attrs["placeholder"] = "Password"


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "first_name", "last_name", "email", "direction"]


class ProjectsTitleSearchForm(forms.Form):
    title = forms.CharField(
        max_length=55,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "style": "width: 400px; height: 40px",
                "placeholder": "Search by title"
            }
        )
    )


class ProjectListCreationForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "start_date", "command"]



class TaskCreationForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["project", "title", "description", "task_type", "assigned_to", "direction", "deadline", "github_link"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["assigned_to"].queryset = get_user_model().objects.filter(command__code=user.command.code)
            self.fields["assigned_to"].required = False



class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["project", "title", "description", "task_type", "direction", "deadline", "github_link"]


class TaskChangeExecutionForm(forms.ModelForm):
    link_to_solution = forms.URLField(
        required=False,
        label="Enter a link to solution",
        widget=forms.URLInput(
            attrs={"placeholder": "https://github.com"}
        )
    )

    class Meta:
        model = Task
        fields = ["execution_status", "link_to_solution"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["execution_status"].widget.attrs["placeholder"] = "Enter new execution status"

    def save(self, commit=True):
        task = super().save(commit=False)

        if int(task.execution_status) == 100:
            task.status = "code_review"
            task.stage_of_execution = 75

        link = self.cleaned_data["link_to_solution"]
        if link:
            task.link_to_solution = link

        if commit:
            task.save()
        return task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["project", "title", "description", "task_type", "direction", "deadline", "github_link"]


class TaskLinkForm(forms.ModelForm):
    link = forms.URLField(
        label="Enter a Link",
        widget=forms.URLInput(
            attrs={"placeholder": "https://github.com"}
        )
    )
