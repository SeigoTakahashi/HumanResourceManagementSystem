from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from itertools import chain
from datetime import timedelta
from django.utils import timezone
from .models import Confirmation, BicycleCommute
from .forms import ConfirmationForm, BicycleCommuteForm
from notification.models import Notification
from accounts.models import CustomUser
from .utils import is_commute_allowance, is_bicycle_allowance
from notification.utils import send_custom_email

LOGIN_URL = "http://127.0.0.1:8000/accounts/login/"
class DashboardView(LoginRequiredMixin, TemplateView):
    """ダッシュボードページ"""

    template_name = 'request/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        application_models = [Confirmation, BicycleCommute]
        if user.is_staff:
            # 管理者の場合、全体の申請ステータスのカウントを取得
            unprocessing_count = 0
            approved_count = 0
            for application in application_models:
                unprocessing_count += application.objects.filter(status='pending').count()
                approved_count += application.objects.filter(status='approved').count()
            context['unprocessing_count'] = unprocessing_count
            context['approved_count'] = approved_count

            unsubmitted_users = UnsubmittedListView.get_queryset(self)
            context['unsubmitted_count'] = len(unsubmitted_users)
        else:
            # 現在のユーザーに関連する申請ステータスのカウントを取得
            # 内定者の場合の未申請カウント
            if user.employee_type == '内定者':
                # 住居・身上確認書の申請状況
                confirmation_exists = Confirmation.objects.filter(user=user, status='approved').exists()
                
                # 自転車通勤の有無
                is_bicycle_commute = Confirmation.objects.filter(
                    user=user, 
                    is_bicycle_commute=True
                ).exists()

                # 自転車通勤申請書の申請状況
                bicycle_exists = True
                if is_bicycle_commute:
                    bicycle_exists = BicycleCommute.objects.filter(user=user, status='approved').exists()

                # 未申請のカウント
                unsubmitted_count = 0

                # 住居・身上確認書の未提出をチェック
                if not confirmation_exists:
                    unsubmitted_count += 1

                # 自転車通勤申請書の未提出をチェック
                if not bicycle_exists:
                    unsubmitted_count += 1

                context['unsubmitted_count'] = unsubmitted_count
            pending_count = 0
            approved_count = 0
            rejected_count = 0
            for application in application_models:
                pending_count += application.objects.filter(user=user, status='pending').count()
                approved_count += application.objects.filter(user=user, status='approved').count()
                rejected_count += application.objects.filter(user=user, status='rejected').count()

            context['pending_count'] = pending_count
            context['approved_count'] = approved_count
            context['rejected_count'] = rejected_count
        return context

class RouteView(TemplateView):
    """経路探索ページ"""
    
    template_name = 'request/route.html'

class ConfirmationView(LoginRequiredMixin, CreateView):
    """住居・身上確認書の申請ページ"""

    model = Confirmation
    form_class = ConfirmationForm
    template_name = 'request/confirmation.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        context = {'form': form, 'is_update': False}
        home_address = form.cleaned_data.get('address')
        is_bicycle_commute = form.cleaned_data.get('is_bicycle_commute')
        transportation_type = form.cleaned_data.get('transportation_type')
        route_json = form.cleaned_data.get('route_json', {})
        economic_route_json = form.cleaned_data.get('economic_route_json', {})
        bus_route_json = form.cleaned_data.get('bus_route_json', {})

        # 申請内容の確認
        if self.request.POST.get('next', '') == 'confirm':
            is_valid, message = is_commute_allowance(
                home_address=home_address,
                transportation_type=transportation_type,
                route_json=route_json,
                economic_route_json=economic_route_json,
                is_bicycle_commute=is_bicycle_commute,
                bus_route_json=bus_route_json,
            )
            if not is_valid:
                context['error_message'] = message
            return render(self.request, 'request/confirm_confirmation.html', context)

        # 申請内容の修正
        if self.request.POST.get('next', '') == 'back':
            return render(self.request, 'request/confirmation.html', context)
        
        # 申請内容の保存
        if self.request.POST.get('next', '') == 'create':
            confirmation = form.save(commit=False)
            confirmation.user = self.request.user
            
            if confirmation.is_bicycle_commute:
                confirmation.commute_route = ''
                confirmation.transportation_type = 'bicycle'
                confirmation.bus_route = ''
                confirmation.route_json = {}
                confirmation.bus_route_json = {}
                confirmation.economic_route_json = {}
            else:
                if confirmation.transportation_type != 'bus':
                    confirmation.bus_route = ''
                    confirmation.bus_route_json = {}

            confirmation.save()
            admin_users = CustomUser.objects.filter(is_staff=True)
            message = f"{confirmation.user.first_name}さんが住居・身上確認書の申請をしました。\n確認お願いします。\nログインはこちら: {LOGIN_URL}"
            for admin_user in admin_users:
                Notification.objects.create(
                    user=admin_user,
                    message=f"{confirmation.user.first_name}さんが住居・身上確認書の申請をしました。"
                )
                send_custom_email(subject='住居・身上確認書の申請', message=message, from_email=None, recipient_list=[admin_user.email])
            return super().form_valid(form)
        else:
            # 正常動作ではここは通らない。エラーページへの遷移でも良い
            return redirect(reverse_lazy('dashboard'))
    
    def form_invalid(self, form):
        print('Form is invalid')
        print('Errors:', form.errors)
        return super().form_invalid(form)

class BicycleCommuteView(LoginRequiredMixin, CreateView):
    """住居・身上確認書の申請ページ"""

    model = BicycleCommute
    form_class = BicycleCommuteForm
    template_name = 'request/bicycle_commute.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['userId'] = self.request.user.username
        context['employee_type'] = self.request.user.employee_type
        return context

    def form_valid(self, form):
        context = {'form': form, 'is_update': False}
        home_address = form.cleaned_data.get('current_address')
        # 申請内容の確認
        if self.request.POST.get('next', '') == 'confirm':
            is_valid, message, amount = is_bicycle_allowance(
                home_address=home_address,
            )
            context['calc_amount'] = amount
            if not is_valid:
                context['error_message'] = message
            return render(self.request, 'request/confirm_bicycle_commute.html', context)

        # 申請内容の修正
        if self.request.POST.get('next', '') == 'back':
            return render(self.request, 'request/bicycle_commute.html', context)
        
        # 申請内容の保存
        if self.request.POST.get('next', '') == 'create':
            bicycleCommute = form.save(commit=False)
            bicycleCommute.user = self.request.user
            _, _, amount = is_bicycle_allowance(home_address=bicycleCommute.current_address)
            bicycleCommute.amount = amount
            bicycleCommute.save()
            admin_users = CustomUser.objects.filter(is_staff=True)
            message = f"{bicycleCommute.user.first_name}さんが自転車通勤の申請をしました。\n確認お願いします。\nログインはこちら: {LOGIN_URL}"
            for admin_user in admin_users:
                Notification.objects.create(
                    user=admin_user,
                    message=f"{bicycleCommute.user.first_name}さんが自転車通勤の申請をしました"
                )
                send_custom_email(subject='自転車通勤の申請', message=message, from_email=None, recipient_list=[admin_user.email])
            return super().form_valid(form)
        else:
            # 正常動作ではここは通らない。エラーページへの遷移でも良い
            return redirect(reverse_lazy('dashboard'))
    
    def form_invalid(self, form):
        print('Form is invalid')
        print('Errors:', form.errors)
        return super().form_invalid(form)


class ApplicationListView(LoginRequiredMixin, ListView):
    """申請一覧ページ"""

    template_name = 'request/application_list.html'
    context_object_name = 'applications'

class PendingListView(ApplicationListView):
    """申請中の申請一覧ページ"""

    def get_queryset(self):
        # 申請中の申請を取得
        user = self.request.user

        confirmation_apps = Confirmation.objects.filter(user=user, status='pending')
        bicycle_commute_apps = BicycleCommute.objects.filter(user=user, status='pending')

        # 全ての申請を結合して日付順にソート
        all_applications = sorted(
            chain(confirmation_apps, bicycle_commute_apps),
            key=lambda x: x.updated_at,
            reverse=True
        )
        return all_applications
    

class RejectingListView(ApplicationListView):
    """差し戻しの申請一覧ページ"""

    def get_queryset(self):
        # 差し戻しの申請を取得
        user = self.request.user

        confirmation_apps = Confirmation.objects.filter(user=user, status='rejected')
        bicycle_commute_apps = BicycleCommute.objects.filter(user=user, status='rejected')

        # 全ての申請を結合して日付順にソート
        all_applications = sorted(
            chain(confirmation_apps, bicycle_commute_apps),
            key=lambda x: x.updated_at,
            reverse=True
        )
        return all_applications

class ApprovedListView(ApplicationListView):
    """承認済みの申請一覧ページ"""

    def get_queryset(self):
        # 承認済みの申請を取得
        user = self.request.user
        if user.is_staff:
            confirmation_apps = Confirmation.objects.filter(status='approved')
            bicycle_commute_apps = BicycleCommute.objects.filter(status='approved')
        else:
            confirmation_apps = Confirmation.objects.filter(user=user, status='approved')
            bicycle_commute_apps = BicycleCommute.objects.filter(user=user, status='approved')

        # 全ての申請を結合して日付順にソート
        all_applications = sorted(
            chain(confirmation_apps, bicycle_commute_apps),
            key=lambda x: x.updated_at,
            reverse=True
        )
        return all_applications

class UnprocessingListView(ApplicationListView):
    """未処理の申請一覧ページ"""

    def get_queryset(self):
        confirmation_apps = Confirmation.objects.filter(status='pending')
        bicycle_commute_apps = BicycleCommute.objects.filter(status='pending')

        # 全ての申請を結合して日付順にソート
        all_applications = sorted(
            chain(confirmation_apps, bicycle_commute_apps),
            key=lambda x: x.updated_at,
            reverse=True
        )
        return all_applications

    

class ApplicationDetailView(LoginRequiredMixin, DetailView):
    """申請の詳細ページ"""

    template_name = 'request/application_detail.html'
    context_object_name = 'application'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application_type'] = self.application_type
        return context

class ConfirmationDetailView(ApplicationDetailView):
    """住居・身上確認書の詳細ページ"""

    model = Confirmation
    application_type = '住居・身上確認書'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_object = self.object
        if self.request.user.is_staff and self.object.status == 'pending':
            # 通勤経路のチェック
            is_valid, message = is_commute_allowance(
                home_address=self.object.address,
                transportation_type=self.object.transportation_type,
                route_json=self.object.route_json,
                economic_route_json=self.object.economic_route_json,
                is_bicycle_commute=self.object.is_bicycle_commute,
                bus_route_json=self.object.bus_route_json,
            )
            context['route_check'] = {
                'is_valid': is_valid,
                'message': message
            }
        # 次のオブジェクトを取得
        next_object = current_object.get_next_application(user=self.request.user)
        # 前のオブジェクトを取得
        previous_object = current_object.get_previous_application(user=self.request.user)

        # コンテキストに追加
        context['next_object'] = next_object
        context['previous_object'] = previous_object
        return context
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('dashboard')
        
        application = self.get_object()
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        if action == 'approve':
            application.status = 'approved'
            application.approval_date = application.updated_at
            message = f"住居・身上確認書が承認されました。\n確認お願いします。\nログインはこちら: {LOGIN_URL}"
            Notification.objects.create(user=application.user, message="住居・身上確認書が承認されました。")
            send_custom_email(subject='住居・身上確認書の承認', message=message, from_email=None, recipient_list=[application.user.email])
        elif action == 'reject':
            application.status = 'rejected'
            message = f"住居・身上確認書が差し戻されました。\n確認お願いします。\nログインはこちら: {LOGIN_URL}"
            Notification.objects.create(user=application.user, message="住居・身上確認書が差し戻されました。")
            send_custom_email(subject='住居・身上確認書の差し戻し', message=message, from_email=None, recipient_list=[application.user.email])
        application.remarks = comment

        application.save()

        return redirect('request:unprocessing_list')

# 自転車通勤申請書詳細ビュー
class BicycleCommuteDetailView(ApplicationDetailView):
    """自転車通勤申請書の詳細ページ"""

    model = BicycleCommute
    application_type = '自転車通勤申請書'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_object = self.object
        if self.request.user.is_staff and self.object.status == 'pending':
            # 通勤経路のチェック
            is_valid, message, amount = is_bicycle_allowance(
                home_address=self.object.current_address,
            )
            context['route_check'] = {
                'is_valid': is_valid,
                'message': message
            }
        # 次のオブジェクトを取得
        next_object = current_object.get_next_application(user=self.request.user)

        # 前のオブジェクトを取得
        previous_object = current_object.get_previous_application(user=self.request.user)

        # コンテキストに追加
        context['next_object'] = next_object
        context['previous_object'] = previous_object
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('dashboard')
        
        application = self.get_object()
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        if action == 'approve':
            application.status = 'approved'
            application.approval_date = application.updated_at
            message = f"自転車通勤申請書が承認されました。\n確認お願いします。\nログインはこちら: {LOGIN_URL}"
            Notification.objects.create(user=application.user, message="自転車通勤申請書が承認されました。")
            send_custom_email(subject='自転車通勤申請書の承認', message=message, from_email=None, recipient_list=[application.user.email])
        elif action == 'reject':
            application.status = 'rejected'
            message = f"自転車通勤申請書が差し戻されました。\n確認お願いします。\nログインはこちら: {LOGIN_URL}"
            Notification.objects.create(user=application.user, message="自転車通勤申請書が差し戻されました。")
            send_custom_email(subject='自転車通勤申請書の差し戻し', message=message, from_email=None, recipient_list=[application.user.email])
        application.remarks = comment

        application.save()

        return redirect('request:unprocessing_list')
    
class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    """申請の更新"""

    template_name = 'request/application_update.html'
    context_object_name = 'application'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application_type'] = self.application_type
        return context


class ConfirmationUpdateView(ApplicationUpdateView):
    """住居・身上確認書の更新"""
    
    model = Confirmation
    form_class = ConfirmationForm
    success_url = reverse_lazy('request:pending_list')
    application_type = '住居・身上確認書'

    def form_valid(self, form):
        application = form.instance
        pk = application.pk  
        
        context = {
            'form': form,
            'is_update': True,
            'application_pk': pk,  
        }
        home_address = form.cleaned_data.get('address')
        is_bicycle_commute = form.cleaned_data.get('is_bicycle_commute')
        transportation_type = form.cleaned_data.get('transportation_type')
        route_json = form.cleaned_data.get('route_json', {})
        economic_route_json = form.cleaned_data.get('economic_route_json', {})
        bus_route_json = form.cleaned_data.get('bus_route_json', {})
        if self.request.POST.get('next', '') == 'confirm':
            is_valid, message = is_commute_allowance(
                home_address=home_address,
                transportation_type=transportation_type,
                route_json=route_json,
                economic_route_json=economic_route_json,
                is_bicycle_commute=is_bicycle_commute,
                bus_route_json=bus_route_json,
            )
            if not is_valid:
                context['error_message'] = message
            return render(self.request, 'request/confirm_confirmation.html', context)
        if self.request.POST.get('next', '') == 'back':
            context = {
                'form': form,
                'application': self.get_object(),
                'application_type': self.application_type
            }
            return render(self.request, 'request/application_update.html', context)
        if self.request.POST.get('next', '') == 'create':
            confirmation = form.save(commit=False)
            confirmation.user = self.request.user
            confirmation.status = 'pending'
            confirmation.remakrs = ''
            if confirmation.is_bicycle_commute:
                confirmation.commute_route = ''
                confirmation.transportation_type = 'bicycle'
                confirmation.bus_route = ''
                confirmation.route_json = {}
                confirmation.bus_route_json = {}
                confirmation.economic_route_json = {}
            else:
                if confirmation.transportation_type != 'bus':
                    confirmation.bus_route = ''
                    confirmation.bus_route_json = {}
            confirmation.save()
            admin_users = CustomUser.objects.filter(is_staff=True)
            message = f"{confirmation.user.first_name}さんが住居・身上確認書の申請をしました。\n確認お願いします。\nログインはこちら: {LOGIN_URL}"
            for admin_user in admin_users:
                Notification.objects.create(
                    user=admin_user,
                    message=f"{confirmation.user.first_name}さんが住居・身上確認書の申請をしました。")
                send_custom_email(subject='住居・身上確認書の申請', message=message, from_email=None, recipient_list=[admin_user.email])
            return super().form_valid(form)
        else:
            # 正常動作ではここは通らない。エラーページへの遷移でも良い
            return redirect(reverse_lazy('dashboard'))
    
    def form_invalid(self, form):
        print('Form is invalid')
        print('Errors:', form.errors)
        return super().form_invalid(form)

class BicycleCommuteUpdateView(ApplicationUpdateView):
    """自転車通勤申請書の更新"""
        
    model = BicycleCommute
    form_class = BicycleCommuteForm
    success_url = reverse_lazy('request:pending_list')
    application_type = '自転車通勤申請書'

    def form_valid(self, form):
        application = form.instance
        pk = application.pk  
        
        context = {
            'form': form,
            'is_update': True,
            'application_pk': pk,  
        }
        home_address = form.cleaned_data.get('current_address')
        if self.request.POST.get('next', '') == 'confirm':
            is_valid, message, amount = is_bicycle_allowance(
                home_address=home_address,
            )
            context['calc_amount'] = amount
            if not is_valid:
                context['error_message'] = message
            return render(self.request, 'request/confirm_bicycle_commute.html', context)
        if self.request.POST.get('next', '') == 'back':
            context = {
                'form': form,
                'application': self.get_object(),
                'application_type': self.application_type
            }
            return render(self.request, 'request/application_update.html', context)
        if self.request.POST.get('next', '') == 'create':
            bicycleCommute = form.save(commit=False)
            bicycleCommute.user = self.request.user
            bicycleCommute.status = 'pending'
            bicycleCommute.remarks = ''
            _, _, amount = is_bicycle_allowance(home_address=bicycleCommute.current_address)
            bicycleCommute.amount = amount
            bicycleCommute.save()
            admin_users = CustomUser.objects.filter(is_staff=True)
            message = f"{bicycleCommute.user.first_name}さんが自転車通勤の申請をしました。\n確認お願いします。\nログインはこちら: {LOGIN_URL}"
            for admin_user in admin_users:
                Notification.objects.create(
                    user=admin_user,
                    message=f"{bicycleCommute.user.first_name}さんが自転車通勤の申請をしました。")
                send_custom_email(subject='自転車通勤の申請', message=message, from_email=None, recipient_list=[admin_user.email])
            return super().form_valid(form)
        else:
            # 正常動作ではここは通らない。エラーページへの遷移でも良い
            return redirect(reverse_lazy('dashboard'))
        
    def form_invalid(self, form):
        print('Form is invalid')
        print('Errors:', form.errors)
        return super().form_invalid(form)

class UnsubmittedListView(LoginRequiredMixin, ListView):
    """未提出の内定者リストを表示"""
    template_name = 'request/unsubmitted_list.html'
    context_object_name = 'unsubmitted_users'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # 入社予定日が近い未提出の内定者を抽出
            near_joining_date = 30  # 入社30日前から対象とする
            
            # 内定者のみ、かつ入社日が近い未提出ユーザーを抽出
            pending_users = CustomUser.objects.filter(
                employee_type='内定者',
                date_of_joining__isnull=False,
                date_of_joining__lte=timezone.now().date() + timedelta(days=near_joining_date)
            )
        else:
            pending_users = [user]

        # 未提出のユーザーをフィルタリング
        unsubmitted_users = []
        for user in pending_users:
            # 住居・身上確認書が未承認
            confirmation_submitted = Confirmation.objects.filter(
                user=user, 
                status='approved'
            ).exists()

            # 自転車通勤の場合は自転車通勤申請書も確認
            is_bicycle_commute = Confirmation.objects.filter(
                user=user, 
                is_bicycle_commute=True
            ).first()

            bicycle_submitted = True
            if is_bicycle_commute:
                bicycle_submitted = BicycleCommute.objects.filter(
                    user=user, 
                    status='approved'
                ).exists()

            # 両方未提出の場合リストに追加
            if not (confirmation_submitted and bicycle_submitted):
                unsubmitted_users.append(user)

        return unsubmitted_users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 追加情報を含むリストを作成
        enhanced_users = []
        for user in context['unsubmitted_users']:
            # 自転車通勤情報を取得
            bicycle_commute_info = Confirmation.objects.filter(
                user=user, 
                is_bicycle_commute=True
            ).first()

            user_data = {
                'user': user,
                'is_bicycle_commute': bicycle_commute_info is not None,
                'bicycle_commute_details': bicycle_commute_info
            }
            enhanced_users.append(user_data)
        
        context['unsubmitted_users'] = enhanced_users
        return context

    












