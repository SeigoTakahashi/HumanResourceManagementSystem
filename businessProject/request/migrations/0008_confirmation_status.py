# Generated by Django 5.0.4 on 2024-12-13 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("request", "0007_confirmation_economic_route_json"),
    ]

    operations = [
        migrations.AddField(
            model_name="confirmation",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "申請中"),
                    ("approved", "承認済み"),
                    ("rejected", "差し戻し"),
                ],
                default="pending",
                max_length=10,
                verbose_name="申請ステータス",
            ),
        ),
    ]
