from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (FavoriteViewSet, IngredientViewSet,
                       RecipeViewSet, SubscribeViewSet,
                       SubscriptionListAPI, TagViewSet, UserGetViewSet)

app_name = "api"

v1_router = DefaultRouter()

v1_router.register(r"users", UserGetViewSet, basename="user")
v1_router.register(r"tags", TagViewSet, basename="tag")
v1_router.register(r"ingredients", IngredientViewSet, basename="ingredient")
v1_router.register(r"recipes", RecipeViewSet, basename="recipe")


urlpatterns = [
    path("", include(v1_router.urls)),
    # path(
    #     "users/",
    #     UserGetViewSet.as_view({"get": "list", "post": "create"}),
    #     name="user-list-create",
    # ),
    # path(
    #     "users/<int:pk>/",
    #     UserGetViewSet.as_view({"get": "retrieve"}),
    #     name="user-detail",
    # ),
    path(
        "recipes/<int:recipe_id>/favorite/",
        FavoriteViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="favorite",
    ),
    path(
        "users/subscriptions/",
        SubscriptionListAPI.as_view(),
        name="subscriptions",
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
