from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from import_export.admin import ExportMixin
from .models import Confirmation, BicycleCommute
from .resources import ConfirmationResource, BicycleCommuteResource

class UserJoinDateFilter(SimpleListFilter):
    """ユーザーの入社日ごとに絞り込むフィルター"""
    title = '入社日'  # 管理画面で表示されるフィルター名
    parameter_name = 'date_of_joining'

    def lookups(self, request, model_admin):
        # 全てのユーザーの入社日を取得し、選択肢として表示
        join_dates = model_admin.model.objects.values_list('user__date_of_joining', flat=True).distinct()
        return [(date, date.strftime('%Y-%m-%d')) for date in join_dates if date]

    def queryset(self, request, queryset):
        # フィルターで選択された日付で絞り込み
        if self.value():
            return queryset.filter(user__date_of_joining=self.value())
        return queryset

class ConfirmationAdmin(ExportMixin, admin.ModelAdmin):
    """住居・身上確認書モデルの管理画面"""
    
    list_display = ('user', 'name', 'address', 'updated_at', 'status')
    list_filter = ('name', 'status', UserJoinDateFilter)
    search_fields = ('name', 'name_kana', 'address', 'address_kana', 'status')
    list_per_page = 10

    resource_class = ConfirmationResource

    def get_fields(self, request, obj=None):
        if obj and obj.is_bicycle_commute:  
            return (
                'user', 'name', 'name_kana', 'address', 'address_kana',
                'is_bicycle_commute', 'commuting_expenses', 'updated_at', 'status', 'remarks'
            )
        else:  
            return (
                'user','name', 'name_kana', 'address', 'address_kana', 
                'is_bicycle_commute', 'commute_route', 'transportation_type', 
                'bus_route', 'commuting_expenses', 'updated_at', 'status', 'remarks'
            )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_bicycle_commute:  
            return (
                'user','name', 'name_kana', 'address', 'address_kana',
                'is_bicycle_commute', 'commuting_expenses', 'updated_at', 'status', 'remarks'
            )
        else:  
            return (
                'user','name', 'name_kana', 'address', 'address_kana', 
                'is_bicycle_commute', 'commute_route', 'transportation_type', 
                'bus_route', 'commuting_expenses', 'updated_at', 'status', 'remarks'
            )


admin.site.register(Confirmation, ConfirmationAdmin)

class BicycleCommuteAdmin(ExportMixin, admin.ModelAdmin):
    """自転車通勤申請書モデルの管理画面"""
    
    list_display = ('user', 'name', 'current_address', 'updated_at', 'status')
    list_filter = ('application_date', 'status', UserJoinDateFilter)
    search_fields = ('name', 'name_kana', 'current_address', 'status')
    list_per_page = 10

    resource_class = BicycleCommuteResource

    def get_fields(self, request, obj=None):
        return ('user', 'application_date', 'employee_number', 'name', 'name_kana', 'affiliation','current_address', 'amount', 'updated_at', 'status', 'remarks')

    def get_readonly_fields(self, request, obj=None):
        return ('user', 'application_date', 'employee_number', 'name', 'name_kana', 'affiliation', 'current_address', 'amount', 'updated_at', 'status', 'remarks')

admin.site.register(BicycleCommute, BicycleCommuteAdmin)