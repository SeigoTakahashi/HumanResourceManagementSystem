# Generated by Django 5.0.7 on 2024-11-30 03:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_customuser_date_of_joining_customuser_employee_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="employee_type",
            field=models.CharField(
                choices=[("内定者", "内定者"), ("社員", "社員"), ("退職者", "退職者"), ("人事", "人事")],
                default="内定者",
                max_length=20,
                verbose_name="社員属性",
            ),
        ),
    ]
