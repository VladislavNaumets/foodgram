import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = "Импорт ингредиентов и тегов из CSV в базу данных"

    def handle(self, *args, **options):
        data_path = "/app/data"

        # Импорт ингредиентов
        ingredients_path = os.path.join(data_path, "ingredients.csv")
        if os.path.exists(ingredients_path):
            self.import_ingredients(ingredients_path)
        else:
            self.stdout.write(self.style.ERROR(f"Файл {ingredients_path} не найден!"))

        # Импорт тегов
        tags_path = os.path.join(data_path, "tags.csv")
        if os.path.exists(tags_path):
            self.import_tags(tags_path)
        else:
            self.stdout.write(self.style.ERROR(f"Файл {tags_path} не найден!"))

        self.stdout.write(self.style.SUCCESS("Импорт данных завершён!"))

    def import_ingredients(self, file_path):
        """Импорт ингредиентов из CSV."""
        with open(file_path, encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) != 2:  # Проверяем, чтобы было 2 колонки (название, ед. измерения)
                    self.stdout.write(self.style.ERROR(f"Ошибка в строке (ингредиенты): {row}"))
                    continue

                name, measurement_unit = row
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name, defaults={"measurement_unit": measurement_unit}
                )

                # Дебаг-логирование (по желанию)
                # if created:
                #     self.stdout.write(self.style.SUCCESS(f"Добавлен ингредиент: {name}"))
                # else:
                #     self.stdout.write(self.style.WARNING(f"Ингредиент {name} уже существует."))

        self.stdout.write(self.style.SUCCESS("Импорт ингредиентов завершён!"))

    def import_tags(self, file_path):
        """Импорт тегов из CSV."""
        with open(file_path, encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) != 2:  # Проверяем, чтобы было 2 колонки (название, slug)
                    self.stdout.write(self.style.ERROR(f"Ошибка в строке (теги): {row}"))
                    continue

                name, slug = row
                tag, created = Tag.objects.get_or_create(name=name, defaults={"slug": slug})

                # Дебаг-логирование (по желанию)
                # if created:
                #     self.stdout.write(self.style.SUCCESS(f"Добавлен тег: {name} ({slug})"))
                # else:
                #     self.stdout.write(self.style.WARNING(f"Тег {name} ({slug}) уже существует."))

        self.stdout.write(self.style.SUCCESS("Импорт тегов завершён!"))
