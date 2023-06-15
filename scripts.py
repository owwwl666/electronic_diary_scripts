from datacenter.models import Schoolkid, Mark, Lesson, Chastisement, Commendation
import random
import pathlib


def get_praise_from_file():
    """Считывает файл praise.txt с похвалами и берет оттуда случайную речь."""
    file_path = pathlib.Path.cwd().joinpath('praise.txt')
    with open(file_path, 'r') as file:
        praise = random.choice([line for line in file.readlines()])
    return praise


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


def fix_marks(child_name):
    """Исправляет оценки меньше тройки ученика на пятерки."""
    child_data = get_schoolkid(child_name)
    Mark.objects.filter(schoolkid__full_name=child_data.full_name, points__lte=3) \
        .update(points=5)


def remote_chastisements(child_name):
    """Удаляет замечания с учетной записи ученика."""
    child_data = get_schoolkid(child_name)
    child_chastisement = Chastisement.objects.filter(schoolkid__full_name=child_data.full_name)
    child_chastisement.delete()


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
