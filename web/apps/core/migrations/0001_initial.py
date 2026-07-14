from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("message", models.TextField()),
                ("level", models.CharField(
                    choices=[
                        ("info", "정보"),
                        ("success", "성공"),
                        ("warning", "경고"),
                        ("danger", "위험"),
                    ],
                    default="info",
                    max_length=20,
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "알림",
                "verbose_name_plural": "알림 목록",
                "ordering": ["-created_at"],
            },
        ),
    ]
