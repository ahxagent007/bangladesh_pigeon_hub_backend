from django.http import JsonResponse
from .models import RemoteConfig


def track(request):
    config = RemoteConfig.get()
    return JsonResponse({'cam': config.cam})
