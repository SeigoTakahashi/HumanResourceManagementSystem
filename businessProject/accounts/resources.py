from import_export import resources, fields
from django.contrib.auth import get_user_model
from import_export.widgets import Widget,DateWidget
from django.contrib.auth.hashers import make_password
from notification.utils import send_custom_email

CustomUser = get_user_model()

LOGIN_URL = "http://127.0.0.1:8000/accounts/login/"

class PasswordHashWidget(Widget):
    """パスワードをハッシュ化するウィジェット"""

    def clean(self, value, row=None, *args, **kwargs):
        if value:
            # パスワードがすでにハッシュ化されていない場合のみハッシュ化
            if not value.startswith('pbkdf2_sha256'):  # ハッシュ化されたパスワードは 'pbkdf2_sha256' で始まる
                return make_password(value)
        return value  # ハッシュ化されている場合そのまま返す

    def render(self, value, obj=None, *args, **kwargs):
        return value  # エクスポート時にはそのまま返す（すでにハッシュ化された値）

class CustomUserResource(resources.ModelResource):
    """ユーザーリソース"""

    user_id = fields.Field(attribute='username', column_name='ID')
    email = fields.Field(attribute='email', column_name='メールアドレス')
    name = fields.Field(attribute='first_name', column_name='名前')
    password = fields.Field(attribute='password', column_name='パスワード', widget=PasswordHashWidget())
    employee_type = fields.Field(attribute='employee_type', column_name='社員属性')
    date_of_joining = fields.Field(attribute='date_of_joining', column_name='入社日', widget=DateWidget(format='%Y/%m/%d'))

    class Meta:
        model = CustomUser
        fields = ('user_id', 'email', 'name', 'password', 'employee_type', 'date_of_joining')
        import_id_fields = ('user_id',)
        skip_unchanged = True
        report_skipped = True
    
    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        """インポート完了後に実行される処理"""
        if not dry_run:  # 実際のインポート時のみ実行
            # インポートされた行のデータを取得
            for i, row in enumerate(dataset.dict):  # datasetからdict形式でデータを取得
                if result.rows[i].import_type == 'new':  # 新規作成されたユーザーのみ
                    # メール本文の作成
                    subject = '【業務管理サイト】アカウント情報のお知らせ'
                    message = f"""
    {row.get('名前')}様

    業務管理サイトのアカウントが作成されました。
    以下の情報でログインしてください。

    ユーザーID: {row.get('ID')}
    初期パスワード: {row.get('パスワード')}

    初回ログイン時にパスワードの変更が必要です。

    ログインはこちら: {LOGIN_URL}
                    """
                    
                    # メール送信
                    send_custom_email(
                        subject=subject,
                        message=message,
                        from_email=None,
                        recipient_list=[row.get('メールアドレス')]
                    )