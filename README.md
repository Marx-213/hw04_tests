# yatube_tests
![Python](https://img.shields.io/badge/Python_3.7-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Python](https://img.shields.io/badge/django_2.2.9-%23092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/pytest-3776AB?style=for-the-badge&logo=python&logoColor=white)
[![CI](https://github.com/yandex-praktikum/hw04_tests/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw04_tests/actions/workflows/python-app.yml)

Протестированы модели приложения posts в URL, Yatube, приложения Views, тестирование форм
Написаны тесты, проверяющие:
- View-функции используют правильные html-шаблоны.
- Запрос к несуществующей странице вернёт ошибку 404
- При отправке валидной формы со страницы создания поста создаётся новая запись в базе данных;
- При отправке валидной формы со страницы редактирования поста происходит изменение поста с post_id в базе данных.
- Доступность страниц и названия шаблонов приложения Posts

### Установка
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/yandex-praktikum/hw04_tests.git
``` 
Установить и активировать виртуальное окружение:
``` 
python3 -m venv env
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
``` 
