from django.contrib import admin
from .models import QRCode, Scan


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'short_code', 'total_scans', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'short_code', 'destination_url']
    readonly_fields = ['short_code', 'created_at', 'qr_image']


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ['qr_code', 'scanned_at', 'device_type', 'browser', 'os', 'ip_address']
    list_filter = ['device_type', 'scanned_at']
    search_fields = ['qr_code__name', 'ip_address', 'browser']
    readonly_fields = ['scanned_at']
