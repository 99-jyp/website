from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Hospital AI 관리자"
admin.site.site_title = "Hospital AI"
admin.site.index_title = "관리 패널"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("web.apps.accounts.urls")),
    path("", include("web.apps.core.urls")),
]
