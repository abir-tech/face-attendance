from django.urls import path
# Make sure 'AttendanceHistoryView' is spelled exactly like this:
from .views import ScanFaceView, RegisterFaceView, AttendanceHistoryView

urlpatterns = [
    path('api/scan-face/', ScanFaceView.as_view(), name='scan-face'),
    path('api/register-face/', RegisterFaceView.as_view(), name='register-face'),
    path('api/attendance-history/', AttendanceHistoryView.as_view(), name='attendance-history'), 
]