# Generated by Django 5.0.4 on 2024-12-10 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("request", "0006_alter_confirmation_transportation_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="confirmation",
            name="economic_route_json",
            field=models.JSONField(blank=True, null=True, verbose_name="経済路線（JSON）"),
        ),
    ]
