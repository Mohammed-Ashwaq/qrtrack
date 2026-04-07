# QR.track — Django QR Code Analytics Platform

A full-featured Django application for creating permanent, trackable QR codes with a real-time analytics dashboard.

---

## Features

- **Permanent QR Codes** — No expiry, ever. Once created, your QR code works forever.
- **Scan Tracking** — Every scan logs device type, browser, OS, IP address, and timestamp.
- **Analytics Dashboard** — 30-day scan timeline, device breakdown (doughnut chart), browser/OS stats, recent scans table.
- **Multi-user** — Each user has their own QR codes and private analytics.
- **QR Image Download** — PNG QR codes downloadable directly from the UI.
- **Django Admin** — Full admin panel at `/admin/`.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Apply migrations

```bash
python manage.py migrate
```

### 3. Create a superuser

```bash
python manage.py createsuperuser
```

### 4. Run the development server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## Project Structure

```
qranalytics/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3              # SQLite database (auto-created)
├── media/
│   └── qrcodes/            # Generated QR PNG images
├── templates/
│   ├── base.html           # Shared layout, nav, styles
│   ├── home.html           # Landing page
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html      # Overview + scans chart
│   ├── create_qr.html      # QR creation form
│   ├── qr_detail.html      # Per-QR analytics
│   └── confirm_delete.html
├── qranalytics/
│   ├── settings.py
│   └── urls.py
└── tracker/
    ├── models.py           # QRCode, Scan models
    ├── views.py            # All views
    ├── forms.py            # QRCodeForm, SignUpForm
    ├── urls.py             # URL routing
    ├── utils.py            # QR generation, UA parsing
    └── admin.py            # Admin registration
```

---

## URL Routes

| URL | View | Description |
|-----|------|-------------|
| `/` | `home` | Landing page |
| `/signup/` | `signup_view` | User registration |
| `/login/` | `login_view` | Login |
| `/logout/` | `logout_view` | Logout |
| `/dashboard/` | `dashboard` | Analytics overview |
| `/create/` | `create_qr` | Create new QR code |
| `/qr/<code>/` | `qr_detail` | Per-QR analytics page |
| `/qr/<code>/delete/` | `delete_qr` | Delete QR + all scans |
| `/r/<code>/` | `redirect_qr` | Tracking redirect endpoint |

---

## Models

### `QRCode`
| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `user` | FK(User) | Owner |
| `name` | CharField | Human-readable label |
| `destination_url` | URLField | Where the QR points |
| `short_code` | CharField | 8-char unique tracking code |
| `qr_image` | ImageField | Stored PNG |
| `created_at` | DateTimeField | Auto |

No expiry field — QR codes are permanent by design.

### `Scan`
| Field | Type | Notes |
|-------|------|-------|
| `qr_code` | FK(QRCode) | Related QR |
| `scanned_at` | DateTimeField | Auto |
| `ip_address` | GenericIPAddressField | Visitor IP |
| `device_type` | CharField | mobile/tablet/desktop/bot |
| `browser` | CharField | e.g. Chrome |
| `os` | CharField | e.g. Android |
| `user_agent` | TextField | Raw UA string |
| `referer` | URLField | HTTP Referer header |

---

## Production Checklist

- Set `SECRET_KEY` via environment variable
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS` with your domain
- Use PostgreSQL instead of SQLite
- Serve media files via Nginx or S3
- Run `python manage.py collectstatic`

---

## Demo Credentials

After running the seed script or `createsuperuser`:
- **Username:** `admin`
- **Password:** `admin123`
