from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from workspace.forms import (
    WorkerCreationForm,
    WorkerLoginForm,
    ProjectsTitleSearchForm,
    TaskCreationForm,
    TaskUpdateForm,
    ProjectListCreationForm,
    TaskChangeExecutionForm,
    TaskForm,
    TaskLinkForm,
    UserUpdateForm,
)
from workspace.models import Project, Task, Archive, Direction, Command, TaskType


User = get_user_model()


@login_required
def index(request: HttpRequest) -> HttpResponse:
    user = request.user
    context = {
        "count_of_workers": User.objects.count(),
        "count_of_projects": Project.objects.count(),
        "count_of_users_tasks": Archive.objects.filter(worker_id=user.id).count(),
    }
    return render(request, "index.html", context=context)


class CustomRegisterView(generic.CreateView):
    model = User
    form_class = WorkerCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("login")


class CustomLoginView(LoginView):
    model = User
    form_class = WorkerLoginForm
    template_name = "accounts/login.html"
    success_url = reverse_lazy("index")


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = "workspace/user_detail.html"
    context_object_name = "users"

    def get_queryset(self):
        return super().get_queryset().select_related("direction", "command")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_from_url"] = self.object
        return context


class UsersListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "workspace/users-list.html"
    context_object_name = "workers"

    def get_context_data(self):
        context = super().get_context_data()
        context["code_dict"] = {
            user.id: user.command.code
            for user in User.objects.all().select_related("command")
        }
        return context

    def get_queryset(self):
        return User.objects.all().select_related("direction", "command")


class UserTasksListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "workspace/user-tasks-list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        user_tasks_list = Task.objects.filter(assigned_to=user_id).select_related(
            "project", "assigned_to", "direction", "task_type"
        )
        return user_tasks_list.filter(execution_status__lt=100)

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_user_model().objects.get(id=self.kwargs["pk"])
        context["user"] = user
        context["archive_users_ids"] = Archive.objects.values_list(
            "worker_id", flat=True
        )
        return context


class UserUpdateView(generic.UpdateView):
    model = User
    template_name = "workspace/user_update.html"
    form_class = UserUpdateForm

    def get_queryset(self):
        return super().get_queryset().select_related("direction", "command")

    def get_success_url(self):
        return reverse("workspace:workers-list")


class ProjectsArchivedListView(LoginRequiredMixin, generic.ListView):
    model = Project
    template_name = "workspace/archived-projects.html"
    context_object_name = "projects"

    def get_queryset(self):
        archived_project_ids = Archive.objects.filter(
            task_id=None, worker_id=None
        ).values_list("project_id", flat=True)
        return Project.objects.filter(id__in=archived_project_ids)

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)
        archived_projects = Archive.objects.filter(
            task_id=None, worker_id=None
        ).select_related("project")
        context["archived_projects"] = archived_projects
        return context


class ProjectsListView(LoginRequiredMixin, generic.ListView):
    model = Project
    template_name = "workspace/projects-list.html"
    context_object_name = "projects"

    def get_queryset(self):
        user = self.request.user
        title = self.request.GET.get("title")
        archived_projects_ids = Archive.objects.filter(
            worker_id=None, task_id=None
        ).values_list("project_id", flat=True)
        queryset = (
            Project.objects.select_related("command")
            .filter(command=user.command)
            .exclude(id__in=archived_projects_ids)
        )

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.request.GET.get("title", "")
        context["form"] = ProjectsTitleSearchForm(initial={"title": title})
        user = self.request.user
        context["create_form"] = ProjectListCreationForm(
            initial={"command": user.command.name}
        )

        return context


class ProjectsDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = "workspace/projects-list-detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return super().get_queryset().select_related("command")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        archived_projects_ids = Archive.objects.filter(
            worker_id=None, task_id=None
        ).values_list("project_id", flat=True)
        context["archived_projects_ids"] = list(archived_projects_ids)
        archives = Archive.objects.filter(task_id=None, worker_id=None).select_related(
            "project"
        )
        context["archived_projects_date"] = {
            archive.project.id: archive.end_date
            for archive in archives
            if archive.project is not None
        }
        return context


class ProjectsListCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    template_name = "workspace/projects-list-form.html"
    form_class = ProjectListCreationForm

    def get_success_url(self):
        return reverse("workspace:projects-list")


class ProjectsListDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = "workspace/projects-list-confirm-delete.html"

    def get_queryset(self):
        return super().get_queryset().select_related("command")

    def get_success_url(self):
        return reverse("workspace:projects-list")


class ProjectsListUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    fields = ["title", "description", "start_date", "command"]
    template_name = "workspace/projects-list-update.html"
    context_object_name = "project"

    def get_queryset(self):
        return super().get_queryset().select_related("command")

    def get_success_url(self):
        return reverse("workspace:projects-list")


class ProjectsTaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = "workspace/projects-list-detail.html"
    context_object_name = "task"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("project__command", "assigned_to", "direction", "task_type")
        )

    def get_object(self):
        project_id = self.kwargs["project_id"]
        task_id = self.kwargs["pk"]
        return get_object_or_404(Task, project__id=project_id, pk=task_id)


class ProjectArchiveView(generic.View):
    def post(self, request: HttpRequest, pk: int):
        project = get_object_or_404(Project, pk=pk)
        if request.user.is_leader:
            Archive.objects.create(
                project_id=project.id,
                worker_id=None,
                task_id=None,
            )
        return redirect("workspace:projects-list")


# TASK ------------------
class TaskUserArchiveView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "workspace/tasks-archive.html"
    context_object_name = "tasks"

    def get_queryset(self):
        user_id = self.request.user.id
        archived_tasks_ids = Archive.objects.filter(worker_id=user_id).values_list(
            "task_id", flat=True
        )
        return (
            Task.objects.filter(id__in=archived_tasks_ids)
            .filter(execution_status=100)
            .select_related("project", "assigned_to", "direction", "task_type")
        )

    def get_context_data(self, *, object_list=..., **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user
        context["archive_users_ids"] = Archive.objects.values_list(
            "worker_id", flat=True
        )
        return context


@login_required
def task_in_archive(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task.objects.select_related("project__command"), pk=pk)
    user = request.user
    project_id = task.project_id
    if user.is_leader:
        Archive.objects.create(
            worker_id=user.id,
            project_id=project_id,
            task=task,
        )
        task.status = "done"
        task.stage_of_execution = 100
        task.save()
    return redirect("workspace:project-tasks-list", project_id=project_id)


class TasksListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "workspace/tasks-list.html"
    context_object_name = "tasks"

    def get_context_data(self, **kwargs):
        user_id = self.request.user.id
        context = super().get_context_data(**kwargs)
        context["archive_tasks_ids"] = Archive.objects.values_list("task_id", flat=True)
        context["form"] = TaskCreationForm(user=self.request.user)
        context["user"] = User.objects.get(id=user_id)
        return context

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        command_id = self.request.user.command_id
        return (
            Task.objects.filter(project_id=project_id, project__command_id=command_id)
            .filter(stage_of_execution__lt=76)
            .select_related("project", "assigned_to", "task_type")
        )


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskCreationForm

    def get_success_url(self):
        return reverse(
            "workspace:project-tasks-list",
            kwargs={"project_id": self.object.project.pk},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    template_name = "workspace/task-update.html"
    form_class = TaskUpdateForm

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("project__command", "assigned_to", "direction", "task_type")
        )

    def get_success_url(self):
        return reverse(
            "workspace:project-tasks-list",
            kwargs={"project_id": self.object.project.pk},
        )


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "workspace/task-confirm-delete.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("project__command", "assigned_to", "direction", "task_type")
        )

    def get_success_url(self):
        return reverse(
            "workspace:project-tasks-list",
            kwargs={"project_id": self.object.project.pk},
        )


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    context_object_name = "task"
    template_name = "workspace/task-detail.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("project__command", "assigned_to", "direction", "task_type")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = TaskChangeExecutionForm(instance=self.object)
        context["form_update"] = TaskForm(instance=self.object)
        return context


class TaskExecutionChangeView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskChangeExecutionForm
    template_name = "workspace/task-detail.html"
    context_object_name = "task"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("project__command", "assigned_to", "direction", "task_type")
        )

    def get_success_url(self):
        return reverse("workspace:task-detail", kwargs={"pk": self.object.pk})


class TaskModalUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    template_name = "workspace/task-detail.html"
    form_class = TaskForm
    context_object_name = "task"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("project__command", "assigned_to", "direction", "task_type")
        )

    def get_success_url(self):
        return reverse("workspace:task-detail", kwargs={"pk": self.object.pk})


class TaskReviewListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "workspace/task-review-list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        user = self.request.user
        if user.command_id:
            return Task.objects.filter(
                stage_of_execution=75, assigned_to__command_id=user.command_id
            ).select_related("project", "assigned_to", "direction", "task_type")
        return Task.objects.all().select_related(
            "project", "assigned_to", "direction", "task_type"
        )


@login_required
def assign_to_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task.objects.select_related("project__command"), id=pk)
    user = request.user
    if task.assigned_to == user:
        task.assigned_to = None
        task.stage_of_execution = 25
        task.execution_status = 0
        task.status = "to_do"
    else:
        task.assigned_to = user
        task.stage_of_execution = 50
        task.status = "in_progress"

    task.save()
    return redirect("workspace:task-detail", pk=pk)


class LinkInputView(LoginRequiredMixin, generic.FormView):
    template_name = "workspace/task-detail.html"
    form_class = TaskLinkForm
    success_url = reverse_lazy("workspace:task-detail")

    def form_valid(self, form):
        link = form.cleaned_data["link"]
        task = get_object_or_404(
            Task.objects.select_related("project__command"),
            pk=self.request.GET.get("pk"),
        )
        task.link_to_solution = link
        task.save()
        return super().form_valid(form)
