#############################################################################################################################################
# Getting all the Necessary imports.
import re, os, requests
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import UserRegisterForm, LoginForm, UserEditForm, ProfileUpdateForm
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from blog.models import ProfileInfo
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from .decorators import check_recaptcha
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.conf import settings
from dhidarpan.backends import EmailBackend
from django.views.generic.base import TemplateView
from blog.models import Subscribers
# Imports end
#############################################################################################################################################



#############################################################################################################################################
# Function to send the account actiavtion link to the newly registered user
def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('activate-email.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to you email {to_email} inbox and click on \
            received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')
# activateEmail end
#############################################################################################################################################



#############################################################################################################################################
# Function to receive the token and uique ID to activate the newly registered user
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        pinstance = ProfileInfo.objects.create(user_id=get_user_model().objects.get(email=user.email).id)
        pinstance.display_picture = '/profiles/NULL.png'
        pinstance.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
    return redirect('register')
# activate end
#############################################################################################################################################



#############################################################################################################################################
# Register view, to create page to register and handle registration request
@check_recaptcha
def register(request):
    if request.user.is_anonymous:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid()  and request.recaptcha_is_valid:
                email = form.cleaned_data.get('email')
                if get_user_model().objects.filter(email=email):
                    return render(request, 'registration/register.html', {'form': form,'mermsg':'Email already exists, try different one!'})
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                ######################### mail system ############################
                activateEmail(request, user, form.cleaned_data.get('email'))
                ##################################################################
                return redirect('login')
            else:
                return render(request, 'registration/register.html', {'form': form,'mermsg':form.errors})
        else:
            form = UserRegisterForm()
            return render(request, 'registration/register.html', {'form': form})
    return redirect('home')
# Register end
#############################################################################################################################################



#############################################################################################################################################
# Login view, to create page to login and handle login request
@check_recaptcha
def usr_login(request):
    if request.user.is_anonymous:
        if request.method == 'GET':
            lin_form = LoginForm()
            return render(request, 'registration/login.html', {'form': lin_form,'msg':''})
        else:
            lin_form = LoginForm(request.POST)
            if lin_form.is_valid() and request.recaptcha_is_valid:
                idInput = lin_form.cleaned_data.get('username')
                password = lin_form.cleaned_data.get('password')
                if valid_email(idInput):
                    email = lin_form.cleaned_data.get('username')
                    user = User.objects.filter(email=email)
                    if user.exists():
                        username = user[0].username
                    else:
                        return render(request, 'registration/login.html', {'form': lin_form,'msg':'Invalid Email!'})
                else:
                    username = lin_form.cleaned_data.get('username')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    # Redirect to a success page.
                    return redirect('pa-land')
                else:
                    lin_form = LoginForm()
                    return render(request, 'registration/login.html', {'form': lin_form,'msg':'Details incorrect!'})
            lin_form = LoginForm()
            return render(request, 'registration/login.html', {'form': lin_form,'msg':''})
    return redirect('home')
# Login end
#############################################################################################################################################



#############################################################################################################################################
# Function for logging out the user
def logout_view(request):
    if request.user.is_anonymous:
        return redirect('login')
    logout(request)
    # Redirect to a success page.
    return redirect('home')
# Logout end
#############################################################################################################################################



#############################################################################################################################################
# Function check if the username is valid
def check_username(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if get_user_model().objects.filter(username=username):
            return HttpResponse("<div style='color:red;padding-left:2%;'><small><b> Username already exists!</b></small></div>")
        else:
            if " " in username:
                return HttpResponse("<div style='color:red;padding-left:2%;'><small><b> Username can not have Whitespaces!</b></small></div>")
            return HttpResponse("<div style='color:green; padding-left:2%;'><small><b> Username is available!</b></small></div")
    return redirect('register')
# check_username end
#############################################################################################################################################



#############################################################################################################################################
# Function check if the email already user and is valid
def check_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if get_user_model().objects.filter(email=email):
            return HttpResponse("<div style='color:red;padding-left:2%;'><small><b> Email already exists!</b></small></div>")
        else:
            if not valid_email(email):
                return HttpResponse("<div style='color:red;padding-left:2%;'><small><b>  Enter Valid Email!</b></small></div>")
            return HttpResponse("<div style='color:green; padding-left:2%;'><small><b>  Email is available!</b></small></div")
    return redirect('register')
# check_email end
#############################################################################################################################################



#############################################################################################################################################
# Function to check is email is valid
def valid_email(email):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.match(pat, email):
        return True
    else:
        return False
# valid_email end
#############################################################################################################################################



#############################################################################################################################################
# Function to change password view
@login_required(login_url='/members/login/')
def change_password(request):
    if request.user.is_anonymous:
        return redirect('login')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/changepass.html', {'form': form})
# change_password end
#############################################################################################################################################



#############################################################################################################################################
# Function to handle user profile edit view
@login_required(login_url="/members/login/")
def edit_user_profile(request):
    id = request.user.id
    uinstance = User.objects.get(id=id)
    user_form = UserEditForm(request.POST or None, instance=uinstance)
    if user_form.is_valid():
        email = user_form.cleaned_data.get('email')
        uobj = get_user_model().objects.get(email=email)
        if uobj.id != id:
            pinstance = ProfileInfo.objects.get(user_id=id)
            profile_form = ProfileUpdateForm(request.POST or None,instance=pinstance)
            return render(request,'registration/edit_user.html',{'user_form':user_form,'profile_form':profile_form,'ermsg':'Enter a different Email!'})
        pinstance = ProfileInfo.objects.get(user_id=id)
        profile_form = ProfileUpdateForm(request.POST or None,instance=pinstance)
        user_form.save()
    if ProfileInfo.objects.filter(user_id = id).exists():
        pinstance = ProfileInfo.objects.get(user_id=id)
        profile_form = ProfileUpdateForm(request.POST or None,instance=pinstance)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('pa-land')
    else:
        pinstance = ProfileInfo.objects.create(user_id=id)
        profile_form = ProfileUpdateForm(request.POST or None,instance=pinstance)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('pa-land')
        profile_form = ProfileUpdateForm()
    return render(request,'registration/edit_user.html',{'user_form':user_form,'profile_form':profile_form})
# edit_user_profile end
#############################################################################################################################################



#############################################################################################################################################
# Function to update the display picture of logged in user
@login_required(login_url='/members/login/')
def updateDp(request,uid):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if image_file:
            pi = ProfileInfo.objects.get(user_id=uid)
            pi.display_picture = image_file
            pi.save_with_dp()

        if ProfileInfo.objects.filter(user_id = uid).exists():
            pinstance = ProfileInfo.objects.get(user_id=uid)
            profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None,instance=pinstance)
        else:
            pinstance = ProfileInfo.objects.create(user_id=uid)
            profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None,instance=pinstance)
        return render(request, 'registration/edit_user_model.html',{'profile_form':profile_form})
    return redirect('members/edit_user/'+str(uid))
# updateDp end
#############################################################################################################################################



#############################################################################################################################################
# Function to Delete display picture of logged in user
@login_required(login_url='/members/login/')
def deleteDp(request,uid):
    if request.method == 'DELETE':
        pi = ProfileInfo.objects.get(user_id=uid)
        pi.display_picture.delete()
        pi.display_picture = None
        pi.save_with_dp()
        if ProfileInfo.objects.filter(user_id = uid).exists():
            pinstance = ProfileInfo.objects.get(user_id=uid)
            profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None,instance=pinstance)
        else:
            pinstance = ProfileInfo.objects.create(user_id=uid)
            profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None,instance=pinstance)
        return render(request, 'registration/edit_user_model.html',{'profile_form':profile_form})
    return redirect('members/edit_user/'+str(uid))
# updateDp end
#############################################################################################################################################



#############################################################################################################################################
# Class handles password reset view
class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')
# ReserPasswordView end
#############################################################################################################################################



#############################################################################################################################################
# Handle template for confirming deleting user
class DeleteView(TemplateView):
    template_name = 'deleteUser.html'
# DeleteView end
#############################################################################################################################################



#############################################################################################################################################
# Function to delete the user
@login_required(login_url='/members/login/')
def delete_user(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)

    # Delete the profile picture
    pi = ProfileInfo.objects.get(user=user)
    pi.display_picture.delete()
    pi.display_picture = None

    # Delete the subscriber
    if Subscribers.objects.filter(email=user.email).exists():
        sub = Subscribers.objects.get(email=user.email)
        sub.delete()
        pi.save_with_dp()
    logout(request)
    user.delete()
    return redirect('home')
# delete_user end
#############################################################################################################################################



#############################################################################################################################################
# Function to handle Google SSO login
def google_sso_login(request):
    google_auth_url = generate_google_auth_url()
    return HttpResponseRedirect(google_auth_url)
# google_sso_login end
#############################################################################################################################################



#############################################################################################################################################
# Function to get the path to Google SSO login
def generate_google_auth_url():
    google_auth_base_url = 'https://accounts.google.com/o/oauth2/auth'
    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    scope = 'openid email profile'
    response_type = 'code'
    approval_prompt = 'force'

    auth_url = f'{google_auth_base_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}&approval_prompt={approval_prompt}'
    return auth_url
# generate_google_auth_url end
#############################################################################################################################################



#############################################################################################################################################
# Function to handle the callback of Google SSO
def google_sso_callback(request):
    auth_code = request.GET.get('code')
    access_token = exchange_code_for_token(auth_code)

    user_info = get_google_user_info(access_token)

    #Extract user info
    email = user_info.get('email')
    given_name = user_info.get('given_name')
    family_name = user_info.get('family_name')
    profilePictuteUrl = user_info.get('picture')
    
    #Create or get the user based on email
    user, created = User.objects.get_or_create(email=email, defaults={'username': given_name,'first_name': given_name, 'last_name': family_name})

    if created:
        user_id = get_user_model().objects.get(email=user.email).id
        image_path = download_and_save_picture(profilePictuteUrl, user_id)

        pinstance = ProfileInfo.objects.create(user_id=user_id)
        pinstance.display_picture = image_path
        pinstance.isGoogleUser = True
        pinstance.save()

    #log in the user
    user = EmailBackend.authenticate(ModelBackend(), request, email=email)
    if user is not None:
        login(request, user, backend='mysite.backends.EmailBackend')
        # Redirect to a success page.
        return redirect('pa-land')
    else:
        lin_form = LoginForm()
        return render(request, 'registration/login.html', {'form': lin_form,'msg':'Please use Normal Login, Google login not allowed!'})
# google_sso_callback end
#############################################################################################################################################



#############################################################################################################################################
# Funtion to exchange code to get google token
def exchange_code_for_token(code):
    token_url = 'https://oauth2.googleapis.com/token'
    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    client_secret = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    grant_type = 'authorization_code'
    params = {
        'code' : code,
        'client_id' : client_id,
        'client_secret' : client_secret,
        'redirect_uri' : redirect_uri,
        'grant_type' : grant_type,
    }

    response = requests.post(token_url, data=params)
    token_data = response.json()
    access_token = token_data.get('access_token')
    return access_token
# exchange_code_for_token end
#############################################################################################################################################



#############################################################################################################################################
# Function to get the information of google user
def get_google_user_info(access_token):
    user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    headers = {'Authorization' : f'Bearer {access_token}'}

    response = requests.get(user_info_url, headers=headers)
    user_info = response.json()

    return user_info
# get_google_user_info end
#############################################################################################################################################



#############################################################################################################################################
# Function downloads the picture from google profile and saved it in server
def download_and_save_picture(url, user_id):
    response = requests.get(url)
    image_path = os.path.join(settings.MEDIA_ROOT,f'profiles/{user_id}.jpg')
    with open(image_path, 'wb') as f:
        f.write(response.content)
    return image_path
# download_and_save_picture end
#############################################################################################################################################