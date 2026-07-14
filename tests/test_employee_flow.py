import time
import unittest

from tools.employee import (
    create_employee,
    delete_employee,
    get_leave,
    search_employee,
    update_employee_department,
    update_leave,
)


class EmployeeFlowIntegrationTest(unittest.TestCase):
    def test_employee_crud_and_leave_flow(self):
        name = f"통합테스트_{int(time.time())}"

        created = create_employee(name=name, department="원무과")
        self.assertTrue(created["success"])
        self.assertEqual(created["employee"]["name"], name)
        self.assertEqual(created["employee"]["department"], "원무과")

        searched = search_employee(name)
        self.assertTrue(searched["success"])
        self.assertEqual(searched["employee"]["name"], name)

        changed_leave = update_leave(name=name, amount=-2)
        self.assertTrue(changed_leave["success"])
        self.assertEqual(changed_leave["employee"]["leave"], 13)

        leave = get_leave(name=name)
        self.assertTrue(leave["success"])
        self.assertEqual(leave["leave"], 13)

        changed_department = update_employee_department(
            name=name,
            department="총무과"
        )
        self.assertTrue(changed_department["success"])
        self.assertEqual(changed_department["employee"]["department"], "총무과")

        deleted = delete_employee(name=name)
        self.assertTrue(deleted["success"])
        self.assertEqual(deleted["employee"]["name"], name)

        searched_after_delete = search_employee(name)
        self.assertFalse(searched_after_delete["success"])


if __name__ == "__main__":
    unittest.main()
