from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Accounts
from django.contrib.auth import authenticate

class UserSignUpForm(UserCreationForm):
    email=forms.EmailField(max_length=100,help_text='required')

    class Meta:
        model=Accounts
        fields=('username','email','password1','password2')

    def clean(self,*args,**kwargs):
        email=self.cleaned_data.get('email')
        email_qs=Accounts.objects.filter(email=email)
        if email_qs.exists(): self.add_error('email','This email has been registered')
        return super(UserSignUpForm,self).clean(*args,**kwargs)

class UserLogInForm(forms.Form):
    username=forms.CharField(label=('Username'),required=True)
    password=forms.CharField(label=('Password'),widget=forms.PasswordInput,required=True)