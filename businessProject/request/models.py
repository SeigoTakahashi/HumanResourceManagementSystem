from django.db import models
from accounts.models import CustomUser

class ApplicationManager(models.Manager):
    def get_all_applications(self):
        # 申請日時順に並べ替えて取得
        return self.get_queryset().order_by('-updated_at')
    
class Application(models.Model):
    """申請モデル"""

    STATUS_CHOICES = [
        ('pending', '申請中'),
        ('approved', '承認済み'),
        ('rejected', '差し戻し'),
    ]
    
    user = models.ForeignKey(
        to=CustomUser,
        verbose_name='ユーザ',
        on_delete=models.CASCADE,
        null=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name="申請ステータス",
        default='pending'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    approval_date = models.DateField(verbose_name="承認日", blank=True, null=True)
    remarks = models.TextField(verbose_name="備考欄", blank=True, null=True)

    objects = ApplicationManager()

    class Meta:
        abstract = True
    
    def get_next_application(self, user=None):
        """次の申請書を取得"""
        queryset = type(self).objects.filter(
            updated_at__lt=self.updated_at,
            status='approved'  # 承認済みのみを対象とする
        )
        
        if user and user.is_staff:
            # 管理者の場合は全ユーザーの申請を対象
            return queryset.order_by('-updated_at').first()
        else:
            # 一般ユーザーの場合は自身の申請のみ
            return queryset.filter(user=self.user).order_by('-updated_at').first()

    def get_previous_application(self, user=None):
        """前の申請書を取得"""
        queryset = type(self).objects.filter(
            updated_at__gt=self.updated_at,
            status='approved'  # 承認済みのみを対象とする
        )
        
        if user and user.is_staff:
            # 管理者の場合は全ユーザーの申請を対象
            return queryset.order_by('updated_at').first()
        else:
            # 一般ユーザーの場合は自身の申請のみ
            return queryset.filter(user=self.user).order_by('updated_at').first()

class Confirmation(Application):
    """住居・身上確認書モデル"""
    
    TRANSPORTATION_CHOICES = [
        ('walk', '徒歩'),
        ('bus', 'バス'),
        ('bicycle', '自転車'),
    ]

    name = models.CharField(max_length=100, verbose_name="氏名")
    name_kana = models.CharField(max_length=100, verbose_name="氏名フリガナ")
    address = models.TextField(verbose_name="住所")
    address_kana = models.TextField(verbose_name="住所フリガナ")
    is_bicycle_commute = models.BooleanField(verbose_name="自転車通勤", default=False)
    commute_route = models.TextField(verbose_name="通勤経路", blank=True, null=True)
    transportation_type = models.CharField(
        max_length=10,
        choices=TRANSPORTATION_CHOICES,
        verbose_name="最寄駅までの交通手段",
        default='walk'
    )
    bus_route = models.TextField(verbose_name="バス経路", blank=True, null=True)
    route_json = models.JSONField(verbose_name="経路データ（JSON）", blank=True, null=True)
    bus_route_json = models.JSONField(verbose_name="バス経路データ（JSON）", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    economic_route_json = models.JSONField(verbose_name="経済路線（JSON）", blank=True, null=True)
    commuting_expenses = models.IntegerField(verbose_name="定期券代", blank=True, null=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "住居・身上確認書"
        verbose_name_plural = "住居・身上確認書"


class BicycleCommute(Application):
    """自転車通勤申請書モデル"""

    application_date = models.DateField(verbose_name="申請日")
    employee_number = models.CharField(max_length=10, verbose_name="社員番号")
    name = models.CharField(max_length=100, verbose_name="氏名")
    name_kana = models.CharField(max_length=100, verbose_name="氏名フリガナ")
    affiliation = models.CharField(max_length=100, verbose_name="所属")
    current_address = models.TextField(verbose_name="現住所")
    amount = models.IntegerField(verbose_name="支給額計")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "自転車通勤申請書"
        verbose_name_plural = "自転車通勤申請書"
