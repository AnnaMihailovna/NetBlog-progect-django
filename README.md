## Проект NetBlog
### Описание  
  Проект представляет собой социальную сеть для публикации личных микроблогов. Она даёт пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи. Пользователи могут заходить на чужие страницы, и комментировать записи других авторов.
### Технологии  
  Python 3.8.10  
  Django 2.2.19  
### Запуск проекта в dev-режиме
  * Клонируйте проект на свой компьютер
```
git clone git@github.com:AnnaMihailovna/NetBlog-progect-django.git
```
  * Установите и активируйте виртуальное окружение
```
python -m venv venv
source venv/bin/activate
```
  * Установите зависимости из файла requirements.txt  
```
pip install -r requirements.txt
```
  * В папке с файлом manage.py подготовить и провести миграции:
```
python manage.py makemigrations
python manage.py migrate
```
  * Там же создать суперюзера:
```
python manage.py createsuperuser
```
  * Запустить проект:
```
python manage.py runserver
```
### Развёрнутый проект:
https://netblog.pythonanywhere.com/

https://netblog.pythonanywhere.com/admin/

### Автор  
[AnnaMihailovna](https://github.com/AnnaMihailovna/)
