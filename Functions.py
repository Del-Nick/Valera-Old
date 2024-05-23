import pymorphy2
from Database import check_group, change_action, all_data, check_time_schedule, check_headman, check_books, check_studsovet
from datetime import datetime, timedelta
from vkbottle import Keyboard, KeyboardButtonColor, Text
import requests
import math
from config import owner_id, app_token, token
import os
import openpyxl
from Arrays import workshop_rooms
from Rooms import floors_coord
import traceback
import fitz
import json
from prettytable import PrettyTable, PLAIN_COLUMNS, MARKDOWN


def weekday():
    return datetime.today().weekday()


def number_of_week():
    return datetime.today().isocalendar()[1]


def word_normalized(text):
    morph = pymorphy2.MorphAnalyzer()
    return morph.parse(text)[0].normal_form


def schedule(id, group):
    with open('Schedule.json', encoding='utf-8') as f:
        try:
            data = json.load(f)[group]
            number_of_week_var = number_of_week() - 34

            day = weekday()
            date = datetime.now()
            if day == 6:
                day = 0
                date += timedelta(days=1)
                number_of_week_var += 1
            elif datetime.now().strftime('%H:%M') > check_time_schedule(id):
                if day == 5:
                    day = 0
                    date += timedelta(days=2)
                    number_of_week_var += 1
                else:
                    day += 1
                    date += timedelta(days=1)

            answer = list(data.keys())[day].upper() + ', ' + date.strftime('%d.%m') + '\n\n'

            day = list(data.keys())[day]

            if number_of_week_var % 2 != 0:
                for lesson in data[day].keys():
                    temp = data[day][lesson]["odd"]
                    if temp["lesson"] != '':
                        time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40', '18:55-20:30']
                        answer += f'{time[int(lesson)-1]}  {temp["lesson"]}  {temp["room"]}\n'
            else:
                for lesson in data[day].keys():
                    temp = data[day][str(lesson)]["even"]
                    if temp["lesson"] != '':
                        time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40', '18:55-20:30']
                        answer += f'{time[int(lesson)-1]}  {temp["lesson"]}  {temp["room"]}\n'

            num_of_lessons = len(answer.split('\n'))-3

            if num_of_lessons == 1:
                answer += '\nУ тебя 1 пара'
            elif num_of_lessons < 5:
                answer += f'\nУ тебя {num_of_lessons} пары'
            else:
                answer += f'\nУ тебя {num_of_lessons} пар'

            return answer

        except Exception as Ex:
            print(Ex)
            return 'Вот это дела. Расписание украли!'


def week_schedule(id, group):
    with open('Schedule.json', encoding='utf-8') as f:
        try:
            data = json.load(f)[group]
            number_of_week_var = number_of_week() - 5

            day = weekday()
            date = datetime.now()

            next_week = False
            if day == 6:
                number_of_week_var += 1
                next_week = True
                answer = f'Следующая неделя № {number_of_week_var}\n\n'
            elif datetime.now().strftime('%H:%M') > check_time_schedule(id):
                if day == 5:
                    number_of_week_var += 1
                    next_week = True
                    answer = f'Следующая неделя № {number_of_week_var}\n\n'
                else:
                    answer = f'Неделя № {number_of_week_var}\n\n'
            else:
                answer = f'Неделя № {number_of_week_var}\n\n'

            time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40', '18:55-20:30']

            parity = "even" if number_of_week_var % 2 == 1 else 'odd'

            for day_of_week in data.keys():
                if next_week:
                    answer += day_of_week.upper() + ', ' + (
                            date - timedelta(days=date.weekday() - list(data.keys()).index(day_of_week) - 7)).strftime(
                        '%d.%m') + '\n\n'
                else:
                    answer += day_of_week.upper() + ', ' + (
                            date - timedelta(days=date.weekday() - list(data.keys()).index(day_of_week))).strftime(
                        '%d.%m') + '\n\n'
                for lesson in data[day_of_week].keys():
                    temp = data[day_of_week][lesson][parity]
                    if temp["lesson"] != '':
                        answer += f'{time[int(lesson) - 1]}  {temp["lesson"]}  {temp["room"]}\n'

                answer += '\n\n'

            return answer

        except:
            return 'Вот это дела. Расписание украли!'


def settings(id):
    change_action(id, 'Settings')
    data = all_data(id)
    if len(data[10].split(', ')) == 1:
        answer = 'ID: %s\n' \
                 'Имя: %s\n' \
                 'Фамилия: %s\n' \
                 'Группа: %s\n' \
                 'Время перехода: %s' % (data[0], data[1], data[2], data[10], data[9])

    else:
        groups = data[10].split(',')
        add_group = ''
        for i in groups[1:len(groups) - 1]:
            add_group += i + ', '
        add_group += groups[len(groups) - 1]
        answer = 'ID: %s\n' \
                 'Имя: %s\n' \
                 'Фамилия: %s\n' \
                 'Группа: %s\n' \
                 'Доп. группы: %s\n' \
                 'Время перехода: %s' % (data[0], data[1], data[2], groups[0], add_group, data[9])
    keyboard = setiings_keyboard()

    return [answer, keyboard]


def standard_keyboard(id):
    headman = check_headman(id)
    keyboard = Keyboard(one_time=True) \
        .add(Text('&#128466; ДЗ'), color=KeyboardButtonColor.POSITIVE) \
        .add(Text('&#128218; Учебники'), color=KeyboardButtonColor.POSITIVE) \
        .add(Text('&#128300; ОФП'), color=KeyboardButtonColor.POSITIVE) \
        .row() \
        .add(Text('&#128198; Расписание'), color=KeyboardButtonColor.POSITIVE) \
        .add(Text('7&#8419;&#128198; На неделю'), color=KeyboardButtonColor.POSITIVE) \
        .row().add(Text('&#128218; Сессия'), color=KeyboardButtonColor.POSITIVE) \
        .row().add(Text('&#9881; Настройки'))


    # .add(Text('&#128373; ККО'), color=KeyboardButtonColor.PRIMARY).row() \

    # keyboard.add(Text('&#128198; Сессия'), color=KeyboardButtonColor.POSITIVE) \
        
    if headman:
        # keyboard.row()
        keyboard.add(Text('&#128526; Cтароста Mode'))

    return keyboard


def setiings_keyboard():
    return Keyboard(one_time=True) \
        .add(Text('&#8987; Время перехода на новый день'), color=KeyboardButtonColor.PRIMARY) \
        .row() \
        .add(Text('&#128256; Сменить группу'), color=KeyboardButtonColor.PRIMARY) \
        .row() \
        .add(Text('Добавить группу'), color=KeyboardButtonColor.POSITIVE) \
        .add(Text('Удалить группу'), color=KeyboardButtonColor.NEGATIVE) \
        .row() \
        .add(Text('&#128450; История разработки')) \
        .row() \
        .add(Text('&#128281; Вернуться в главное меню'))


def group_keyboard(id):
    groups = check_group(id).split(', ')
    keyboard = Keyboard(one_time=True)
    for group in range(len(groups)):
        keyboard.add(Text('%s' % groups[group]))
    return keyboard


def subjects_keyboard(buttons, id, Starosta_Mode):
    keyboard = Keyboard(one_time=True)
    temp = False
    for button in range(len(buttons)):
        temp = False
        keyboard.add(Text('%s' % buttons[button]), color=KeyboardButtonColor.PRIMARY)
        if (button + 1) % 2 == 0:
            keyboard.row()
            temp = True

    if not Starosta_Mode:
        if not temp:
            keyboard.row()
        keyboard.add(Text('Вернуться в главное меню'))

    if check_headman(id) and Starosta_Mode:
        if not temp:
            keyboard.row()

        keyboard.add(Text('Добавить предмет'), color=KeyboardButtonColor.POSITIVE) \
            .row() \
            .add(Text('Удалить предмет'), color=KeyboardButtonColor.NEGATIVE) \
            .row() \
            .add(Text('Вернуться в меню старосты'), color=KeyboardButtonColor.SECONDARY)

    return keyboard


def headman_keyboard(action=''):
    if action == 'ДЗ':
        buttons = ['Добавить ДЗ', 'Удалить ДЗ', 'Вернуться к списку предметов', 'NEGATIVE']
    elif action == 'Учебник':
        buttons = ['Добавить учебник', 'Удалить учебник', 'Вернуться в меню старосты', 'NEGATIVE']
    elif action == 'Сессия':
        buttons = ['Добавить зачёт/экзамен', 'Удалить зачёт/экзамен', 'Вернуться в меню старосты', 'NEGATIVE']
    else:
        buttons = ['Редактировать учебники', 'Редактировать ДЗ', 'Вернуться в главное меню', '']

    keyboard = Keyboard(one_time=True)
    for i in range(len(buttons) - 2):
        if i == 1:
            if buttons[len(buttons) - 1] == 'NEGATIVE':
                keyboard.add(Text('%s' % buttons[i]), color=KeyboardButtonColor.NEGATIVE).row()
            else:
                keyboard.add(Text('%s' % buttons[i]), color=KeyboardButtonColor.POSITIVE).row()
        else:
            keyboard.add(Text('%s' % buttons[i]), color=KeyboardButtonColor.POSITIVE).row()

    keyboard.add(Text('%s' % buttons[len(buttons) - 2]), color=KeyboardButtonColor.SECONDARY)
    return keyboard


def custom_keyboard(buttons):
    keyboard = Keyboard(one_time=True)
    koef = int(5 * math.exp(-0.05 * len(str(max(buttons)))))
    for button in range(len(buttons)):
        keyboard.add(Text('%s' % buttons[button]))

        if (button + 1) % koef == 0:
            keyboard.row()
    keyboard.add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE)
    return keyboard


def editing_books(id):
    return check_books(check_group(id).split(', ')[0])


def workshop(id: str, group: str):
    if os.path.exists(f'Практикумы/{group}.json'):
        with open(f'Практикумы/{group}.json', encoding='utf-8') as f:
            schedule_workshop = json.load(f)

            def text_designer(workshops: dict):
                answer = f'⠀Дата⠀⠀Номер⠀⠀Оценка⠀\n'
                for date in workshops.keys():
                    answer += f'{"·" * 50}\n'
                    num = workshops[date]["num"]
                    grade = workshops[date]["mark"]
                    if grade == 'Нет оценки':
                        answer += f'⠀{date}⠀⠀⠀{num}\n'
                    else:
                        answer += f'⠀{date}⠀⠀⠀{num}⠀⠀⠀⠀{grade}\n'
                return answer

            if id in schedule_workshop.keys():
                return text_designer(schedule_workshop[id])
            else:
                return 'Не смог найти тебя в таблице &#128532;'
    else:
        return 'Староста твоей группы ещё не добавил расписание практикумов'


def search_workshop_room(workshop):
    try:
        for key in workshop_rooms.keys():
            if workshop in workshop_rooms[key]:
                break
        return key
    except:
        traceback.print_exc()
        return 'Не найден'


def homework(id):
    return 'Раздел находится в разработке'


def books(id):
    return 'Раздел находится в разработке'


def lst2pgarr(alist):
    return ','.join(alist)


def lst2pgarr_homework(list):
    return ','.join(list)


def lst2pgarr_attach(list):
    return ','.join(list)


def collect_books(workshop):
    url = 'https://api.vk.com/method/docs.get'
    data = {
        'owner_id': owner_id,
        'access_token': app_token,
        'v': '5.131'
    }
    response = requests.get(url, params=data)
    response = response.json()

    if 'error' in response.keys():
        return 'Произошла какая-то ошибка, но мы о ней уже знаем и работаем над устранением ;)'
    names = []
    for i in range(len(response['response']['items'])):
        names.append(response['response']['items'][i]['title'])

    num = 0
    try:
        while True:
            if response['response']['items'][num]['title'] == workshop:
                break
            num += 1

        doc_owner_id = response['response']['items'][num]['owner_id']
        doc_id = response['response']['items'][num]['id']

        link = 'doc%s_%s' % (owner_id, doc_id)
        return link
    except:
        traceback.print_exc()
        return 'Не удалось найти методичку'


def check_books_in_group():
    books = collect_books()


def parse_attachments(id):
    url = 'https://api.vk.com/method/messages.getHistory'
    data = {
        'user_id': id,
        'access_token': token,
        'count': 1,
        'v': '5.131'
    }
    response = requests.get(url, params=data)
    response = response.json()

    attachments = []
    temp = response['response']['items'][0]['attachments']
    for num in range(len(temp)):
        file_type = temp[num]['type']
        access_key = temp[num][file_type]['access_key']
        owner_id = temp[num][file_type]['owner_id']
        doc_id = temp[num][file_type]['id']
        attach = f'{file_type}{owner_id}_{doc_id}_{access_key}'
        attachments.append(attach)
        num += 1

    return attachments


def check_rooms(text):
    try:
        text = text.lower().replace(' ', '').replace('.', '')

        if text in ['библиотек', 'ниияф', 'цфа', 'юфа', 'сфа', 'лкаб']:
            pass
        elif text == 'учебнаячасть':
            text = '2-38'
        elif text == 'аудхохлова' or text == 'аудимхохлова':
            text = 'цфа'
        elif text == 'вус':
            text = '5-68а'
        elif text[1] == ' ':
            text[1] = '-'
        elif text == 'лингафон':
            text = 'л.каб'
        elif 'ру' in text:
            if text[2] == ' ':
                text[2] = '-'
            elif text[2] != '-':
                text = text[:2] + '-' + text[2:]
        elif text[1] != '-':
            text = text[0] + '-' + text[1:]

        for floor in floors_coord:
            if text in floor.keys():

                if 'ру' in text:
                    num_letter = 3
                else:
                    num_letter = 0

                if ('сфа' in text) or ('цфа' in text) or ('юфа' in text):
                    floor = 2
                elif text[num_letter] == 'ц':
                    floor = 0
                elif text[num_letter].isdigit():
                    floor = int(text[num_letter])
                elif text in ['ниияф', 'библиотека', 'лкаб']:
                    floor = 5

                x_1, y_1, x_2, y_2 = floors_coord[floor][text]

                if floor in [0, 1, 2]:
                    if x_2 > 1370:
                        part = 'Тебе на юг'
                    elif x_1 < 950:
                        part = 'Тебе на север'
                    else:
                        part = 'Тебе в центральную часть'
                elif floor == 3:
                    if x_2 > 1430:
                        part = 'Тебе на юг'
                    elif x_1 < 1050:
                        part = 'Тебе на север'
                    else:
                        part = 'Тебе в центральную часть'
                elif floor == 4:
                    if x_2 > 1470:
                        part = 'Тебе на юг'
                    elif x_1 < 1045:
                        part = 'Тебе на север'
                    else:
                        part = 'Тебе в центральную часть'
                elif floor == 5:
                    if x_2 > 1450:
                        part = 'Тебе на юг'
                    elif x_1 < 1010:
                        part = 'Тебе на север'
                    else:
                        part = 'Тебе в центральную часть'

                return text, floor, part

        return False

    except Exception as Ex:
        traceback.print_exc()


def schedule_session(group):

    words_for_delete = ['профессор',
                        'доцент',
                        'преподават',
                        'преподават',
                        'понедельник',
                        'вторник',
                        'среда',
                        'четверг',
                        'пятница',
                        'суббота',
                        'воскресенье',
                        'экзамен',
                        'препода',
                        'преподават',
                        'ст.',
                        'ассистент',
                        ' науч. сот',
                        'науч. сотру',
                        'мл. науч. со']
    group = group.lower()
    try:
        if 'м' in group.lower():
            path = 'Сессия/Маги1.pdf'
        else:
            path = f'Сессия/Спец{group[0]}.pdf'

        text = ''
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()

        for word in words_for_delete:
            text = text.replace(word, '')
        text = text.split('\n')[11:-7]

        for i in range(len(text) - 1, 0, -1):
            if 'Страница' in text[i] or 'Дата' in text[i] or 'мая' in text[i] or text[i] == '' or text[i] == '.':
                text.pop(i)

        schedule = {}
        for i in range(len(text)):
            if text[i] == 'группа':
                iterator = 2
                try:
                    while text[i + iterator] != 'группа':
                        if text[i + iterator][2] == '.':
                            if iterator < 3:
                                schedule[text[i + 1]] = [[text[i + iterator]]]
                            else:
                                schedule[text[i + 1]].append([text[i + iterator]])
                        else:
                            schedule[text[i + 1]][-1].append(text[i + iterator])
                        iterator += 1
                except:
                    pass

        [print(key, schedule[key]) for key in schedule.keys()]


        answer = []
        for examine in schedule[group]:
            temp = ''
            # for i in range(65):
            #     temp += '-'
            temp += f'\n&#128197; {examine[0].replace(".2023", "")}⠀⠀⠀{examine[1]}⠀⠀⠀{examine[3]}\n\n'
            for i in examine[5:]:
                temp += i
            temp += '\n'
            for i in range(15):
                temp += '━'
            if temp not in answer:
                answer.append(temp)

        return answer
    except:
        traceback.print_exc()
        return 'Почему-то я не смог найти твоё расписание сессии. Уже разбираюсь в проблеме &#128373;'