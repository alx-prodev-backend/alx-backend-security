# ip_tracking/middleware.py
from django.utils import timezone
from ip_tracking.models import RequestLog
from ipware import get_client_ip  # مكتبة لاستخراج الـ IP

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
            client_ip = "0.0.0.0"

        RequestLog.objects.create(
            ip_address=client_ip,
            timestamp=timezone.now(),
            path=request.path
        )

        response = self.get_response(request)
        return response
