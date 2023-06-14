from datacenter.models import *
import random


def fix_marks(child_name):
    """Исправляем оценки меньше тройки ученика на пятерки."""
    child = Schoolkid.objects.get(full_name__contains=child_name).full_name
    child_marks = Mark.objects.filter(schoolkid__full_name=child, points__lte=3)
    for child_mark in child_marks:
        child_mark.points = '5'


def remote_chastisements(child_name):
    """Удаляем замечания с учетной записи ученика."""
    chastisement_child = Chastisement.objects.filter(schoolkid__full_name__contains=child_name)
    chastisement_child.delete()


def create_commendation(child_name, subject):
    """Создаем похвалительную речь для ученика на случайном уроке одного из предмета."""
    subject = Lesson.objects.filter(year_of_study=6, group_letter='А', subject__title=subject)
    lesson = random.choice(subject)
    child = Schoolkid.objects.get(full_name__contains=child_name)
    Commendation.objects.create(text='Хвалю', created=lesson.date, schoolkid=child, subject=lesson.subject,
                                teacher=lesson.teacher)
