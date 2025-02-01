#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput

if [ -f /app/backend/data/ingredients.csv ]; then

    echo "Импорт данных из ingredients.csv..."
    python manage.py ingredients_import
else
    echo "Файл ingredients.csv не найден. Пропускаем импорт."
fi

if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Проверка существования суперпользователя..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email="$DJANGO_SUPERUSER_EMAIL").exists():
    User.objects.create_superuser(
        email="$DJANGO_SUPERUSER_EMAIL",
        username="$DJANGO_SUPERUSER_USERNAME",
        first_name="$DJANGO_SUPERUSER_FIRST_NAME",
        last_name="$DJANGO_SUPERUSER_LAST_NAME",
        password="$DJANGO_SUPERUSER_PASSWORD"
    )
    print("Суперпользователь создан.")
else:
    print("Суперпользователь уже существует.")
EOF
fi

cp -r /app/collected_static/. /backend_static/static/
exec "$@"