from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserSerializer
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import FoodgramPagination
from api.permissions import ActionRestriction, IsAuthorOrStaff
from api.renderer import PlainTextRenderer
from api.serializers import (AvatarSerializer, FavoriteSerializer,
                             IngredientSerializer, NewUserSerializer,
                             RecipeIWriteSerializer, RecipeReadSerializer,
                             ShoppingCartSerializer, SubscribeActionSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserCreateSerializer)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class NewUserViewSet(UserViewSet):
    """Переопределяет вьюсет пользователя от djoser."""

    serializer_class = NewUserSerializer
    permission_classes = (ActionRestriction, IsAuthenticated)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class UserGetViewSet(viewsets.ViewSet):
    """Предоставляет просмотр и создание юзера(ов)."""

    queryset = User.objects.all()
    serializer_class = NewUserSerializer
    permission_classes = (AllowAny,)

    def get_serializer(self, *args, **kwargs):
        """Возвращает экземпляр сериализатора."""
        return self.serializer_class(*args, **kwargs)

    def list(self, request):
        queryset = User.objects.order_by("id")
        paginator = FoodgramPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = NewUserSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = NewUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = UserSerializer(user)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated])
    def get_me(self, request):
        """Получение информации о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["put", "delete"],
        url_path="me/avatar",
        permission_classes=[IsAuthenticated],
    )
    def manage_avatar(self, request):
        """Обновление или удаление аватара пользователя."""
        user = request.user

        if request.method == "PUT":
            serializer = AvatarSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_200_OK)

        if request.method == "DELETE":
            if user.avatar:
                user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Получение списка подписок текущего пользователя."""
        current_user = request.user
        queryset = (
            User.objects.filter(subscribers__user=current_user)
            .annotate(
                recipes_count=Count("recipes"),
                is_subscribed=Exists(
                    Subscription.objects.filter(
                        user=current_user, subscribed_to=OuterRef("pk")
                    )
                ),
            )
            .order_by("id")
        )

        paginator = FoodgramPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = SubscriptionSerializer(
            paginated_queryset, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        """Подписаться или отписаться от пользователя."""
        if request.method == "POST":
            subscribed_to = get_object_or_404(User, id=pk)
            serializer = SubscribeActionSerializer(
                data={"subscribed_to": subscribed_to.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            pair = serializer.save()
            return Response(
                SubscribeActionSerializer(pair).data,
                status=status.HTTP_201_CREATED
            )

        if request.method == "DELETE":
            deleted_count, _ = Subscription.objects.filter(
                user=request.user, subscribed_to__id=pk
            ).delete()

            if deleted_count == 0:
                return Response(
                    {"detail": "Подписка не найдена."},
                    status=status.HTTP_404_NOT_FOUND,
                )
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


class ReturnShortLinkRecipeAPI(APIView):
    """Перенаправляет на объект рецепта по короткой ссылке."""

    permission_classes = (ActionRestriction,)

    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        recipe_url = f"{settings.BASE_URL}/recipes/{recipe.id}/"
        return redirect(recipe_url)


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD для модели Recipe."""

    permission_classes = (IsAuthorOrStaff,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = (
            self.request.user if self.request.user.is_authenticated else None
        )
        return (
            Recipe.objects.prefetch_related("ingredients", "tags")
            .select_related("author")
            .annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=user, recipe=OuterRef("pk"))
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user, recipe=OuterRef("pk")
                    )
                ),
            )
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Добавление или удаление рецепта из корзины."""
        if request.method == "POST":
            # Добавление в корзину
            recipe = get_object_or_404(Recipe, id=pk)
            serializer = ShoppingCartSerializer(
                data={"recipe": recipe.id}, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            cart_item = serializer.save()
            return Response(
                ShoppingCartSerializer(cart_item).data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == "DELETE":
            # Удаление из корзины
            deleted_count, _ = ShoppingCart.objects.filter(
                user=request.user, recipe_id=pk
            ).delete()

            if deleted_count == 0:
                return Response(
                    {"detail": "Рецепта нет в корзине."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        permission_classes=[IsAuthenticated],
        renderer_classes=[PlainTextRenderer],
    )
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__cart_users__user=request.user
        ).select_related("ingredient")

        content = self.create_file(ingredients)

        response = Response(content)
        response[
            "Content-Disposition"
        ] = 'attachment; filename="products_list.txt"'
        return response

    def create_file(self, ingredients):
        """Создает содержимое файла на основе элементов корзины."""
        in_cart = {}

        for ingredient in ingredients:
            ingredient_name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            amount = ingredient.amount

            in_cart[(ingredient_name, measurement_unit)] = (
                in_cart.get((ingredient_name, measurement_unit), 0) + amount
            )

        cart = [
            f"{key[0]} - {value}({key[1]})" for key, value in in_cart.items()
        ]
        content = "\n".join(cart)
        return content

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="favorite",
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта в Избранное."""
        if request.method == "POST":
            recipe = get_object_or_404(Recipe, id=pk)
            serializer = FavoriteSerializer(
                data={"recipe": recipe.id}, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            fav_item = serializer.save()
            return Response(
                FavoriteSerializer(fav_item).data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == "DELETE":
            deleted_count, _ = Favorite.objects.filter(
                user=request.user, recipe_id=pk
            ).delete()

            if deleted_count == 0:
                return Response(
                    {"detail": "Рецепта нет в Избранном."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        """Получение короткой ссылки к рецепту."""
        recipe = self.get_object()
        short_link = f"{settings.BASE_URL}/s/{recipe.short_link}"
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeIWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


def short_link_redirect(request, short_link):
    """Перенаправляет по короткой ссылке на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    recipe_url = f"{settings.BASE_URL}/recipes/{recipe.id}/"
    return redirect(recipe_url)
