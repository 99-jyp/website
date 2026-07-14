from django.db import models


class Employee(models.Model):
    """Read/write mirror of the existing employee table created by init_db.py."""

    employee_no = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    leave_days = models.IntegerField(default=15)

    class Meta:
        db_table = "employee"
        managed = False  # Django must not run migrations on this table.
        verbose_name = "직원"
        verbose_name_plural = "직원 목록"
        ordering = ["employee_no"]

    def __str__(self):
        return f"{self.name} ({self.department})"

    @property
    def leave_status(self):
        if self.leave_days < 5:
            return "danger"
        if self.leave_days < 10:
            return "warning"
        return "success"


class Notification(models.Model):
    LEVEL_INFO = "info"
    LEVEL_SUCCESS = "success"
    LEVEL_WARNING = "warning"
    LEVEL_DANGER = "danger"

    LEVEL_CHOICES = [
        (LEVEL_INFO, "정보"),
        (LEVEL_SUCCESS, "성공"),
        (LEVEL_WARNING, "경고"),
        (LEVEL_DANGER, "위험"),
    ]

    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=LEVEL_INFO)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "알림"
        verbose_name_plural = "알림 목록"

    def __str__(self):
        return f"[{self.level}] {self.message[:60]}"
