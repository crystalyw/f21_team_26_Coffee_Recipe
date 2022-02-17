from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import fields
from web_project.models import Profile

MAX_UPLOAD_SIZE = 2500000


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, label='Username')
    password = forms.CharField(max_length=100, label='Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        # validate and confirm passwords match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        authenticated = authenticate(username=username, password=password)
        if not authenticated:
            raise forms.ValidationError('Error: Invalid Username or Password.')
        # print(username)
        # print(password)

        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, label='Username')
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    email = forms.CharField(max_length=100, label='E-mail', widget=forms.EmailInput)
    password = forms.CharField(max_length=100, label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100, label='Confirm', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        # check and confirm password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Error: Passwords did not match.')
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username):
            raise forms.ValidationError('Error: Username is already taken.')

        return username
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = {'zip_code', 'city', 'country', 'profile_pic'}
        labels = {
            'zip_code': 'Zipcode',
            'city': 'City',
            'country': 'Country',
            'profile_pic':'Profile Picture'
        }

    def clean(self):
        cleaned_data = super().clean()
        self.clean_picture()
        return cleaned_data
    
    def clean_picture(self):
        if self.cleaned_data['profile_pic'] != None:
            picture = self.cleaned_data['profile_pic']
            if not picture or not hasattr(picture, 'content_type'):
                raise forms.ValidationError('You must upload a picture')
            if not picture.content_type or not picture.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')
            if picture.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
            return picture


class SearchForm(forms.Form):
    search = forms.CharField(max_length=20, label=False)