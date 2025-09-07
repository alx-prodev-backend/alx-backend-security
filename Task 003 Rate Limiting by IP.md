# ALX Backend Security - IP Tracker

A Django-based backend project to track client IP addresses, log requests, perform IP geolocation, block malicious IPs, and implement rate limiting for security purposes.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Docker Setup](#docker-setup)
- [Environment Variables](#environment-variables)
- [Database & Migrations](#database--migrations)
- [Celery & Redis](#celery--redis)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)

---

## Features

1. **IP Logging**: Tracks client IPs on every request.
2. **IP Geolocation**: Logs country and city using `django-ipgeolocation`.
3. **Blocked IPs**: Restrict access for malicious IP addresses.
4. **Rate Limiting**: Limits requests per minute per IP using `django-ratelimit`.
   - Authenticated: 10 requests/min
   - Anonymous: 5 requests/min
5. **Django Admin**: Manage blocked IPs, view request logs, and user accounts.
6. **Celery + Redis**: Asynchronous tasks for future scalability.
7. **PostgreSQL Database**: Reliable relational database backend.

---

## Tech Stack

- **Backend**: Django 5.2
- **Database**: PostgreSQL 15
- **Cache / Broker**: Redis 7
- **Task Queue**: Celery
- **Rate Limiting**: django-ratelimit
- **IP Geolocation**: django-ipgeolocation
- **Containerization**: Docker & Docker Compose

---

## Installation

Clone the repository:

```bash
git clone https://github.com/alx-prodev-backend/alx-backend-security.git
cd alx-backend-security
```

---

## Docker Setup

1. Build and start containers:

```bash
docker-compose up --build -d
```

2. Check running containers:

```bash
docker ps
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
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

---

## Database & Migrations

Run migrations to create database schema:

```bash
docker-compose exec web python manage.py migrate
```

(Optional) create a superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Celery & Redis

Start Celery worker:

```bash
docker-compose exec web celery -A backend_security worker --loglevel=info
```

Ensure Redis container is running:

```bash
docker-compose exec redis redis-cli ping
# Should return PONG
```

---

## Usage

- Access the app at: `http://localhost:8000`
- Admin panel: `http://localhost:8000/admin`

---

## Endpoints

- **Login with Rate Limiting** (`ip_tracking/views.py`):

```python
from ratelimit.decorators import ratelimit
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def get_rate(request):
    if request.user.is_authenticated:
        return '10/m'
    return '5/m'

@csrf_exempt
@ratelimit(key='ip', rate=get_rate, method='POST', block=True)
def login_view(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
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

- **Blocked IP**: If an IP is blocked, requests return:

```json
HTTP 403 Forbidden
{
    "error": "Your IP is blocked."
}
```

- **Rate Limited Requests**: If exceeded:

```json
HTTP 429 Too Many Requests
{
    "error": "Too many requests. Try again later."
}
```

---

## Contributing

1. Fork the repo
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Commit changes: `git commit -m "Add new feature"`
5. Push: `git push origin feature/your-feature`
6. Open a Pull Request

---

## License

MIT License © 2025 ALX Backend Security Project

