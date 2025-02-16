from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

app_name = "api"

router = DefaultRouter()
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"ingredients", IngredientViewSet, basename="ingredient")
router.register(r"recipes", RecipeViewSet, basename="recipe")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "recipes/download_shopping_cart/",
        RecipeViewSet.as_view({'get': 'download_shopping_cart'}),
        name="download",
    ),
    path(
        "users/",
        UserViewSet.as_view({"get": "list", "post": "create"}),
        name="user-list-create",
    ),
    path(
        "users/<int:pk>/",
        UserViewSet.as_view({"get": "retrieve"}),
        name="user-detail",
    ),
    path(
        "recipes/<int:recipe_id>/shopping_cart/",
        RecipeViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="shopping_cart",
    ),
    path(
        "recipes/<int:recipe_id>/favorite/",
        RecipeViewSet.as_view(
            {'post': 'manage_favorites', 'delete': 'manage_favorites'}),
        name="favorite",
    ),
    path("users/me/avatar/", UserViewSet.as_view(), name="user-avatar"),
    path(
        "users/subscriptions/",
        UserViewSet.as_view(),
        name="subscriptions",
    ),
    path(
        "users/me/",
        UserViewSet.as_view({"get": "retrieve"}),
        name="user-me",
    ),
    path(
        "users/<int:user_id>/subscribe/",
        UserViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="subscribe-to",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
