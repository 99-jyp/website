import time
import unittest
from pathlib import Path

from ai.memory import memory
from tools.employee import (
    create_employee,
    delete_employee,
    export_employee_excel,
    get_leave,
    search_employee,
)


class MemoryAndExcelFlowTest(unittest.TestCase):
    def test_memory_reference_for_leave(self):
        name = f"메모리테스트_{int(time.time())}"

        created = create_employee(name=name, department="원무과")
        self.assertTrue(created["success"])

        searched = search_employee(name)
        self.assertTrue(searched["success"])

        leave = get_leave()
        self.assertTrue(leave["success"])
        self.assertEqual(leave["leave"], 15)

        deleted = delete_employee(name)
        self.assertTrue(deleted["success"])

    def test_export_employee_excel(self):
        result = export_employee_excel(filename="employee_export_test.xlsx")
        self.assertTrue(result["success"])

        path = Path(result["file_path"])
        self.assertTrue(path.exists())

        # Reset memory state side effects from previous tests.
        memory.set_employee(None)
        memory.set_department(None)

        path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
