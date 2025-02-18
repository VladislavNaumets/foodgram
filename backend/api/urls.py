from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (AvatarUpdateView, FavoriteViewSet, IngredientViewSet,
                       RecipeViewSet, SubscribeViewSet, SubscriptionListAPI,
                       TagViewSet, UserGetViewSet, UserViewSet)

app_name = "api"

router = DefaultRouter()

router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "users/",
        UserGetViewSet.as_view({"get": "list", "post": "create"}),
        name="user-list-create",
    ),
    path(
        "users/<int:pk>/",
        UserGetViewSet.as_view({"get": "retrieve"}),
        name="user-detail",
    ),
    path(
        "recipes/<int:recipe_id>/favorite/",
        FavoriteViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="favorite",
    ),
    path("users/me/avatar/", AvatarUpdateView.as_view(), name="user-avatar"),
    path(
        "users/subscriptions/",
        SubscriptionListAPI.as_view(),
        name="subscriptions",
    ),
    path(
        "users/me/",
        UserViewSet.as_view({"get": "retrieve"}),
        name="user-me",
    ),
    path(
        "users/<int:user_id>/subscribe/",
        SubscribeViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="subscribe-to",
    ),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("djoser.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
