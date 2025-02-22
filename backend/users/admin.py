from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recipes.models import Favorite, ShoppingCart
from users.models import FoodgramUser, Subscription
from recipes.models import Favorite, ShoppingCart, Recipe


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 1
    fk_name = "user"


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    extra = 1
    fk_name = "user"


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1
    fk_name = "user"


@admin.register(FoodgramUser)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "recipes_count",
        "subscriptions_count",
    )
    search_fields = ("username", "email")
    inlines = (SubscriptionInline, FavoriteInline, ShoppingCartInline)

    @admin.display(description="Количество рецептов")
    def recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    @admin.display(description="Количество подписчиков")
    def subscriptions_count(self, obj):
        return obj.subscribers.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "subscribed_to")
    search_fields = ("user__email", "subscribed_to__email")
