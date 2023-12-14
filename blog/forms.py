from django.core.mail import message
from .models import *
from django import forms
from django_summernote.widgets import SummernoteWidget
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name','email','body')

        labels = {
            'name':'',
            'email':'',
            'body':'',
        }

        widgets = {
            'name':forms.TextInput(attrs={'class':'cname','id':'cnam','placeholder':'Your Name'}),
            'email':forms.EmailInput(attrs={'class':'cemail','id':'cmail','placeholder':'Your Email'}),
            'body':forms.Textarea(attrs={'class':'cbody','id':'cmbdy','placeholder':'Type your comment...'}),
        }

class ContactForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'First Name','class':'ct'}),label='',max_length=50, required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Last Name','class':'ct'}),label='',max_length=50, required=True)
    email_address= forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'YourEmail@provider.com','class':'ct'}),label='',max_length=200,required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Type your message....','class':'ct'}),label='',max_length=2000, required=True)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title','slug','thumbnail','categories','author','content')

        labels = {
            'title':'',
            'slug':'',
            'thumbnail':'',
            'categories':'',
            'author':'',
            'content':'',
        }

        widgets = {
            'title':forms.TextInput(attrs={'class':'pftitle','id':'pftit','value':'','placeholder':'Enter the title of post....'}),
            'slug':forms.TextInput(attrs={'class':'pfslug','id':'pfslg','value':'','type':'hidden'}),
            'thumbnail':forms.FileInput(attrs={'class':'pfthumb','id':'pftbnl'}),
            'categories':forms.Select(attrs={'class':'pfcategory','id':'pfcate','value':''}),
            'author':forms.TextInput(attrs={'class':'pfauthor','id':'pfath','value':'','type':'hidden'}),
            'content':SummernoteWidget(attrs={'class':'smte'}),
        }

class UpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title','slug','thumbnail','content')

        labels = {
            'title':'',
            'slug':'',
            'thumbnail':'',
            'author':'',
            'content':'',
        }

        widgets = {
            'title':forms.TextInput(attrs={'class':'pftitle','id':'pftit','value':'','placeholder':'Enter the title of post....'}),
            'slug':forms.TextInput(attrs={'class':'pfslug','id':'pfslg','value':'','type':'hidden'}),
            'thumbnail':forms.FileInput(attrs={'class':'pfthumb','id':'pftbnl'}),
            'content':SummernoteWidget(attrs={'class':'smte'}),
        }


class EditUserForm(forms.ModelForm):
    class Meta:
        model = ProfileInfo
        fields = ('bio','display_picture','website_url','facebook_url','twitter_url','youtube_url','linkedin_url')