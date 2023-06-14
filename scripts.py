from datacenter.models import *
import random


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
