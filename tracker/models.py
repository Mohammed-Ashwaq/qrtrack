import uuid
from django.db import models
from django.contrib.auth.models import User


class QRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qrcodes')
    name = models.CharField(max_length=200)
    destination_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=12, unique=True)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # No expiry field — QR codes are permanent by design

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def total_scans(self):
        return self.scans.count()

    @property
    def unique_scans(self):
        return self.scans.values('ip_address').distinct().count()


class Scan(models.Model):
    DEVICE_CHOICES = [
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
        ('bot', 'Bot'),
        ('unknown', 'Unknown'),
    ]

    qr_code = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name='scans')
    scanned_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_CHOICES, default='unknown')
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    referer = models.URLField(max_length=2000, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-scanned_at']

    def __str__(self):
        return f"Scan of {self.qr_code.name} at {self.scanned_at}"
