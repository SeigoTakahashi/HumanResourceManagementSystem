from django import forms
from .models import Confirmation, BicycleCommute

class ConfirmationForm(forms.ModelForm):
    """住居・身上確認書のフォーム"""
    
    class Meta:
        model = Confirmation
        fields = [
            "name",
            "name_kana",
            "address",
            "address_kana",
            "is_bicycle_commute",
            "commute_route",
            "transportation_type",
            "bus_route",
            "route_json",
            "bus_route_json",
            "economic_route_json",
            "remarks",
            "commuting_expenses",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control custom-input",
                "id": "name",
                "required": True,
            }),
            "name_kana": forms.TextInput(attrs={
                "class": "form-control custom-input",
                "id": "nameKana",
                "required": True,
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control custom-input",
                "id": "address",
                "required": True,
            }),
            "address_kana": forms.TextInput(attrs={
                "class": "form-control custom-input",
                "id": "addressKana",
                "required": True,
            }),
            "is_bicycle_commute": forms.CheckboxInput(attrs={
                "class": "form-control custom-input",
                "id": "isBicycleCommute",
            }),
            "commute_route": forms.Textarea(attrs={
                "class": "form-control custom-input",
                "id": "commuteRoute",
                "rows": 3,
                "placeholder": "例: 船橋 －（JR 総武線）－ 西船橋 －（東京メトロ東西線）－ 東陽町",
                "style": "resize: vertical;",
                "readonly": True,
            }),
            "transportation_type": forms.RadioSelect(
                choices=Confirmation.TRANSPORTATION_CHOICES,
                attrs={
                    "class": "custom-control custom-radio",
                },
               
            ),
            "bus_route": forms.Textarea(attrs={
                "class": "form-control custom-input",
                "id": "busRoute",
                "rows": 3,
                "placeholder": "例: 船橋中央市場 －（新京成バス）－ 船橋駅北口",
                "readonly": True,
            }),
            "route_json": forms.HiddenInput(attrs={
                "id": "routeJson",  
            }),
            "bus_route_json": forms.HiddenInput(attrs={
                "id": "busRouteJson",
            }),
            "economic_route_json": forms.HiddenInput(attrs={
                "id": "economicRouteJson",
            }),
            "remarks": forms.Textarea(attrs={
                "class": "form-control custom-input",
                "id": "remarks",
                "rows": 3,
                "placeholder": "その他、ご要望等がございましたらご記入ください。",
                "style": "resize: vertical;",
            }),
            "commuting_expenses": forms.HiddenInput(attrs={
                "id": "commutingExpenses",
                "value": 0,
            }),
        }

class BicycleCommuteForm(forms.ModelForm):
    """自転車通勤申請書のフォーム"""
    
    class Meta:
        model = BicycleCommute
        fields = [
            "application_date",
            "employee_number",
            "name",
            "name_kana",
            "affiliation",
            "current_address",
            "amount",
            "remarks",
        ]
        widgets = {
            "application_date": forms.DateInput(attrs={
                "class": "form-control custom-input",
                "id": "applicationDate",
                "type": "date",
                "required": True,
            }),
            "employee_number": forms.TextInput(attrs={
                "class": "form-control custom-input",
                "id": "employeeNumber",
                "required": True,
            }),
            "name": forms.TextInput(attrs={
                "class": "form-control custom-input",
                "id": "name",
                "required": True,
            }),
            "name_kana": forms.TextInput(attrs={
                "class": "form-control custom-input",
                "id": "nameKana",
                "required": True,
            }),
            "affiliation": forms.TextInput(attrs={
                "class": "form-control custom-input",
                "id": "affiliation",
                "required": True,
            }),
            "current_address": forms.TextInput(attrs={
                "class": "form-control custom-input",
                "id": "currentAddress",
                "required": True,
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control custom-input",
                "id": "amount",
                "value": 0,
                "required": False,
                "readonly": True,
            }),
            "remarks": forms.Textarea(attrs={
                "class": "form-control custom-input",
                "id": "remarks",
                "rows": 3,
                "placeholder": "その他、ご要望等がございましたらご記入ください。",
                "style": "resize: vertical;",
            }),
        }
    
