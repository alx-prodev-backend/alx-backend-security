# ip_tracking/views.py
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
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
