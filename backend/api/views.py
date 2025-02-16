from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import FoodgramPagination
from api.permissions import IsAuthorOrStaff
from api.serializers import (AvatarSerializer, FavoriteSerializer,
                             IngredientSerializer, NewUserSerializer,
                             RecipeIWriteSerializer, RecipeReadSerializer,
                             SubscribeActionSerializer, SubscriptionSerializer,
                             TagSerializer, UserCreateSerializer)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class UserViewSet(UserViewSet):
    """Расширенный UserViewSet на основе Djoser."""
    serializer_class = NewUserSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        """Использует разные сериализаторы в зависимости от запроса."""
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "me":
            return NewUserSerializer
        return super().get_serializer_class()

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписка на пользователя."""
        subscribed_to = get_object_or_404(User, pk=pk)
        if request.user == subscribed_to:
            return Response({"detail": "Нельзя подписаться на самого себя."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscribeActionSerializer(
            data={
                "subscribed_to": subscribed_to.id}, context={
                    "request": request}
        )
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=["delete"],
        permission_classes=[IsAuthenticated])
    def unsubscribe(self, request, pk=None):
        """Отписка от пользователя."""
        deleted_count, _ = Subscription.objects.filter(
            user=request.user, subscribed_to__id=pk).delete()
        if deleted_count == 0:
            return Response({"detail": "Подписка не найдена."},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Получение списка подписок текущего пользователя."""
        current_user = request.user
        queryset = (User.objects.filter(subscribers__user=current_user)
                    .annotate(
                        recipes_count=Count("recipes"),
                        is_subscribed=Exists(
                            Subscription.objects.filter(
                                user=current_user,
                                subscribed_to=OuterRef("pk"))),).order_by(
                                    "-date_joined"))
        paginator = FoodgramPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = SubscriptionSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=["put", "delete"],
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Обновление или удаление аватара пользователя."""
        user = request.user
        if request.method == "PUT":
            serializer = AvatarSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "DELETE":
            if user.avatar:
                user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """list() и retrieve() для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """list() и retrieve() для модели Ingridient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD для модели Recipe."""

    permission_classes = (IsAuthorOrStaff,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """Возвращает QuerySet рецептов"""
        """с аннотацией 'избранное' и 'в корзине'."""
        user = None
        if self.request.user.is_authenticated:
            user = self.request.user
        return (
            Recipe.objects
            .prefetch_related("ingredients", "tags")
            .select_related("author")
            .annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user, recipe=OuterRef("pk"))
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user, recipe=OuterRef("pk"))
                ),
            )
        )

    @action(detail=False, methods=["get"], url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок в формате .txt."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__cart_users__user=request.user
        ).select_related("ingredient")

        content = self._generate_shopping_cart(ingredients)
        response = Response(content, content_type="text/plain")
        response[
            "Content-Disposition"] = 'attachment; filename="shopping_list.txt"'
        return response

    def _generate_shopping_cart(self, ingredients):
        """Генерация содержимого файла со списком покупок."""
        in_cart = {}
        for ingredient in ingredients:
            ingredient_name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            amount = ingredient.amount

            in_cart[(ingredient_name, measurement_unit)] = (
                in_cart.get((ingredient_name, measurement_unit), 0) + amount
            )

        return "\n".join(
            f"{name} - {amount} ({unit})"
            for (name, unit), amount in in_cart.items()
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="short-link/(?P<short_link>[^/.]+)"
    )
    def get_by_short_link(self, request, short_link):
        """Перенаправляет на объект рецепта по короткой ссылке."""
        recipe = get_object_or_404(Recipe, short_link=short_link)
        recipe_url = f"{settings.BASE_URL}/recipes/{recipe.id}/"
        return redirect(recipe_url)

    @action(
        detail=True, methods=["post", "delete"], url_path="favorite"
    )
    def manage_favorites(self, request, pk=None):
        """Добавление и удаление рецепта в Избранное."""
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == "POST":
            serializer = FavoriteSerializer(
                data={"recipe": recipe.id}, context={"request": request}
            )
            if serializer.is_valid():
                fav_item = serializer.save()
                return Response(
                    self.get_serializer(fav_item).data,
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "DELETE":
            deleted_count, _ = Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).delete()

            if deleted_count == 0:
                return Response(
                    {"detail": "Рецепта нет в Избранном."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"], url_path="shopping_cart")
    def manage_shopping_cart(self, request, pk=None):
        """Добавление и удаление рецептов из корзины."""
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == "POST":
            ShoppingCart.objects.get_or_create(
                user=request.user, recipe=recipe)
            return Response({
                "detail": "Рецепт добавлен в корзину."}, status=201)

        deleted, _ = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe).delete()
        if deleted:
            return Response(
                {"detail": "Рецепт удалён из корзины."}, status=204)
        return Response(
            {"detail": "Рецепт отсутствует в корзине."}, status=400)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода запроса."""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeIWriteSerializer

    def get_serializer_context(self):
        """Добавляет 'request' в контекст сериализатора."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
