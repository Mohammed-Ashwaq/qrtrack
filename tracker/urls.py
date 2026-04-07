from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_qr, name='create_qr'),
    path('qr/<str:short_code>/', views.qr_detail, name='qr_detail'),
    path('qr/<str:short_code>/delete/', views.delete_qr, name='delete_qr'),
    path('r/<str:short_code>/', views.redirect_qr, name='redirect_qr'),
]
