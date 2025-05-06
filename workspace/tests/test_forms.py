from django.test import TestCase
from django.contrib.auth import get_user_model

from workspace.forms import (
    WorkerCreationForm,
    TaskCreationForm,
    TaskChangeExecutionForm,
)

from workspace.models import Command, Direction, Task, Project, TaskType


class FormTests(TestCase):
    def setUp(self):
        self.direction_frontend = Direction.objects.create(direction="Frontend")
        self.direction_backend = Direction.objects.create(direction="Backend")
        self.direction_qa = Direction.objects.create(direction="Quality Assurance")

        self.leader_existing_command = get_user_model().objects.create_user(
            username="leader_backend",
            password="password",
            first_name="backend",
            last_name="leader",
            email="backend.leader@test.com",
            direction=self.direction_backend,
            is_leader=True,
        )
        self.existing_command = Command.objects.create(
            name="test command", code="BACKEND000", leader=self.leader_existing_command
        )
        self.leader_existing_command.command = self.existing_command
        self.leader_existing_command.save()

        self.regular_user_existing_command = get_user_model().objects.create_user(
            username="worker",
            password="password",
            first_name="worker",
            last_name="test",
            email="test@test.com",
            direction=self.direction_frontend,
            command=self.existing_command,
            is_leader=False,
        )

        self.leader_new_command_candidate = get_user_model().objects.create_user(
            username="leader_qa",
            password="password",
            first_name="Beta",
            last_name="Candidate",
            email="beta.candidate@test.com",
            direction=self.direction_qa,
        )

        self.feature_type = TaskType.objects.create(name="Feature")
        self.bugfix_type = TaskType.objects.create(name="Bugfix")

        self.project_frontend = Project.objects.create(
            title="Frontend Project",
            description="Project for Frontend Team",
            command=self.existing_command,
        )

        self.task_to_change = Task.objects.create(
            project=self.project_frontend,
            title="Task to Change",
            description="Desc Change",
            task_type=self.feature_type,
            status="in_progress",
            assigned_to=self.regular_user_existing_command,
            direction=self.direction_frontend,
            stage_of_execution=50,
            execution_status=50,
        )

        self.another_user_in_frontend = get_user_model().objects.create_user(
            username="another_frontend_user",
            password="password",
            first_name="Alpha",
            last_name="Another",
            email="another@test.com",
            direction=self.direction_frontend,
            command=self.existing_command,
            is_leader=False,
        )

    def test_worker_creation_with_existing_command(self):
        form_data = {
            "username": "new_worker",
            "password1": "1qazcde3",
            "password2": "1qazcde3",
            "first_name": "New",
            "last_name": "Worker",
            "email": "test@test.com",
            "direction": self.direction_frontend.pk,
            "command_code": self.existing_command.code,
        }
        form = WorkerCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        worker = form.save()

        self.assertIsNotNone(worker.pk)
        self.assertEqual(worker.username, "new_worker")
        self.assertEqual(worker.command, self.existing_command)
        self.assertFalse(worker.is_leader)
        self.assertEqual(worker.direction, self.direction_frontend)
        self.assertEqual(Command.objects.count(), 1)

    def test_worker_creation_with_new_command(self):
        new_code = "test000000"
        form_data = {
            "username": "new_worker",
            "password1": "1qazcde3",
            "password2": "1qazcde3",
            "first_name": "New",
            "last_name": "Worker",
            "email": "new_worker@test.com",
            "direction": self.direction_backend.pk,
            "command_code": new_code,
        }
        form = WorkerCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        worker = form.save()

        self.assertIsNotNone(worker.pk)
        self.assertEqual(worker.username, "new_worker")
        self.assertEqual(Command.objects.count(), 2)

        new_command = Command.objects.get(code=new_code)
        self.assertIsNotNone(new_command.pk)
        self.assertEqual(new_command.name, "New Command")
        self.assertEqual(worker.command, new_command)
        self.assertTrue(worker.is_leader)
        self.assertEqual(new_command.leader, worker)
        self.assertEqual(worker.direction, self.direction_backend)

    def test_worker_creation_validation_required_fields(self):
        form_data = {}
        form = WorkerCreationForm(data=form_data)

        self.assertFalse(form.is_valid())

        required_fields = [
            "username",
            "password1",
            "password2",
            "direction",
            "command_code",
        ]
        for field in required_fields:
            self.assertIn(field, form.errors)

        form_data_mismatch = {
            "username": "test user",
            "password1": "password1",
            "password2": "password2",
            "direction": self.direction_frontend.pk,
            "command_code": "test000000",
        }
        form = WorkerCreationForm(data=form_data_mismatch)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_worker_creation_validation_command_code_length(self):
        form_data_short = {
            "username": "test user",
            "password1": "password123",
            "password2": "password123",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "direction": self.direction_frontend.pk,
            "command_code": "000",
        }
        form = WorkerCreationForm(data=form_data_short)
        self.assertFalse(form.is_valid())
        self.assertIn("command_code", form.errors)

        form_data_long = {
            "username": "test user",
            "password1": "password123",
            "password2": "password123",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "direction": self.direction_frontend.pk,
            "command_code": "000000000000000000000000000",
        }
        form = WorkerCreationForm(data=form_data_long)
        self.assertFalse(form.is_valid())
        self.assertIn("command_code", form.errors)

    def test_task_creation_form_assigned_to_queryset_not_filtered_without_user(self):
        form = TaskCreationForm()
        assigned_to_queryset = form.fields["assigned_to"].queryset
        self.assertEqual(assigned_to_queryset.count(), get_user_model().objects.count())

    def test_task_change_execution_form_save_status_to_code_review(self):
        form_data = {
            "execution_status": 100,
            "link_to_solution": "http://github.com/solution",
        }
        form = TaskChangeExecutionForm(data=form_data, instance=self.task_to_change)
        self.assertTrue(form.is_valid(), form.errors)

        task = form.save()

        self.task_to_change.refresh_from_db()

        self.assertEqual(task.execution_status, 100)
        self.assertEqual(task.link_to_solution, "http://github.com/solution")
        self.assertEqual(task.status, "code_review")
        self.assertEqual(task.stage_of_execution, 75)

    def test_task_change_execution_form_save_status_below_100(self):
        self.assertNotEqual(self.task_to_change.status, "code_review")
        self.assertNotEqual(self.task_to_change.status, "done")
        initial_status = self.task_to_change.status
        initial_stage = self.task_to_change.stage_of_execution

        form_data = {
            "execution_status": 80,
            "link_to_solution": "",
        }
        form = TaskChangeExecutionForm(data=form_data, instance=self.task_to_change)

        self.assertTrue(form.is_valid(), form.errors)

        task = form.save()

        self.task_to_change.refresh_from_db()
        self.assertEqual(task.execution_status, 80)
        self.assertEqual(task.link_to_solution, "")
        self.assertEqual(task.status, initial_status)
        self.assertEqual(task.stage_of_execution, initial_stage)

    def test_task_change_execution_form_validation(self):
        form_data = {
            "execution_status": -10,
            "link_to_solution": "not-a-url",
        }
        form = TaskChangeExecutionForm(data=form_data, instance=self.task_to_change)
        self.assertFalse(form.is_valid())
        self.assertIn("execution_status", form.errors)
        self.assertIn("link_to_solution", form.errors)

        form_data_valid = {
            "execution_status": 50,
            "link_to_solution": "http://github.com/solution",
        }
        form = TaskChangeExecutionForm(
            data=form_data_valid, instance=self.task_to_change
        )
        self.assertTrue(form.is_valid())
