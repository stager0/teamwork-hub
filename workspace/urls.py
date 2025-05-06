from django.urls import path

from workspace.views import index, ProjectsListView, ProjectsListCreateView, ProjectsListUpdateView, \
    ProjectsListDeleteView, \
    TasksListView, UserDetailView, TaskUpdateView, TaskDeleteView, TaskCreateView, TaskDetailView, UsersListView, \
    assign_to_task, TaskExecutionChangeView, ProjectsDetailView, TaskModalUpdateView, ProjectsTaskDetailView, \
    UserTasksListView, ProjectsArchivedListView, TaskUserArchiveView, task_in_archive, TaskReviewListView, \
    ProjectArchiveView, UserUpdateView

app_name = "workspace"

urlpatterns = [
    path("", index, name="index"),

    path("user_detail/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users-list/", UsersListView.as_view(), name="workers-list"),
    path("user-tasks-list/<int:pk>/", UserTasksListView.as_view(), name="user-tasks-list"),
    path("user/<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),

    path("projects-list/", ProjectsListView.as_view(), name="projects-list"),
    path("projects-list/<int:pk>/detail/", ProjectsTaskDetailView.as_view(), name="projects-list-detail"),
    path("projects-list/<int:pk>/update/", ProjectsListUpdateView.as_view(), name="projects-list-update"),
    path("projects-list/create/", ProjectsListCreateView.as_view(), name="projects-list-create"),
    path("projects-list/<int:pk>/delete/", ProjectsListDeleteView.as_view(), name="projects-list-delete"),
    path("project/<int:pk>/archive/", ProjectArchiveView.as_view(), name="project-archive"),
    path("projects-archieve/", ProjectsArchivedListView.as_view(), name="projects-archive"),
    path("projects-list/<int:project_id>/tasks/", TasksListView.as_view(), name="project-tasks-list"),
    path("projects-list/<int:pk>/", ProjectsDetailView.as_view(), name="project-detail"),

    path("task-detail/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("task/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("task/<int:pk>/modal-update/", TaskModalUpdateView.as_view(), name="task-modal-update"),
    path("task/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path("task/create/", TaskCreateView.as_view(), name="task-create"),
    path("project/<int:project_id>/task/<int:pk>/", TaskDetailView.as_view(), name="project-task-detail"),
    path("task/<int:pk>/assign/", assign_to_task, name="assign-to-task"),
    path("task/<int:pk>/change-task-execution/", TaskExecutionChangeView.as_view(), name="change-task-execution"),
    path("task/<int:pk>/archive-tasks/", TaskUserArchiveView.as_view(), name="user-archive-tasks"),
    path("task/<int:pk>/", task_in_archive , name="task-in-archive"),
    path("tasks-review-list/", TaskReviewListView.as_view(), name="tasks-review-list")

]
