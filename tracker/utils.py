import io
import random
import string
import qrcode
import qrcode.image.svg
from django.core.files.base import ContentFile
from PIL import Image


def generate_short_code(length=8):
    """Generate a unique short code for QR tracking URL."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_qr_image(url, short_code):
    """Generate a styled QR code image and return as ContentFile."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="#0f172a",
        back_color="white"
    ).convert('RGBA')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return ContentFile(buffer.read(), name=f'{short_code}.png')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def parse_user_agent(ua_string):
    """Parse user agent string and return device info."""
    try:
        from user_agents import parse
        ua = parse(ua_string)
        if ua.is_bot:
            device_type = 'bot'
        elif ua.is_mobile:
            device_type = 'mobile'
        elif ua.is_tablet:
            device_type = 'tablet'
        elif ua.is_pc:
            device_type = 'desktop'
        else:
            device_type = 'unknown'

        browser = ua.browser.family or 'Unknown'
        os_name = ua.os.family or 'Unknown'
        return device_type, browser, os_name
    except Exception:
        return 'unknown', 'Unknown', 'Unknown'
