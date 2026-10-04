from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

if settings.DEBUG:
    urlpatterns = static(
        settings.STATIC_URL,
        document_root=str(settings.BASE_DIR / 'detection_app' / 'static'),
    )
else:
    urlpatterns = []

urlpatterns += [
    path('admin/', admin.site.urls),
    path('', include('detection_app.urls')),
]