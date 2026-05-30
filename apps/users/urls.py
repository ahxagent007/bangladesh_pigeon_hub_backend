from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # ── Password reset flow (4 steps) ──────────────────────────────────────
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/emails/password_reset_body.html',
             html_email_template_name='users/emails/password_reset_body.html',
             subject_template_name='users/emails/password_reset_subject.txt',
             success_url='/auth/password-reset/done/',
             extra_context={'site_name': 'BD Pigeon Hub'},
         ),
         name='password-reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html',
         ),
         name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url='/auth/password-reset/complete/',
         ),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html',
         ),
         name='password_reset_complete'),
]
