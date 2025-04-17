# backend/core_settings/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static
from rest_framework_simplejwt.views import ( # Import JWT views
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView, # Optional: If you want an endpoint to verify tokens
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), # Your app's API endpoints

    # JWT Authentication Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # POST username/password -> returns access/refresh tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   # POST refresh_token -> returns new access token
    # path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'), # Optional: POST token -> verifies if valid
]

# --- Add this for serving media files during development ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)