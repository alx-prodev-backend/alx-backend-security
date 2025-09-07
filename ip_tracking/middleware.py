# ip_tracking/middleware.py
from django.utils import timezone
from django.http import HttpResponseForbidden
from ipware import get_client_ip
from ip_tracking.models import RequestLog, BlockedIP


class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
            client_ip = "0.0.0.0"

        #
        if BlockedIP.objects.filter(ip_address=client_ip).exists():
            return HttpResponseForbidden("Your IP is blocked.")

        # recording request in database
        RequestLog.objects.create(
            ip_address=client_ip,
            timestamp=timezone.now(),
            path=request.path
        )

        response = self.get_response(request)
        return response
