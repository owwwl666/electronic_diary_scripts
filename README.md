# Электронный дневник школы

Этот сайт - интерфейс для учеников школы. Здесь можно посмотреть оценки, расписание и прочую открытую информацию. Учителя заполняют базу данных через другой сайт. Ставят там оценки и т.д.

## Описание моделей

На сайте есть ученики: `Schoolkid`. Класс ученика определяется через комбинацию его полей `year_of_study` — год обучения и `group_letter` — литера класса. Вместе получается, например, 10А. Ученик связан со следующими моделями:

- `Mark` — оценка на уроке, от 2 до 5.
- `Commendation` — похвала от учителя, за особые достижения.
- `Chastisement` — замечание от учителя, за особые проступки.

Все 3 объекта связаны не только с учителем, который их создал, но и с учебным предметом (`Subject`). Примеры `Subject`:

- Математика 8 класса
- Геометрия 11 класса
- Русский язык 1 класса
- Русский язык 4 класса

`Subject` определяется не только названием, но и годом обучения, для которого учебный предмет проходит.

За расписание уроков отвечает модель `Lesson`. Каждый объект `Lesson` — урок в расписании. У урока есть комбинация `year_of_study` и `group_letter`, благодаря ей можно узнать для какого класса проходит этот урок. У урока есть `subject` и `teacher`, которые отвечают на вопросы "что за урок" и "кто ведёт". У урока есть `room` — номер кабинета, где он проходит. Урок проходит в дату `date`.

Расписание в школе строится по слотам:

- 8:00-8:40 — 1 урок
- 8:50-9:30 — 2 урок
- ...

У каждого `Lesson` есть поле `timeslot`, которое объясняет, какой номер у этого урока в расписании.

## Запуск

- [Скачайте код](https://github.com/devmanorg/e-diary/tree/master)
- [Скачайте БД и поместите файл в директорию проекта](https://dvmn.org/filer/canonical/1562234129/166/)
- Скачайте данный репозиторий и поместите скрипт `scripts.py` и файл `praise.txt` в директорию проекта
- Установите зависимости командой `pip install -r requirements.txt`
- Создайте БД командой `python3 manage.py migrate`
- Запустите сервер командой `python3 manage.py runserver`

## Переменные окружения

Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` рядом с `manage.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Доступны 4 переменные:
- `DEBUG` — дебаг-режим. Поставьте True, чтобы увидеть отладочную информацию в случае ошибки.
- `SECRET_KEY` — секретный ключ проекта
- `ALLOWED_HOSTS` — см [документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).
- `DATABASE_NAME` — путь до базы данных, например: `schoolbase.sqlite3`

## Реализация проекта
В скрипте `scripts.py` реализованый 3 функции, отвечающие за изменение данных ученика в электронном дневнике.
- Перейдите в `django shell`,введя следующую команду:
    ```
    python manage.py shell
    ```
- Скопируйте код из `scripts.py` в shell

- Функция `generates_praise` открывает файл `praise.txt` и выбирает в нем случайную похвалу:

    ```python
    def get_praise_from_file():
        """Считывает файл praise.txt с похвалами и берет оттуда случайную речь."""
        file_path = pathlib.Path.cwd().joinpath('praise.txt')
        with open(file_path, 'r') as file:
            praise = random.choice([line for line in file.readlines()])
        return praise
    ```
    
- Функция `get_schoolkid` возвращает данные учетной записи ученика, а в случае ошибки обрабтывает ее и сообщает пользователю о причине поломки кода:

    ```python
    def get_schoolkid(child_name):
        """Возвращает данные об ученике

        В случае ошибки обрабатывает исключение и возбуждает его в зависимости от проблемы.
        """
        try:
            student_account = Schoolkid.objects.get(full_name__contains=child_name)
        except Schoolkid.MultipleObjectsReturned:
            raise Schoolkid.MultipleObjectsReturned('Уточните ФИО ученика')
        except Schoolkid.DoesNotExist:
            raise Schoolkid.DoesNotExist('Ученик не найден')
        return student_account
    ```

- Функция `fix_marks` отвечает отвечает за исправление всех плохих оценок ученика на 5. Чтобы ее запустить передайте функции в качестве аргумента ФИО ученика:

    ```python
    def fix_marks(child_name):
        """Исправляет оценки меньше тройки ученика на пятерки."""
        child_data = get_schoolkid(child_name)
        Mark.objects.filter(schoolkid__full_name=child_data.full_name, points__lte=3) \
            .update(points=5)
    ```
    
- Функция `remote_chastisements` удаляет все замечания в учетной записи ученика. Принимает в качестве аргумента ФИО ученика:

    ```python
    def remote_chastisements(child_name):
        """Удаляет замечания с учетной записи ученика."""
        child_data = get_schoolkid(child_name)
        child_chastisement = Chastisement.objects.filter(schoolkid__full_name=child_data.full_name)
        child_chastisement.delete()
    ```

- Функция `create_commendation` создает похвалу от учителя ученику за случайный урок по определенному предмету. Аргументы - ФИО ученика, 'Название' предмета:

     ```python
   def create_commendation(child_name, subject):
        """Создает похвалительную речь для ученика на случайном уроке одного из предмета."""
        try:
            child_data = get_schoolkid(child_name)
            school_subject = Lesson.objects.filter(year_of_study=child_data.year_of_study,
                                                   group_letter=child_data.group_letter,
                                                   subject__title=subject)
            lesson = random.choice(school_subject)
        except IndexError:
            raise IndexError('Неверное название предмета или отсутствие урока')
        else:
            Commendation.objects.create(text=get_praise_from_file(),
                                        created=lesson.date,
                                        schoolkid=get_schoolkid(child_name),
                                        subject=lesson.subject,
                                        teacher=lesson.teacher)
    ```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
