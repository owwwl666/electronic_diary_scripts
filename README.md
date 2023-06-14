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
- Скачайте данный репозиторий и поместите скрипт `scripts.py` в директорию проекта
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
- Функция `fix_marks` отвечает отвечает за исправление всех плохих оценок ученика на 5. Чтобы ее запустить передайте функции в качестве аргумента ФИО ученика:

    ```python
    def fix_marks(child_name):
      """Исправляем оценки меньше тройки ученика на пятерки."""
      try:
          child_data = Schoolkid.objects.get(full_name__contains=child_name).full_name
          child_marks = Mark.objects.filter(schoolkid__full_name=child_data, points__lte=3)
          for child_mark in child_marks:
              child_mark.points = '5'
              child_mark.save()
      except Schoolkid.MultipleObjectsReturned:
          print('Уточните ФИО ученика')
      except Schoolkid.DoesNotExist:
          print('Ученик не найден')
    ```
    
- Функция `remote_chastisements` удаляет все замечания в учетной записи ученика. Принимает в качестве аргумента ФИО ученика:

    ```python
    def remote_chastisements(child_name):
      """Удаляем замечания с учетной записи ученика."""
      try:
          child_data = Schoolkid.objects.get(full_name__contains=child_name).full_name
          chastisement_child = Chastisement.objects.filter(schoolkid__full_name__contains=child_data)
          chastisement_child.delete()
      except Schoolkid.MultipleObjectsReturned:
          print('Уточните ФИО ученика')
      except Schoolkid.DoesNotExist:
          print('Ученик не найден')
    ```

- Функция `create_commendation` создает похвалу от учителя ученику за случайный урок по определенному предмету. Аргументы - ФИО ученика, 'Название' предмета:

     ```python
    def create_commendation(child_name, subject):
      """Создаем похвалительную речь для ученика на случайном уроке одного из предмета."""
      try:
          child_data = Schoolkid.objects.get(full_name__contains=child_name)
          school_subject = Lesson.objects.filter(year_of_study=6, group_letter='А', subject__title=subject)
          lesson = random.choice(school_subject)
          Commendation.objects.create(text='Хвалю', created=lesson.date, schoolkid=child_data, subject=lesson.subject,
                                      teacher=lesson.teacher)
      except Schoolkid.MultipleObjectsReturned:
          print('Уточните ФИО ученика')
      except Schoolkid.DoesNotExist:
          print('Ученик не найден')
      except IndexError:
          print('Неверное название предмета')
    ```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
