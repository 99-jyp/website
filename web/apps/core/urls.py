from django.urls import path
from web.apps.core import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("chat/", views.chat_page, name="chat"),
    path("api/chat/", views.chat_api, name="chat_api"),
    path("api/chat/clear/", views.clear_chat, name="clear_chat"),
    path("api/stats/", views.stats_api, name="stats_api"),
    path("api/notifications/", views.notifications_api, name="notifications_api"),
    path("api/notifications/read/", views.mark_notifications_read, name="mark_notifications_read"),
    path("api/report/", views.generate_report, name="generate_report"),
]
