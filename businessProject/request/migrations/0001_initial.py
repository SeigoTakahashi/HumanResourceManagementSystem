# Generated by Django 5.0.4 on 2024-12-03 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Confirmation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="氏名")),
                ("name_kana", models.CharField(max_length=100, verbose_name="氏名フリガナ")),
                ("address", models.TextField(verbose_name="住所")),
                ("address_kana", models.TextField(verbose_name="住所フリガナ")),
                (
                    "commute_route",
                    models.TextField(blank=True, null=True, verbose_name="通勤経路"),
                ),
                (
                    "transportation_type",
                    models.CharField(
                        choices=[("walk", "徒歩"), ("bus", "バス"), ("bicycle", "自転車")],
                        default="walk",
                        max_length=10,
                        verbose_name="交通手段",
                    ),
                ),
                (
                    "bus_route",
                    models.TextField(blank=True, null=True, verbose_name="バス経路"),
                ),
            ],
        ),
    ]
