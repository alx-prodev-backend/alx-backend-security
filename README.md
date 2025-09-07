# ALX Backend Security Project - IP Tracker

## Overview
IP tracking is a critical technique for enhancing security, understanding user behavior, and maintaining legal compliance in web applications. This Django project demonstrates how to log, blacklist, geolocate, rate limit, and analyze IP addresses responsibly and efficiently.  

Learners gain practical experience using Django tools, middleware, Celery tasks, and third-party libraries to build secure and privacy-conscious IP tracking systems.

---

## Learning Objectives
By the end of this project, learners will be able to:

- Understand the role of IP tracking in web security and analytics.
- Implement request logging using Django middleware.
- Blacklist malicious IPs and manage access control.
- Use IP geolocation to enhance personalization and fraud detection.
- Apply rate limiting techniques to prevent abuse.
- Detect anomalies using log data and scheduled tasks.
- Address privacy, compliance, and ethical considerations.

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| IP Logging | Logs IPs, timestamps, and request paths for auditing and debugging. |
| Blacklisting | Blocks known bad actors from accessing the application. |
| IP Geolocation | Maps IPs to geographic data to improve security and UX. |
| Rate Limiting | Prevents abuse by restricting request rates. |
| Anomaly Detection | Identifies unusual traffic patterns to catch early threats. |
| Privacy & Ethics | Ensures tracking aligns with legal and ethical standards. |

---

## Tasks

### Task 0: Basic IP Logging Middleware
**Objective:**  
Implement middleware to log the IP address, timestamp, and path of every incoming request.

**Instructions:**  
- Create `ip_tracking/middleware.py` with a middleware class that logs request details.  
- Define `ip_tracking/models.py` with a `RequestLog` model:
```python
class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
```
- Register the middleware in `settings.py`.

**Repo:**  
- Directory: `ip_tracking`  
- Files: `middleware.py`, `models.py`

---

### Task 1: IP Blacklisting
**Objective:**  
Implement IP blocking based on a blacklist.

**Instructions:**  
- Create `BlockedIP` model in `ip_tracking/models.py`:
```python
class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    blocked_at = models.DateTimeField(auto_now_add=True)
```
- Update `IPLoggingMiddleware` to block requests from `BlockedIP` entries. Return HTTP 403.  
- Create management command `ip_tracking/management/commands/block_ip.py` to add IPs to the blacklist.

**Repo:**  
- Directory: `ip_tracking`  
- Files: `middleware.py`, `management/commands/block_ip.py`

---

### Task 2: IP Geolocation Analytics
**Objective:**  
Enhance logging with geolocation data (country, city).

**Instructions:**  
- Install `django-ipgeolocation`.  
- Extend `RequestLog` with `country` and `city` fields:
```python
country = models.CharField(max_length=100, blank=True, null=True)
city = models.CharField(max_length=100, blank=True, null=True)
```
- Update middleware to populate these fields using the geolocation API. Cache results for 24 hours.

**Repo:**  
- Directory: `ip_tracking`  
- Files: `models.py`, `middleware.py`

---

### Task 3: Rate Limiting by IP
**Objective:**  
Implement rate limiting to prevent abuse.

**Instructions:**  
- Install `django-ratelimit`.  
- Configure rate limits:
  - Authenticated: 10 requests/min  
  - Anonymous: 5 requests/min
- Apply to sensitive views like login in `ip_tracking/views.py`:
```python
from ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

def get_rate(request):
    return '10/m' if request.user.is_authenticated else '5/m'

@csrf_exempt
@ratelimit(key='ip', rate=get_rate, method='POST', block=True)
def login_view(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'error': 'Too many requests. Try again later.'}, status=429)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({'success': 'Logged in successfully'})
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    return JsonResponse({'error': 'POST request required'}, status=400)
```

**Repo:**  
- Directory: `ip_tracking`  
- Files: `views.py`, `settings.py`

---

### Task 4: Anomaly Detection
**Objective:**  
Implement anomaly detection to flag suspicious IPs.

**Instructions:**  
- Create a Celery task in `ip_tracking/tasks.py` to run hourly:
```python
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalous_ips():
    one_hour_ago = timezone.now() - timedelta(hours=1)
    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)
    ip_counts = {}
    for log in logs:
        ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1
        if log.path in ['/admin', '/login']:
            SuspiciousIP.objects.get_or_create(ip_address=log.ip_address, reason=f"Accessed {log.path}")
    for ip, count in ip_counts.items():
        if count > 100:
            SuspiciousIP.objects.get_or_create(ip_address=ip, reason="Exceeded 100 requests/hour")
```
- Create `SuspiciousIP` model in `ip_tracking/models.py`:
```python
class SuspiciousIP(models.Model):
    ip_address = models.GenericIPAddressField()
    reason = models.TextField()
    flagged_at = models.DateTimeField(auto_now_add=True)
```

**Repo:**  
- Directory: `ip_tracking`  
- Files: `tasks.py`, `models.py`

---

## Installation

### Prerequisites
- Docker & Docker Compose  
- Python 3.11  
- PostgreSQL  
- Redis  

### Setup
1. Clone the repository:
```bash
git clone https://github.com/alx-prodev-backend/alx-backend-security.git
cd alx-backend-security
```
2. Create `.env` file with database and Redis configuration:
```dotenv
DEBUG=0
SECRET_KEY=your_super_secret_key
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 192.168.100.24

DATABASE_NAME=iptracker
DATABASE_USER=ipuser
DATABASE_PASSWORD=ippassword
DATABASE_HOST=db
DATABASE_PORT=5432

REDIS_URL=redis://redis:6379/0
```
3. Build and run containers:
```bash
docker-compose up --build -d
```
4. Apply migrations and collect static files:
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```
5. Monitor logs:
```bash
docker-compose logs -f web
```

---

## Dependencies
- Django >=5.2  
- psycopg2-binary  
- Redis  
- Celery  
- django-ipgeolocation  
- django-ratelimit  
- ipware  

---

## Project Structure
```
alx-backend-security/
│
├─ ip_tracking/
│   ├─ models.py           # RequestLog, BlockedIP, SuspiciousIP
│   ├─ middleware.py       # IPLoggingMiddleware
│   ├─ tasks.py            # Celery anomaly detection tasks
│   ├─ views.py            # Login & rate-limited views
│
├─ backend_security/
│   ├─ settings.py
│   ├─ urls.py
│   └─ wsgi.py
│
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ .env
```

---

## License
MIT License

---

## Author
ALX Backend ProDev Student
