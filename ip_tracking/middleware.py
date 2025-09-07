from django.utils import timezone
from django.http import HttpResponseForbidden
from ipware import get_client_ip
from django.core.cache import cache
from ip_tracking.models import RequestLog, BlockedIP
import requests


class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # الحصول على IP العميل
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
            client_ip = "0.0.0.0"

        # التحقق من حظر IP
        if BlockedIP.objects.filter(ip_address=client_ip).exists():
            return HttpResponseForbidden("Your IP is blocked.")

        # محاولة استرجاع بيانات الجغرافيا من الكاش
        geo_data = cache.get(client_ip)
        if not geo_data:
            try:
                response = requests.get(
                    f"https://ipgeolocation.abstractapi.com/v1/?api_key=YOUR_API_KEY&ip_address={client_ip}"
                )
                if response.status_code == 200:
                    data = response.json()
                    geo_data = {
                        "country": data.get("country"),
                        "city": data.get("city")
                    }
                else:
                    geo_data = {"country": None, "city": None}
            except Exception:
                geo_data = {"country": None, "city": None}

            # تخزين النتائج في الكاش لمدة 24 ساعة
            cache.set(client_ip, geo_data, 24 * 3600)

        # تسجيل الطلب في قاعدة البيانات مع البلد والمدينة
        RequestLog.objects.create(
            ip_address=client_ip,
            timestamp=timezone.now(),
            path=request.path,
            country=geo_data.get("country"),
            city=geo_data.get("city")
        )

        response = self.get_response(request)
        return response
