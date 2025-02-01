import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Импорт ингридиентов из CSV в бд"

    def handle(self, *args, **options):
        ingredients_path = os.path.join("/app/data", "ingredients.csv")

        if not os.path.exists(ingredients_path):
            self.stdout.write(self.style.ERROR(
                f"Файл {ingredients_path} не найден!"
            ))
            return
        with open(ingredients_path, encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0], defaults={"measurement_unit": row[1]}
                )
                # если требуется проверка внесения всех ингридиентов в базу,
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
