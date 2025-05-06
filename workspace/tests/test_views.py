from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from workspace.models import Direction, Project, Command, Task, TaskType


class TaskViewsTest(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(
            name="Bag"
        )
        self.project = Project.objects.create(
            title="test_project",
            description="test description",
            start_date="2020-09-03"
        )
        self.direction = Direction.objects.create(
            direction="Backend"
        )

        self.command = Command.objects.create(
            name="Test Command",
            code="test00test",
        )

        self.worker = get_user_model().objects.create_user(
            username="test_username",
            first_name="Joe",
            last_name="Vie",
            password="1qazcde3",
            email="test@gmail.com",
            direction=self.direction,
            command=self.command,
            is_leader=False,
        )
        self.active_task = Task.objects.create(
            project=self.project,
            title="test_active_task_with_status_to_do",
            description="test active task",
            task_type=self.task_type,
            status="to_do",
            stage_of_execution="25",
            execution_status="0",
            assigned_to=None,
            created_at="2000-01-01",
            direction=self.direction,
            deadline="2026-03-05",
            github_link="https://github.com",
            link_to_solution=None,
        )
        self.task_for_review = Task.objects.create(
            project=self.project,
            title="test_task_for_review",
            description="test_review",
            task_type=self.task_type,
            status="code_review",
            stage_of_execution="75",
            execution_status="100",
            assigned_to=self.worker,
            created_at="2000-01-01",
            direction=self.direction,
            deadline="2026-03-05",
            github_link="https://github.com",
            link_to_solution="https://solution.com"
        )

        self.client.login(username="test_username", password="1qazcde3")


    def test_tasks_list_view_status(self):
        response = self.client.get(reverse("workspace:project-tasks-list", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 200)

    def test_tasks_to_review_list_view_status(self):
        response = self.client.get(reverse("workspace:tasks-review-list"))
        self.assertEqual(response.status_code, 200)

    def test_task_with_execution_status_100_in_review_list(self):
        response = self.client.get(reverse("workspace:tasks-review-list"))
        self.assertContains(response, "test_task_for_review")

    def test_if_user_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("workspace:project-tasks-list", kwargs={"project_id": self.project.id}))
        self.assertRedirects(response, "/accounts/login/?next=/projects-list/1/tasks/", status_code=302, target_status_code=200)

    def test_get_context_data_tasks_list_view(self):
        response = self.client.get(reverse("workspace:project-tasks-list", kwargs={"project_id": self.project.id}))
        user = response.context["user"]
        self.assertEqual(user, self.worker)

    def test_get_queryset_tasks_list_view(self):
        response = self.client.get(reverse("workspace:project-tasks-list", kwargs={"project_id": self.project.id}))
        tasks = response.context["tasks"]
        for task in tasks:
            self.assertLess(task.stage_of_execution, 76)

    def test_task_have_the_right_data_in_project_tasks_list(self):
        response = self.client.get(reverse("workspace:project-tasks-list", kwargs={"project_id": self.project.id}))
        tasks = response.context["tasks"]
        for task in tasks:
            self.assertIn("test_active_task_with_status_to_do", task.title)
            self.assertIn("test active task", task.description)
            self.assertIn("2026-03-05", task.deadline)

    def test_render_template_tasks_list_view(self):
        response = self.client.get(reverse("workspace:project-tasks-list", kwargs={"project_id": self.project.id}))
        self.assertTemplateUsed(response, "workspace/tasks-list.html")

