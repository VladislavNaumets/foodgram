from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.views import short_link_redirect

urlpatterns = [
    path("api/", include("api.urls")),
    path("s/<str:short_link>/", short_link_redirect, name="recipe-short-link"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
