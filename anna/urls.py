from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mchezo/', include('mchezo.urls')),
    path('wakala-balance/', include('multisyncbalance.urls')),
    path('', include('core.urls')),
]