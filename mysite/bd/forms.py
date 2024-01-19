from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(AuthenticationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "password")

class AddRankForm(forms.Form):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label='Select User')
    rank = forms.CharField(max_length=50, label='Rank')