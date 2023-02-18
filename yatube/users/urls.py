import django.contrib.auth.views
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        django.contrib.auth.views.LogoutView.as_view(
            template_name='users/logged_out.html'
        ),
        name='logout'
    ),
    path(
        'signup/', views.SignUp.as_view(), name='signup'
    ),
    path(
        'login/',
        django.contrib.auth.views.LoginView.as_view(
            template_name='users/login.html'
        ),
        name='login'
    ),
    path(
        'password_change/',
        django.contrib.auth.views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change_form'
    ),
    path(
        'password_change/done/',
        django.contrib.auth.views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        django.contrib.auth.views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/',
        django.contrib.auth.views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        django.contrib.auth.views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        django.contrib.auth.views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
