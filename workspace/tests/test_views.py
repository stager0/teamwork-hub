from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from workspace.models import Direction, Project, Command, Task, TaskType, Archive


class BaseTestCase(TestCase):
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
        self.leader_worker = get_user_model().objects.create_user(
            username="leader_worker",
            first_name="Joe",
            last_name="Vie",
            password="1qazcde3",
            email="test@gmail.com",
            direction=self.direction,
            command=self.command,
            is_leader=True,
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
        self.task_archive = Task.objects.create(
            project=self.project,
            title="test_archive_task",
            description="The task is already done",
            task_type=self.task_type,
            status="done",
            stage_of_execution="100",
            execution_status="100",
            assigned_to=self.worker,
            created_at="2000-01-01",
            direction=self.direction,
            deadline="2026-03-05",
            github_link="https://github.com",
            link_to_solution="https://solution.com"
        )
        self.task_assigned_to_worker = Task.objects.create(
            project=self.project,
            title="test_task_with_status_in_progress",
            description="test task in progress",
            task_type=self.task_type,
            status="in_progress",
            stage_of_execution="50",
            execution_status="37",
            assigned_to=self.worker,
            created_at="2025-01-01",
            direction=self.direction,
            deadline="2026-03-05",
            github_link="https://github.com",
            link_to_solution=None,
        )

        self.client.login(username="test_username", password="1qazcde3")


class TasksListAndTaskReviewListTests(BaseTestCase):

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


class UserTasksListTests(BaseTestCase):
    def test_if_tasks_assigned_to_user_are_in_current_tasks(self):
        response = self.client.get(reverse("workspace:user-tasks-list", kwargs={"pk": self.worker.pk}))
        tasks = response.context["tasks"]
        for task in tasks:
            self.assertIn("test_task_with_status_in_progress", task.title)

    def test_if_tasks_assigned_to_worker_have_in_progress_status(self):
        response = self.client.get(reverse("workspace:user-tasks-list", kwargs={"pk": self.worker.pk}))
        tasks = response.context["tasks"]
        for task in tasks:
            self.assertIn("in_progress", task.status)

    def test_if_task_title_leads_to_task_page(self):
        response = self.client.get(reverse("workspace:user-tasks-list", kwargs={"pk": self.worker.pk}))
        tasks = response.context["tasks"]
        for task in tasks:
            expected_url = reverse("workspace:task-detail", kwargs={"pk": task.id})
            self.assertContains(response, f'href="{expected_url}"')

    def test_task_detail_page_returns_200_and_contains_task_title(self):
        task = self.task_assigned_to_worker
        url = reverse("workspace:task-detail", kwargs={"pk": task.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, task.title)


class UserArchiveTasksTests(BaseTestCase):
    def test_if_task_with_status_code_review_is_in_user_archive_list(self):
        response = self.client.get(reverse("workspace:user-archive-tasks", kwargs={"pk": self.worker.id}))
        tasks = response.context["tasks"]
        for task in tasks:
            self.assertContains(response, "test_task_for_review")

    def test_if_task_with_status_done_is_in_user_archive_list(self):
        response = self.client.get(reverse("workspace:user-archive-tasks", kwargs={"pk": self.worker.id}))
        tasks = response.context["tasks"]
        for task in tasks:
            self.assertContains(response, "test_archive_task")

    def test_task_with_status_to_do_and_in_progress_are_not_in_user_tasks_archive(self):
        response = self.client.get(reverse("workspace:user-archive-tasks", kwargs={"pk": self.worker.id}))
        tasks = response.context["tasks"]
        for task in tasks:
            self.assertNotContains(response, "To Do")
            self.assertNotContains(response, "In Progress")


class LogicStatusChangeTests(BaseTestCase):
    def test_if_the_status_changes_when_user_takes_task(self):
        task = self.active_task
        response = self.client.get(reverse("workspace:assign-to-task", kwargs={"pk": task.id}))

        task.refresh_from_db()
        self.assertEqual(task.stage_of_execution, 50)
        self.assertEqual(task.status, "in_progress")
        self.assertEqual(task.assigned_to, self.worker)

    def test_if_the_status_changes_when_user_unassign_the_task(self):
        task = self.task_assigned_to_worker
        response = self.client.get(reverse("workspace:assign-to-task", kwargs={"pk": task.id}))

        task.refresh_from_db()
        self.assertEqual(task.stage_of_execution, 25)
        self.assertEqual(task.status, "to_do")
        self.assertEqual(task.execution_status, 0)
        self.assertNotEqual(task.assigned_to, self.worker)

    def test_when_the_user_is_not_authorized_and_trys_to_take_the_task(self):
        self.client.logout()
        task = self.active_task
        response = self.client.get(reverse("workspace:assign-to-task", kwargs={"pk": task.id}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/task/1/assign/")


class LogicProjectAndTaskInArchiveTests(BaseTestCase):
    def test_if_the_project_relocate_to_archive(self):
        self.client.force_login(self.leader_worker)
        project = self.project
        response = self.client.post(reverse("workspace:project-archive", kwargs={"pk": project.id}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Archive.objects.filter(project_id=project.id, worker_id=None, task_id=None).exists())

    def test_if_the_task_relocate_to_archive(self):
        self.client.force_login(self.leader_worker)
        task = self.task_assigned_to_worker
        response = self.client.post(reverse("workspace:task-in-archive", kwargs={"pk": task.id}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Archive.objects.filter(task=task).exists())
