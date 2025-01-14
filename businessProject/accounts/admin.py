from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from accounts.models import CustomUser
from import_export.admin import ImportExportModelAdmin
from .resources import CustomUserResource

class UserJoinDateFilter(SimpleListFilter):
    """ユーザーの入社日ごとに絞り込むフィルター"""
    title = '入社日'  # 管理画面で表示されるフィルター名
    parameter_name = 'date_of_joining'

    def lookups(self, request, model_admin):
        # 全てのユーザーの入社日を取得し、選択肢として表示
        join_dates = model_admin.model.objects.values_list('date_of_joining', flat=True).distinct()
        return [(date, date.strftime('%Y-%m-%d')) for date in join_dates if date]

    def queryset(self, request, queryset):
        # フィルターで選択された日付で絞り込み
        if self.value():
            return queryset.filter(date_of_joining=self.value())
        return queryset
    
class CustomUserAdmin(ImportExportModelAdmin):
    resource_class = CustomUserResource
    list_display = ('username', 'email', 'first_name', 'employee_type', 'is_active', 'date_of_joining')
    list_filter = ('employee_type', 'is_active', UserJoinDateFilter)
    search_fields = ('username', 'email', 'first_name',)
    list_per_page = 10
    fields = ('username', 'email', 'first_name', 'employee_type', 'is_staff', 'is_active', 'date_of_joining', 'is_first_login')

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.site_header = '業務管理サイト'

admin.site.index_title = 'メニュー'