import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Import data from CSV file to Ingrediemt model"

    def handle(self, *args, **options):
        ingredients = ingredients = os.path.join(
            "/app/data", "ingredients.csv"
        )
        with open(ingredients, encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=row[0], defaults={"measurement_unit": row[1]}
                )
                # если требуется проверка внесения в базу,
                # разкомитить, инфа появится при запуске контейнера с беком
                # if created:
                #     self.stdout.write(
                #         self.style.SUCCESS(f"Добавлен ингридиент {row[0]}")
                #     )
                # else:
                #     self.stdout.write(
                #         self.style.WARNING(
                #             f"Ингридиент {row[0]} уже существует."
                #         )
                #     )

        self.stdout.write(self.style.SUCCESS("Импорт закончен."))
