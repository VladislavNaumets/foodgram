# Проект: [Foodgram](https://food.sytes.net)
### Выпускной проект *Яндекс.Практикум* курса Python-разработчик(backend)

Проект Foodgram дает возможность пользователям создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.


## Технологии
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/Django%20REST%20Framework-092E20?style=for-the-badge&logo=django&logoColor=white)
![Djoser](https://img.shields.io/badge/Djoser-092E20?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

## [API документация](https://food.sytes.net/redoc/)

## [Администрирование](https://food.sytes.net/admin/)

## Запуск проекта на удаленном сервере

1. Установить docker compose на сервер:
```bash
sudo apt update
```
```bash
sudo apt install curl
```
```bash
curl -fSL https://get.docker.com -o get-docker.sh
```
```bash
sudo sh ./get-docker.sh
```
```bash    
sudo apt-get install docker-compose-plugin
```

2. Скачать файл [docker-compose.production.yml](https://github.com/VladislavNaumets/foodgram/blob/main/docker-compose.production.yml) на свой сервер.

3. На сервере в директории с файлом **docker-compose.production.yml** создать файл  **.env**:
``` bash    
Пример заполнения файла (https://github.com/VladislavNaumets/foodgram/blob/main/.env.example)
```        
4. Запустить Docker compose:
``` bash
sudo docker compose -f docker-compose.production.yml up -d
```
5. На сервере настроить и запустить Nginx:
- открыть файлы конфигурации
    ``` bash
    sudo nano /etc/nginx/sites-enabled/default
    ```
- внести изменения, заменив **<your.domain.com>** на свое доменное имя
    ``` bash 
    server {
        listen 80;
        server_name <your.domain.com>;

        location / {
            proxy_set_header Host $http_host;        
            proxy_pass http://127.0.0.1:7777;
            client_max_body_size 5M;
            
        }
    }
    ``` 
- убедиться, что в файле конфигурации нет ошибок
    ``` bash
    sudo nginx -t
    ```
- перезагрузить конфигурацию
    ``` bash
    sudo service nginx reload
    ```

## Запуск на локальной машине

1. Скачать репозиторий (https://github.com/VladislavNaumets/foodgram)

2. На сервере в директории с файлом **docker-compose.yml** создать файл  **.env**:
``` bash    
Пример заполнения файла (https://github.com/VladislavNaumets/foodgram/blob/main/.env.example)
```

## Запуск на сервере

### 1. Клонирование репозитория
Скачайте репозиторий с GitHub:
```bash
git clone https://github.com/VladislavNaumets/foodgram.git
```
Перейдите в директорию проекта:
```bash
cd foodgram
```

### 2. Создание `.env` файла
На сервере в директории с файлом `docker-compose.yml` создайте файл `.env`:
```bash
touch .env
```
Пример заполнения файла: [`.env.example`](https://github.com/VladislavNaumets/foodgram/blob/main/.env.example)

### 3. Запуск контейнеров
Запустите проект с помощью Docker Compose:
```bash
sudo docker compose up -d --build
```

### 4. Выполнение миграций и сбор статических файлов
После запуска контейнеров выполните следующие команды:
```bash
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic --noinput
```

### 5. Создание суперпользователя
Для создания администратора выполните:
```bash
sudo docker compose exec backend python manage.py createsuperuser
```
Следуйте инструкциям для ввода имени, email и пароля.

### 6. Загрузка ингредиентов и тегов
Загрузите список ингредиентов:
```bash
sudo docker compose exec backend python manage.py ingredients_import
```
Загрузите список тегов:
```bash
sudo docker compose exec backend python manage.py tags_import
```

### 7. Доступ к проекту
- API документация: `http://127.0.0.1/api/docs/`
- Панель администратора: `http://127.0.0.1/admin/`
- Сам сайт: `http://127.0.0.1/`

### 8. Остановка контейнеров
Если нужно остановить проект, выполните:
```bash
sudo docker compose down
```

## Автор проекта [**Владислав Наумец**](https://github.com/VladislavNaumets)