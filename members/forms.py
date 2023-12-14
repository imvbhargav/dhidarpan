from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth.models import User
from blog.models import ProfileInfo
 
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'First Name'}),max_length = 20)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Last Name'}),max_length = 20)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email', 'password1', 'password2']

        widgets = {
            'username':forms.TextInput(attrs={'placeholder':'Username'}),
            'password1':forms.PasswordInput(attrs={'placeholder':'Password'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for key, field in self.fields.items():
            field.label=""
        self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder':'Password','id':'pass1'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'placeholder':'Retype Password','id':'pass2'})

class LoginForm(forms.Form):
    username = forms.CharField(max_length = 100,widget=forms.TextInput(attrs={'placeholder':'Username'}),label='')
    password = forms.CharField(max_length = 20,widget=forms.PasswordInput(attrs={'placeholder':'Password'}),label='')

class UserEditForm(UserChangeForm):
    username =forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username*'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email*'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'First Name*'}),max_length = 20)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Last Name*'}),max_length = 20)
    
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

class ProfileUpdateForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Bio'}),required=False)
    website_url = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'https://YourSite.com -Add full link'}),max_length = 200,required=False)
    facebook_url = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'https://Facebook.com/YourProfile -Add full link'}),max_length = 200,required=False)
    twitter_url = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'https://Twitter.com/YourProfile -Add full link'}),max_length = 200,required=False)
    youtube_url = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'https://YouTube.com/YourChannel -Add full link'}),max_length = 200,required=False)
    linkedin_url = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'https://LinkedIn.com/YourProfile -Add full link'}),max_length = 200,required=False)
    class Meta:
        model = ProfileInfo
        fields = ['bio','website_url','facebook_url','twitter_url','youtube_url','linkedin_url']