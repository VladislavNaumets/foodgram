from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet,
                       RecipeViewSet, TagViewSet, UserGetViewSet)

app_name = "api"

v1_router = DefaultRouter()

v1_router.register(r"users", UserGetViewSet, basename="user")
v1_router.register(r"tags", TagViewSet, basename="tag")
v1_router.register(r"ingredients", IngredientViewSet, basename="ingredient")
v1_router.register(r"recipes", RecipeViewSet, basename="recipe")


urlpatterns = [
    path("", include(v1_router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
