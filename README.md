# api_yamdb
## **Описание проекта**
В проекте "Продуктовый помощник" реализованы следуещие возвожности:
 - регистрация пользователя,
 - создание рецепта с возможностью выбора ингредиентов из базы данных, указания тегов и прикрепления изображений,
 - подписка на пользователей,
 - фильтрация рецептов по тегам и авторам,
 - добавление рецептов в избранное,
 - добавление рецептов в корзину,
 - скачивание списка покупок.
Проект реализован на Django, в свою очередь API реализован с использованием библиотеки Django REST Framework (DRF).
Проект запускаеться в трех контейнерах:
 - frontend
 - backend
 - db
 - nginx

## **Шаблон наполнения env-файла**
```
DB_ENGINE= # указываем базу данных, с которой работаем
DB_NAME= # имя базы данных
POSTGRES_USER= # логин для подключения к базе данных
POSTGRES_PASSWORD= # пароль для подключения к БД
DB_HOST= # название сервиса (контейнера)
DB_PORT= # порт для подключения к БД 
```

## **Как запустить проект**

Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/nikontra/foodgram-project-react.git

```
```
cd foodgram-project-react
```
Для сборки и запуска контейнеров перейти в папку "infra":
```
cd infra
```
И использовать команду:
```
sudo docker-compose up
```
Если необходимо запустить контейнеры в "фоновом режиме":
```
sudo docker-compose up -d
```
Для пересборки контейнеров и запуска в "фоновом режиме":
```
sudo docker-compose up -d --build
```
После запуска контейнеров,  чтобы создать миграций, суперпользователя и собрать статику, необходимо последовательно выполнить команды:
```
sudo docker-compose exec web python manage.py migrate 
sudo docker-compose exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py collectstatic --no-input
```
Для остановки контейнеров нажать CTRL+C.
Если контейнеры запущены в "фоновом режиме":
```
sudo docker-compose stop
```
Для остановки и удаления контейнеров:
```
sudo docker-compose down -v
```

## **Заполнение базы данных**
Скопировать файл с данными для базы dump.json в контейнер backend:
```
sudo docker cp dump.json CONTAINER_ID:/app
```
ID контейнера можно узнать выполнив команду:
```
sudo docker container ls -a
```
Для заполнения базы данными выполнить команду:
```
sudo docker-compose exec web python manage.py loaddata dump.json
```
База данных заполнена.

## **Информация об авторе**
Автор проекта: Третьяков Николай
Контакты: 
 - Email: nikontra@yandex.ru
 - Git: https://github.co


## **Проект можно посмотреть по адресу:**

http://51.250.18.26/

Superuser:
login: kolgate
password: kol@trest

![example workflow](https://github.com/nikontra/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)