# api/urls.py
from django.urls import path
from .views import contact_view

urlpatterns = [
    path('contact/', contact_view),  # 对应 /api/contact/
]
