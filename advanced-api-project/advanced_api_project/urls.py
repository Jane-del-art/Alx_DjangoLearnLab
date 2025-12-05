from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

     # Include API URLs with 'api/' prefix
    path('api/', include('api.urls')),
    
    # DRF login/logout for browsable API
    path('api-auth/', include('rest_framework.urls')),
]
