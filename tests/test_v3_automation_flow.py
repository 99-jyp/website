import csv
import time
import unittest
from pathlib import Path

from tools.automation import (
    create_leave_request_pdf,
    generate_leave_status_report,
    import_employees_csv,
    ocr_image_to_text,
    send_notice_email,
    start_daily_leave_scheduler,
    stop_daily_leave_scheduler,
)
from tools.employee import delete_employee, search_employee


class V3AutomationFlowTest(unittest.TestCase):
    def test_pdf_csv_email_scheduler_and_ocr_flow(self):
        timestamp = int(time.time())
        import_name = f"CSV테스트_{timestamp}"

        csv_dir = Path("data") / "imports"
        csv_dir.mkdir(parents=True, exist_ok=True)
        csv_path = csv_dir / f"employees_{timestamp}.csv"

        with csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["name", "department", "leave_days"])
            writer.writeheader()
            writer.writerow({"name": import_name, "department": "원무과", "leave_days": 11})

        imported = import_employees_csv(str(csv_path))
        self.assertTrue(imported["success"])
        self.assertGreaterEqual(imported["imported"], 1)

        searched = search_employee(import_name)
        self.assertTrue(searched["success"])

        pdf = create_leave_request_pdf(name=import_name, reason="테스트")
        self.assertTrue(pdf["success"])
        self.assertTrue(Path(pdf["file_path"]).exists())

        report = generate_leave_status_report()
        self.assertTrue(report["success"])
        self.assertTrue(Path(report["file_path"]).exists())

        scheduler_started = start_daily_leave_scheduler(hour=9, minute=0)
        self.assertTrue(scheduler_started["success"])

        scheduler_stopped = stop_daily_leave_scheduler()
        self.assertTrue(scheduler_stopped["success"])

        email = send_notice_email(
            to_email="test@example.com",
            subject="테스트 공지",
            body="공지 본문",
            dry_run=True,
        )
        self.assertTrue(email["success"])
        self.assertTrue(email["dry_run"])

        ocr = ocr_image_to_text("data/ocr/not_exists.png")
        self.assertFalse(ocr["success"])

        deleted = delete_employee(import_name)
        self.assertTrue(deleted["success"])

        csv_path.unlink(missing_ok=True)
        Path(pdf["file_path"]).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
