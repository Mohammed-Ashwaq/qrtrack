from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta
import json

from .models import QRCode, Scan
from .utils import generate_short_code, generate_qr_image, get_client_ip, parse_user_agent
from .forms import QRCodeForm, SignUpForm


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def redirect_qr(request, short_code):
    """Track scan and redirect to destination."""
    qr = get_object_or_404(QRCode, short_code=short_code)

    ip = get_client_ip(request)
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    device_type, browser, os_name = parse_user_agent(ua_string)
    referer = request.META.get('HTTP_REFERER', '')

    Scan.objects.create(
        qr_code=qr,
        ip_address=ip,
        user_agent=ua_string,
        device_type=device_type,
        browser=browser,
        os=os_name,
        referer=referer,
    )

    return redirect(qr.destination_url)


@login_required
def dashboard(request):
    qrcodes = QRCode.objects.filter(user=request.user).annotate(
        scan_count=Count('scans')
    )
    total_qrs = qrcodes.count()
    total_scans = sum(q.scan_count for q in qrcodes)

    # Scans over last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_scans = (
        Scan.objects.filter(qr_code__user=request.user, scanned_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('scanned_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    daily_data = {str(s['date']): s['count'] for s in daily_scans}

    # Fill all 30 days
    dates, counts = [], []
    for i in range(29, -1, -1):
        d = (timezone.now() - timedelta(days=i)).date()
        dates.append(str(d))
        counts.append(daily_data.get(str(d), 0))

    context = {
        'qrcodes': qrcodes,
        'total_qrs': total_qrs,
        'total_scans': total_scans,
        'chart_dates': json.dumps(dates),
        'chart_counts': json.dumps(counts),
    }
    return render(request, 'dashboard.html', context)


@login_required
def create_qr(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            qr_obj = form.save(commit=False)
            qr_obj.user = request.user

            # Generate unique short code
            while True:
                code = generate_short_code()
                if not QRCode.objects.filter(short_code=code).exists():
                    break
            qr_obj.short_code = code

            # Build tracking URL
            tracking_url = request.build_absolute_uri(f'/r/{code}/')

            # Generate QR image
            qr_obj.qr_image = generate_qr_image(tracking_url, code)
            qr_obj.save()

            messages.success(request, 'QR code created successfully!')
            return redirect('qr_detail', short_code=code)
    else:
        form = QRCodeForm()
    return render(request, 'create_qr.html', {'form': form})


@login_required
def qr_detail(request, short_code):
    qr = get_object_or_404(QRCode, short_code=short_code, user=request.user)

    # All-time scans by day
    daily_scans = (
        qr.scans.annotate(date=TruncDate('scanned_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    daily_data = {str(s['date']): s['count'] for s in daily_scans}

    # Last 30 days
    dates, counts = [], []
    for i in range(29, -1, -1):
        d = (timezone.now() - timedelta(days=i)).date()
        dates.append(str(d))
        counts.append(daily_data.get(str(d), 0))

    # Device breakdown
    device_data = (
        qr.scans.values('device_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    device_labels = [d['device_type'].capitalize() for d in device_data]
    device_counts = [d['count'] for d in device_data]

    # Browser breakdown
    browser_data = (
        qr.scans.values('browser')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    # OS breakdown
    os_data = (
        qr.scans.values('os')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    # Recent scans
    recent_scans = qr.scans.all()[:20]

    tracking_url = request.build_absolute_uri(f'/r/{short_code}/')

    context = {
        'qr': qr,
        'tracking_url': tracking_url,
        'chart_dates': json.dumps(dates),
        'chart_counts': json.dumps(counts),
        'device_labels': json.dumps(device_labels),
        'device_counts': json.dumps(device_counts),
        'browser_data': list(browser_data),
        'os_data': list(os_data),
        'recent_scans': recent_scans,
    }
    return render(request, 'qr_detail.html', context)


@login_required
def delete_qr(request, short_code):
    qr = get_object_or_404(QRCode, short_code=short_code, user=request.user)
    if request.method == 'POST':
        qr.delete()
        messages.success(request, 'QR code deleted.')
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'qr': qr})
