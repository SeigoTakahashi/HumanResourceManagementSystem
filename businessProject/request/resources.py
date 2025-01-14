from import_export import resources, fields
from import_export.widgets import CharWidget
from .models import Confirmation, BicycleCommute

class CustomChoiceWidget:
    """choices を手動で処理するカスタムウィジェット"""

    def __init__(self, choices):
        self.choices = dict(choices)

    def render(self, value, **kwargs):
        """データベースの値をラベルに変換"""
        return self.choices.get(value, value)

    def clean(self, value, **kwargs):
        """ラベルをデータベースの値に変換"""
        reverse_choices = {v: k for k, v in self.choices.items()}
        return reverse_choices.get(value, value)

class ConfirmationResource(resources.ModelResource):
    """住居・身上確認書モデルのエクスポートリソース"""

    user_username = fields.Field(attribute='user__username', column_name='ユーザー名')
    user_date_of_joining = fields.Field(attribute='user__date_of_joining', column_name='入社日')
    name = fields.Field(attribute='name', column_name='氏名')
    name_kana = fields.Field(attribute='name_kana', column_name='氏名フリガナ')
    address = fields.Field(attribute='address', column_name='住所')
    address_kana = fields.Field(attribute='address_kana', column_name='住所フリガナ')
    updated_at = fields.Field(attribute='updated_at', column_name='更新日時')
    is_bicycle_commute = fields.Field(attribute='is_bicycle_commute', column_name='自転車通勤か')
    commute_route = fields.Field(attribute='commute_route', column_name='通勤経路')
    transportation_type = fields.Field(attribute='transportation_type', column_name='交通手段', widget=CharWidget())
    bus_route = fields.Field(attribute='bus_route', column_name='バス経路')
    commuting_expenses = fields.Field(attribute='commuting_expenses', column_name='定期券代')

    class Meta:
        model = Confirmation
        fields = (
            'user_username', 'user_date_of_joining', 'name', 'name_kana', 
            'address', 'address_kana', 'updated_at',
            'is_bicycle_commute', 'commute_route', 
            'transportation_type', 'bus_route', 'commuting_expenses'
        )  # エクスポートするカラムを指定
        export_order = (
            'user_user_name', 'user_date_of_joining', 'name', 'name_kana', 
            'address', 'address_kana', 'updated_at', 
            'is_bicycle_commute', 'commute_route', 
            'transportation_type', 'bus_route', 'commuting_expenses'
        )  # エクスポート順を指定
    
    def dehydrate_transportation_type(self, obj):
        """交通手段の値を日本語に変換"""
        TRANSPORTATION_CHOICES = {
            'walk': '徒歩',
            'bus': 'バス',
            'bicycle': '自転車',
        }
        return TRANSPORTATION_CHOICES.get(obj.transportation_type, '不明')

class BicycleCommuteResource(resources.ModelResource):
    """自転車通勤申請書モデルのエクスポートリソース"""

    user_username = fields.Field(attribute='user__username', column_name='ユーザー名')
    user_date_of_joining = fields.Field(attribute='user__date_of_joining', column_name='入社日')
    name = fields.Field(attribute='name', column_name='氏名')
    name_kana = fields.Field(attribute='name_kana', column_name='氏名フリガナ')
    current_address = fields.Field(attribute='current_address', column_name='現住所')
    amount = fields.Field(attribute='amount', column_name='支給金額')
    updated_at = fields.Field(attribute='updated_at', column_name='更新日時')
    application_date = fields.Field(attribute='application_date', column_name='申請日')
    employee_number = fields.Field(attribute='employee_number', column_name='社員番号')
    affiliation = fields.Field(attribute='affiliation', column_name='所属')

    class Meta:
        model = BicycleCommute
        fields = (
            'user_username', 'user_date_of_joining', 'name', 'name_kana', 
            'current_address', 'amount', 'updated_at',
            'application_date', 'employee_number', 'affiliation'
        )   # エクスポートするカラムを指定
        export_order = (
            'user_username', 'user_date_of_joining', 'name', 'name_kana', 
            'current_address', 'amount', 'updated_at',
            'application_date', 'employee_number', 'affiliation'
        )   # エクスポート順を指定