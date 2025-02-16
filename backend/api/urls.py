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
        "users/<int:pk>/subscribe/",
        UserViewSet.as_view({"post": "subscribe", "delete": "unsubscribe"}),
        name="subscribe-to",
    ),
    path(
        "users/subscriptions/",
        UserViewSet.as_view({"get": "subscriptions"}),
        name="subscriptions",
    ),
    path(
        "users/me/avatar/",
        UserViewSet.as_view({"put": "avatar", "delete": "avatar"}),
        name="user-avatar",
    ),
    path(
        "recipes/<int:pk>/shopping_cart/",
        RecipeViewSet.as_view(
            {"post": "manage_shopping_cart",
             "delete": "manage_shopping_cart"}),
        name="shopping_cart",
    ),
    path(
        "recipes/<int:pk>/favorite/",
        RecipeViewSet.as_view(
            {'post': 'manage_favorites', 'delete': 'manage_favorites'}),
        name="favorite",
    ),
    path(
        "recipes/download_shopping_cart/",
        RecipeViewSet.as_view({'get': 'download_shopping_cart'}),
        name="download",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
