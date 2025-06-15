from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('mp3.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    # Serve static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Serve media files from static directory
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)