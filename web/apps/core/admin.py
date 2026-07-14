from django.contrib import admin
from .models import Employee, Notification


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["employee_no", "name", "department", "leave_days"]
    list_filter = ["department"]
    search_fields = ["name", "employee_no", "department"]
    ordering = ["employee_no"]
    readonly_fields = ["employee_no"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["message", "level", "created_at", "is_read"]
    list_filter = ["level", "is_read"]
    actions = ["mark_read"]

    @admin.action(description="선택 항목을 읽음으로 표시")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
