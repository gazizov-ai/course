from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView

from education_app.views.users import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('api/chat/', include('education_app.urls.chat')),
    path('api/course/', include('education_app.urls.course')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/users/', include('education_app.urls.users')),
    path(
        'api/auth/login/',
        CustomTokenObtainPairView.as_view(),
        name='custom_token_obtain_pair',
    ),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
