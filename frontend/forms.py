from django import forms


class ReferralActivationForm(forms.Form):
    invite_code = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите реферальный код", "class": "form-control"}
        ),
    )


class VerifyCodeForm(forms.Form):
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите номер телефона", "class": "form-control"}
        ),
    )
    code = forms.CharField(
        max_length=4,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите код из смс", "class": "form-control"}
        ),
    )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")
        return phone
