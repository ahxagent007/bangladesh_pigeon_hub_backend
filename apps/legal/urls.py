from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('privacy/',        TemplateView.as_view(template_name='legal/privacy.html'),        name='privacy-policy'),
    path('terms/',          TemplateView.as_view(template_name='legal/terms.html'),          name='terms-of-service'),
    path('delete-account/', TemplateView.as_view(template_name='legal/delete_account.html'), name='delete-account'),
    path('support/',        TemplateView.as_view(template_name='legal/support.html'),        name='support'),
    path('child-safety/',   TemplateView.as_view(template_name='legal/child_safety.html'),   name='child-safety'),
]
