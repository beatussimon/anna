from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('mchezo/', include('mchezo.urls')),
    path('wakala-balance/', include('multisyncbalance.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 