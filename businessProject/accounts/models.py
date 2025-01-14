from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """拡張ユーザーモデル"""
    
    EMPLOYEE_TYPES = [
        ('内定者', '内定者'),
        ('社員', '社員'),
        ('退職者', '退職者'),
        ('人事', '人事'),
    ]

    employee_type = models.CharField(
        max_length=20,
        choices=EMPLOYEE_TYPES,
        default='内定者',
        verbose_name='社員属性'
    )

    date_of_joining = models.DateField(
        null=True,
        blank=True,
        verbose_name='入社日'
    )

    is_first_login = models.BooleanField(
        default=True,
        verbose_name='初回ログイン'
    )