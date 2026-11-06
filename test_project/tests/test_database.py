import tempfile
import unittest
from pathlib import Path
from taskflow.database import (
    initialize_database,
    list_tasks,
    create_task,
    set_task_completed,
    delete_task
)


class TaskDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temp_dir.name) / "test.db")
        initialize_database(self.database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_list_task(self):
        created = create_task(self.database_path, "Estudiar Python")
        tasks = list_tasks(self.database_path)
        self.assertEqual(created["title"], "Estudiar Python")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["completed"], 0)

    def test_toggle_task_completion(self):
        task = create_task(self.database_path, "Probar aplicación")
        updated = set_task_completed(self.database_path, task["id"])
        self.assertEqual(updated["completed"], 1)

    def test_delete_task(self):
        task = create_task(self.database_path, "Eliminar después")
        self.assertTrue(delete_task(self.database_path, task["id"]))
        self.assertEqual(list_tasks(self.database_path), [])

    def test_missing_task_returns_none(self):
        self.assertIsNone(set_task_completed(self.database_path, 999))
        self.assertFalse(delete_task(self.database_path, 999))


if __name__ == "__main__":
    unittest.main()
