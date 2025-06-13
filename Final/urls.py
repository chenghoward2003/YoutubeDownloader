from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('mp3.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    # Only serve static files, as media is merged into static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)