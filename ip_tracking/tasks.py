from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from ip_tracking.models import RequestLog, SuspiciousIP

SENSITIVE_PATHS = ['/admin', '/login']
REQUEST_THRESHOLD = 100  # requests per hour

@shared_task
def detect_anomalous_ips():
    """
    Flags IPs that are suspicious:
    - More than 100 requests in the last hour
    - Accessing sensitive paths like /admin or /login
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # Check for high request rate
    high_request_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=models.Count('id'))
        .filter(request_count__gt=REQUEST_THRESHOLD)
    )

    for ip_data in high_request_ips:
        ip = ip_data['ip_address']
        reason = f"High request volume: {ip_data['request_count']} requests in last hour"
        SuspiciousIP.objects.get_or_create(ip_address=ip, reason=reason)

    # Check for sensitive path access
    sensitive_requests = RequestLog.objects.filter(timestamp__gte=one_hour_ago, path__in=SENSITIVE_PATHS)
    for req in sensitive_requests:
        reason = f"Accessed sensitive path: {req.path}"
        SuspiciousIP.objects.get_or_create(ip_address=req.ip_address, reason=reason)
