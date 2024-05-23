import datetime
import json
import time

from vkbottle import API
from vkbottle.bot import Bot, Message
from vkbottle.tools import PhotoMessageUploader
from Database import *
from Arrays import groups, workshop_rooms
from Functions import *
from History_of_development import history
from config import token
from loguru import logger
import sys
from Rooms import rooms
from quize import *
import asyncio
import random
import gc
import threading

from KKO import kko
from Database_KKO import all_data_kko, check_subjects_kko, delete_user_kko

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="DEBUG")
# logger.remove()

bot = Bot(token=token)
uploader = PhotoMessageUploader(bot.api)

checking()


@bot.on.private_message()
async def message_handler(message: Message):
    user = await bot.api.users.get(message.from_id)
    id = user[0].id
    first_name = user[0].first_name
    last_name = user[0].last_name

    num_of_conn(id)
    update_last_connection(id)
    answer_is_found = False

    if not check_id(id):
        answer_is_found = True
        add_new_user(id, first_name, last_name)
        await message.answer(
            'Привет, %s! Меня зовут Валера, я твой чат-бот. Если вдруг ты запутался и не знаешь выход, просто позови меня по имени, и я тебя вытащу.' %
            user[0].first_name)
        await message.answer(
            'Давай немного познакомимся. Для полноценной работы мне необходимо знать твою группу. Напиши её, пожалуйста. '
            'Если ты не студент физического факультета, нажми на кнопку.',
            keyboard=Keyboard(one_time=True).add(Text('Я не студент физфака'), color=KeyboardButtonColor.NEGATIVE))

    elif check_action(id) == 'Add_group':
        answer_is_found = True
        if message.text == 'Отмена':
            change_action(id, 'Start')
            await message.answer('Мы в главном меню', keyboard=standard_keyboard(id))
        else:
            if message.text in groups:
                if check_group(id) is None:
                    add_group(id, message.text)

                    await message.answer(
                        'Отлично, %s! Я запомнил, что ты из группы %s. Этот параметр можно будет изменить в настройках. Теперь я буду искать информацию для тебя персонально' % (
                            first_name, message.text), keyboard=standard_keyboard(id))
                    change_action(id, 'Start')

                else:
                    add_group(id, message.text)
                    await message.answer(
                        'Отлично, %s! Я добавил в список твоих групп %s. Этот параметр можно будет изменить в настройках. Теперь ты сможешь выбирать, для какой группы смотреть информацию' % (
                            first_name, message.text), keyboard=standard_keyboard(id))
                    change_action(id, 'Start')

            elif message.text == 'Я не студент физфака':
                change_action(id, 'Not_student')
                await message.answer(
                    "Хорошо, %s. Я запомнил, что ты не с физического факультета. Пожалуйста, продублируй сообщение, чтобы мы его не пропустили.\n\nP.s. Если кнопка была нажата по ошибке, ты всегда можешь написать 'Я студент физфака' или 'Я студентка физфака', чтобы зарегистрироваться." %
                    user[0].first_name)
            else:
                await message.answer(
                    "Не могу найти такую группу. Я брал все номера отсюда: http://ras.phys.msu.ru . Проверь правильность ввода и попробуй ещё раз")

    elif check_action(id) == 'Pervokursnik':
        answer_is_found = True
        if 'тык' in message.text.lower():
            await message.answer(f'Отлично! Поехали!')
            await message.answer('Студенческий совет — это выборный орган студенческого самоуправления факультета. '
                                 'Каждый год у нас проходят открытые выборы, на которых студенты каждого курса '
                                 'выбирают членов совета. Но участвовать в работе могут абсолютно все желающие вне '
                                 'зависимости от результатов выборов')
            await asyncio.sleep(1)
            await message.answer('Мы защищаем права ВСЕХ студентов в составе Комиссии по студенческим делам, '
                                 'в Стипендиальной комиссии, на Учёном совете факультета, а также в рамках работы '
                                 'Студенческого совета МГУ.',

                                 keyboard=Keyboard(one_time=True).add(Text('&#128525; Круто!'),
                                                                      color=KeyboardButtonColor.POSITIVE))
            change_action(id, 'Pervokursnik_2')
        else:
            aneqdots = ['Чему равна скорость света в темноте?',
                        'Отец так хотел, чтобы его сын стал физиком, что бил его не ремнем, а током...',
                        'Не можешь найти работу? Умножь время на мощность.']
            await message.answer(aneqdots[random.randint(0, len(aneqdots) - 1)])
            await asyncio.sleep(1)
            await message.answer('Давай пользоваться клавиатурой?)',
                                 keyboard=Keyboard(one_time=True).add(Text('&#128071; Тык на эту кнопочку &#128071;'),
                                                                      color=KeyboardButtonColor.POSITIVE))

    elif check_action(id) == 'Pervokursnik_2':
        answer_is_found = True
        if 'круто' in message.text.lower():
            await message.answer('&#128071; Смотри ниже, какие проекты реализует и какие мероприятия организовывает '
                                 'наша команда. Каждый год мы создаем новые и улучшаем действующие проекты, '
                                 'объединяемся с другими студенческими организациями для получения интересного, '
                                 'полезного и качественного материала. Поступай правильно! Присоединяйся!',
                                 attachment=['photo-34300772_457245247', 'photo-34300772_457245246'],
                                 keyboard=Keyboard(one_time=True).add(Text('Олимпиады??'),
                                                                      color=KeyboardButtonColor.POSITIVE))
            change_action(id, 'Pervokursnik_3')
        else:
            await message.answer('Show must go on!')
            await asyncio.sleep(1)
            await message.answer('Давай пользоваться клавиатурой?)',
                                 keyboard=Keyboard(one_time=True).add(Text('&#128525; Круто!'),
                                                                      color=KeyboardButtonColor.POSITIVE))

    elif check_action(id) == 'Pervokursnik_3':
        answer_is_found = True
        if 'олимпиады' in message.text.lower():
            await message.answer('Да, они самые. Победители получают автомат за экзамен, а призёры — за зачёт. '
                                 'Награждение проводит сам декан на Учёном совете, а ещё можно выиграть ценные призы, '
                                 'так что следи за сообщениями в группе',
                                 attachment='photo-34300772_457245245',
                                 keyboard=Keyboard(one_time=True).add(Text('Вау!'),
                                                                      color=KeyboardButtonColor.POSITIVE))
            change_action(id, 'Pervokursnik_4')
        else:
            await message.answer('Нет, так не пойдёт')
            await asyncio.sleep(1)
            await message.answer('Там снизу есть кнопочка)',
                                 keyboard=Keyboard(one_time=True).add(Text('Олимпиады??'),
                                                                      color=KeyboardButtonColor.POSITIVE))

    elif check_action(id) == 'Pervokursnik_4':
        answer_is_found = True
        if 'вау' in message.text.lower():
            await message.answer(
                'Ну, а чтобы не пропустить ничего важного, мы подготовили для тебя полезные ссылки:\n\n'
                '▪ Смотреть интервью со своим преподавателем: https://vk.cc/cqxkfm\n▪ Получить '
                'оценку автоматом за олимпиаду (там также есть бот Афина, поможет с регистрацией, '
                'когда начнётся сезон олимпиад): https://vk.com/olympff\n▪ Следить за информацией о '
                'предстоящих мероприятиях и ведущих проектах: https://vk.com/sovet_phys',
                keyboard=Keyboard(one_time=True).add(Text('Уже подписываюсь!'),
                                                     color=KeyboardButtonColor.POSITIVE))
            change_action(id, 'Pervokursnik_5')
        else:
            await message.answer('Там снизу есть кнопочка)',
                                 keyboard=Keyboard(one_time=True).add(Text('Вау!'),
                                                                      color=KeyboardButtonColor.POSITIVE))

    elif check_action(id) == 'Pervokursnik_5':
        answer_is_found = True
        if 'подписываюсь' in message.text.lower():
            await message.answer('Вот мы и в главном меню', keyboard=standard_keyboard(id))
            change_action(id, 'Start')
        else:
            await message.answer('Там снизу есть кнопочка)',
                                 keyboard=Keyboard(one_time=True).add(Text('Уже подписываюсь!'),
                                                                      color=KeyboardButtonColor.POSITIVE))

    elif 'Валер' in message.text:
        if message.text == 'Валера, сотри меня в порошок':
            if id in [318861079, 299407304, 240971040, 242303569, 412879243, 170292016, 314219688, 630183515, 314479638,
                      591102411, 159851240, 217602739, 172038913]:
                answer_is_found = True
                if delete_user(id):
                    await message.answer('Данные успешно удалены. Ты можешь зарегистрироваться заново')
                else:
                    await message.answer('Что-то пошло не по плану')
        elif check_action(id) == 'Not_student' or check_group(id) is None:
            answer_is_found = True
            await message.answer(
                'Мои функции доступны только для студентов физического факультета. Если кнопка в начале знакомства '
                'была нажата по ошибке, ты всегда можешь написать "Я студент физфака" или "Я студентка физфака", '
                'чтобы зарегистрироваться')
        # elif 'KKO' in check_action(id):
        #     answer_is_found = True
        #     await message.answer(
        #         'Заверши, пожалуйста, прохождение опроса. После этого все функции вновь будут доступны')
        else:
            answer_is_found = True
            change_action(id, 'Start')
            await message.answer('Любовь, надежда и вера-а-а', keyboard=standard_keyboard(id))

    # if message.text == 'Уран делиться не хотел, так обобрали' and check_studsovet(id):
    #     answer_is_found = True
    #     reset_quize(id)
    #     await message.answer('Данные о прохождении викторины удалены', keyboard=standard_keyboard(id))
    #     change_action(id, 'Start')

    elif check_action(id) == 'Start':
        if 'Расписание' in message.text:
            answer_is_found = True
            if len(check_group(id).split(', ')) > 1:
                await message.answer('Выбери номер группы', keyboard=group_keyboard(id))
                change_action(id, 'Choose_group')
            else:
                await message.answer('&#10071; Расписание проходило выборочную проверку и может содержать неточности. '
                                     'Если видишь ошибку, пиши в свободной форме и отправляй, а потом зови человека',
                                     keyboard=standard_keyboard(id))
                schedule_temp = schedule(id, check_group(id))
                await message.answer(schedule_temp, keyboard=standard_keyboard(id))
            # await message.answer('Как только расписание появится, сразу добавим &#128521;', keyboard=standard_keyboard(id))

        elif 'На неделю' in message.text:
            answer_is_found = True
            if len(check_group(id).split(', ')) > 1:
                await message.answer('Выбери номер группы', keyboard=group_keyboard(id))
                change_action(id, 'Choose_group_week_schedule')
            else:
                await message.answer('&#10071; Расписание проходило выборочную проверку и может содержать неточности. '
                                     'Если видишь ошибку, пиши в свободной форме и отправляй, а потом зови человека',
                                     keyboard=standard_keyboard(id))
                week_schedule_temp = week_schedule(id, check_group(id))
                await message.answer(week_schedule_temp, keyboard=standard_keyboard(id))

            # await message.answer('Как только расписание появится, сразу добавим &#128521;', keyboard=standard_keyboard(id))

        elif 'Сессия' in message.text:
            answer_is_found = True
            if len(check_group(id).split(', ')) > 1:
                await message.answer('Выбери номер группы', keyboard=group_keyboard(id))
                change_action(id, 'Session_choose_group')
            else:
                group = check_group(id)
                with open('Session_Schedule.json', 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    try:
                        session = session[group]

                        days_left = []
                        for exam in session:
                            date_str = f'{exam["date"][:5]} {exam["time"]}'
                            date = datetime.datetime.strptime(date_str, "%d.%m %H:%M").replace(year=2024)
                            if date > datetime.datetime.today():
                                days_left.append(date - datetime.datetime.today())
                                check_mark_sticker = '&#9745;'
                            else:
                                check_mark_sticker = '&#9989;'

                            text = f'{check_mark_sticker}{exam["name"]}\n\n' \
                                   f'&#128198; Дата:  {exam["date"]}\n' \
                                   f'&#8986; Время: {exam["time"]}\n' \
                                   f'&#128205; Место: {exam["room"]}\n' \
                                   f'🎓 Преподаватель:  {exam["teacher"]}'
                            await message.answer(text, keyboard=standard_keyboard(id))

                        days_left.sort()
                        days_left = days_left[0]

                        hours = days_left.seconds // 3600
                        minutes = days_left.seconds // 60 % 60
                        seconds = days_left.seconds % 60

                        answer = f'До ближайшего экзамена'

                        if days_left.days == 1:
                            answer += f' {days_left.days} день'
                        elif 1 < days_left.days < 5:
                            answer += f' {days_left.days} дня'

                        elif days_left.days > 0:
                            answer += f' {days_left.days} дней'

                        if hours % 10 == 1:
                            answer += f' {hours} час'
                        elif 1 < hours % 10 < 5 and not 11 < hours < 15:
                            answer += f' {hours} часа'
                        elif hours > 0:
                            answer += f' {hours} часов'

                        if minutes % 10 == 1 and minutes != 11:
                            answer += f' {minutes} минута'
                        elif 1 < minutes % 10 < 5 and not 11 < minutes < 15:
                            answer += f' {minutes} минуты'
                        elif minutes > 0:
                            answer += f' {minutes} минут'

                        if seconds % 10 == 1 and seconds != 11:
                            answer += f' {seconds} секунда'
                        elif 1 < seconds % 10 < 5 and not 11 < seconds < 15:
                            answer += f' {seconds} секунды'
                        else:
                            answer += f' {seconds} секунд'

                        await message.answer(answer,
                                             keyboard=standard_keyboard(id))

                    except KeyError:
                        await message.answer(
                            'Не могу найти твою группу в расписании. Пожалуйста, ответь в свободной форме, '
                            'а потом позови человека, чтобы мы исправили ошибку',
                            keyboard=standard_keyboard(id))

        elif check_rooms(message.text):
            answer_is_found = True
            try:
                room, floor, part = check_rooms(message.text)
                await message.answer(part)
                path = rooms(room, floor)
                scheme = await uploader.upload(file_source=f'{path}')
                await message.answer('Нужный кабинет обозначен оранжевым цветом &#128521;', attachment=scheme,
                                     keyboard=standard_keyboard(id))
                os.remove(path)
                change_action(id, 'Start')
            except Exception as Ex:
                await message.answer('Не удалось загрузить изображение. Уже копаюсь в себе, ищу очередной триггер',
                                     keyboard=standard_keyboard(id))
                print(Ex)

        # elif 'День российской науки' in message.text:
        #     answer_is_found = True
        #
        #     await message.answer('ДЕНЬ РОССИЙСКОЙ НАУКИ')
        #     await message.answer('Экскурсия в ФИАН\nРегистрация: https://vk.cc/cupR4K.')
        #     await message.answer('💙8 февраля\n\nЛекция на тему «Бозе-звезды из легкой темной материи».\n'
        #                          'Лектор: к. ф.-м. н., научный сотрудник ИЯИ РАН и ИТМФ МГУ Левков Дмитрий '
        #                          'Геннадьевич.\n'
        #                          '📍ЦФА, 15:20 — 16:30.')
        #     await message.answer('❤9 февраля\n\nМастер-класс «Научный постер: как сделать понятно и красиво».\n'
        #                          'Эксперт: Виктория Ипатова.\n'
        #                          '📍Холл ЦФА, 17:00 — 19:00.\n\n'
        #                          'Экскурсия в Лабораторию радиационной обработки биообъектов и материалов.\n'
        #                          'Регистрация: https://vk.cc/cupRfp.\n'
        #                          '📍 Ленинские Горы, 1 ст58.\n'
        #                          'Начало: 15:30.')
        #     await message.answer('💙12 февраля\n\nЭкскурсия на кафедру физики твёрдого тела.\n'
        #                          'Регистрация: https://vk.cc/cupRfp.\n'
        #                          'Начало в 12:40.')
        #     await message.answer('❤ 13 февраля\n\nЭкскурсия на кафедру общей физики и молекулярной электроники.\n'
        #                          'Регистрация: https://vk.cc/cupRfp.\n\n'
        #                          'Экскурсия в Лабораторию плазмы.\n'
        #                          'Регистрация: https://vk.cc/cupRfp.')
        #     await message.answer('💙 14 февраля\n\nМежфакультетский квиз\n'
        #                          'Зови друзей и заходи в беседу команд фф: https://vk.cc/culm8P.\n'
        #                          '📍Холл ЦФА, 15:30.\n\n'
        #                          'Экскурсия в АО «Корпорация «Комета». Закрытое предприятие, будет трансфер от факультета.\n'
        #                          'Регистрация: https://vk.cc/cupSSQ.\n'
        #                          '📍Встреча у физического факультета, 14:00.')
        #     await message.answer('❤ 16 февраля\n\nЭкскурсия в РКЦ\n'
        #                          'Регистрация: https://vk.cc/cun63f.\n'
        #                          'Начало в 14:00\n\n'
        #                          'Экскурсия в Сколтех\n'
        #                          'Регистрация: https://vk.cc/culmrH.\n'
        #                          '📍 Большой Бульвар 30 с1, 15:00 — 18:00\n\n'
        #                          'Экскурсия в Лабораторию кафедры полимеров и кристаллов\n'
        #                          'Регистрация: https://vk.cc/cun63f.\n'
        #                          '📍Ц-49 (цокольный этаж физического факультета), начало в 14:00',
        #                          keyboard=standard_keyboard(id))

        elif 'Настройки' in message.text:
            answer_is_found = True
            change_action(id, 'Settings')
            await message.answer(settings(id)[0], keyboard=settings(id)[1])

        elif 'Cтароста Mode' in message.text:
            answer_is_found = True
            change_action(id, 'Headman_mode')
            await message.answer('Starosta_mode: ON', keyboard=headman_keyboard())

        elif 'Учебник' in message.text:
            answer_is_found = True
            group = check_group(id).split(', ')[0]
            if (check_books(group) is None) or (check_books(group) == 'Error'):
                await message.answer('Староста ещё не добавил учебники. Возвращаюсь в главное меню',
                                     keyboard=standard_keyboard(id))
            else:
                answer = check_books(group)
                for num in range(len(answer['Title'])):
                    await message.answer('%d. %s' % (num + 1, answer['Title'][num]), attachment=answer['Link'][num])
                await message.answer('Возвращаюсь в главное меню', keyboard=standard_keyboard(id))

        elif 'ДЗ' in message.text:
            answer_is_found = True
            group = check_group(id).split(', ')[0]
            if check_subject(group) is None:
                await message.answer(
                    'Предметы ещё не добавлены. Обратись к своему старосте. Если возникают проблемы, напиши в сообщения группы',
                    keyboard=standard_keyboard(id))
                change_action(id, 'Start')
            else:
                subjects = check_subject(group)
                await message.answer('Выбери предмет', keyboard=subjects_keyboard(subjects, id, False))
                change_action(id, 'Homework')

        # elif 'ККО' in message.text:
        #     answer_is_found = True
        #     if all_data_kko(id) is None:
        #         await message.answer('Мы запускаем опрос по качеству образования в осеннем семестре 2023/2024'
        #                              ' учебного года для всех учебных курсов. Просим Вас уделить этому особое внимание, так как'
        #                              ' нами будет представлен отчёт о реализации образовательных программ перед учебной частью и '
        #                              'деканом. Чем больше отзывов будет получено, тем выше вероятность изменений.\n\nПосле начала '
        #                              'прохождения нужно будет пройти опрос до конца. На это время другие функции бота будут '
        #                              'недоступны')
        #         await message.answer('Начинаем?',
        #                              keyboard=Keyboard(one_time=True).add(Text('Нет'),
        #                                                                   color=KeyboardButtonColor.NEGATIVE)
        #                              .add(Text('Да'), color=KeyboardButtonColor.POSITIVE))
        #         change_action(id, 'KKO_prestart')
        #     else:
        #         await message.answer('После начала прохождения нужно '
        #                              'будет пройти опрос до конца. На это время другие функции бота будут недоступны')
        #         keyboard = Keyboard(one_time=True).add(Text('Нет'), color=KeyboardButtonColor.NEGATIVE) \
        #             .add(Text('Да'), color=KeyboardButtonColor.POSITIVE)
        #         if check_studsovet(id) and len(check_subjects_kko(id)) > 0:
        #             keyboard.row().add(Text('Мои ответы'), color=KeyboardButtonColor.SECONDARY)
        #         await message.answer('Начинаем?',
        #                              keyboard=keyboard)
        #         change_action(id, 'KKO_prestart')

        elif 'ОФП' in message.text:
            answer_is_found = True
            group = check_group(id).split(', ')[0]
            first_sem = ['127', '126', '125', '124', '123', '122', '121', '120', '119', '118', '117. Рекомендации',
                         '117', '116', '114',
                         '112', '110', '108', '106', '105', '104', '103', '102', '101']
            second_sem = ['240б', '240', '238', '234', '233', '232', '230',
                          '228', '227', '226', '219m', '219', '218', '210', '208', '207', '206', '205', '204', '202',
                          '201']
            third_sem = ['340', '339', '338', '337', '336', '325', '324', '323', '322', '319', '309',
                         '308М', '308', '307', '305А', '305', '304', '302', '301']
            forth_sem = ['419', '413', '412', '411', '410', '409', '408', '403', '401', '169', '152', '147', '142',
                         '140', '136',
                         '135', '132А', '132', '128']

            answer = workshop(str(id), group)
            await message.answer('%s' % answer)

            if group == '22061999':
                await message.answer(
                    'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                    keyboard=custom_keyboard(list(reversed(first_sem))))
            elif group[0] == '1':

                if datetime.datetime.today().month > 8:
                    await message.answer(
                        'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                        keyboard=custom_keyboard(list(reversed(first_sem))))
                else:
                    await message.answer(
                        'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                        keyboard=custom_keyboard(list(reversed(second_sem))))
            elif group[0] == '2':
                if datetime.datetime.today().month > 8:
                    await message.answer(
                        'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                        keyboard=custom_keyboard(list(reversed(third_sem))))
                else:
                    await message.answer(
                        'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                        keyboard=custom_keyboard(list(reversed(forth_sem))))
            else:
                await message.answer('Введи номер общего физического практикума, и я пришлю тебе методичку',
                                     keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                          color=KeyboardButtonColor.NEGATIVE))
            change_action(id, 'Workshop')
            # await message.answer('%s' % answer, keyboard=standard_keyboard(id))

        # elif message.text == 'Викторина на Неделе атома':
        #     answer_is_found = True
        #     data = quize_all_data(id)
        #     if data is None:
        #         change_action(id, 'Quize')
        #         await message.answer('28 сентября отмечается День работника атомной промышленности')
        #         await asyncio.sleep(2)
        #         await message.answer('В этот раз мы добавили как сложные вопросы, так и простые. Будет время отдохнуть,'
        #                              ' но не расслабиться)')
        #         await asyncio.sleep(2)
        #         await message.answer('Но самое главное, конечно, просто получать удовольствие. Ну, что ж, начинаем?)',
        #                              keyboard=Keyboard(one_time=True)\
        #                              .add(Text('&#128530; Вернусь позже'), color=KeyboardButtonColor.NEGATIVE)\
        #                              .add(Text('&#128519; Да!'), color=KeyboardButtonColor.POSITIVE))

        # else:
        #     answer = quize(id, message.text)
        #     if type(answer) == str:
        #         await message.answer(answer, keyboard=standard_keyboard(id))
        #     else:
        #         await message.answer('Кажется, ты не должен был здесь оказаться. Нолики за единички заехали', keyboard=standard_keyboard(id))

    elif check_action(id) == 'Homework':
        group = check_group(id).split(', ')[0]
        subjects = check_subject(group)

        if 'Вернуться в главное меню' in message.text:
            answer_is_found = True
            change_action(id, 'Start')
            await message.answer('Возвращаюсь в главное меню', keyboard=standard_keyboard(id))

        elif subjects is None:
            answer_is_found = True
            await message.answer(
                'Предметы ещё не добавлены. Обратись к своему старосте. Если возникают проблемы, напиши в сообщения группы',
                keyboard=standard_keyboard(id))
            change_action(id, 'Start')

        elif message.text in subjects:
            answer_is_found = True
            homeworks = check_homework(group)[message.text]
            for num in range(len(homeworks['Homeworks'])):
                homework = homeworks['Homeworks'][num]
                attach = homeworks['Attachments'][num]
                await message.answer('%d. %s' % (num + 1, homework), attachment=attach)
            await message.answer('Возвращаюсь к списку предметов', keyboard=subjects_keyboard(subjects, id, False))
            change_action(id, 'Homework')

        else:
            answer_is_found = True
            await message.answer('Не могу найти такой предмет. Для твоего удобства я сделал клавиатуру',
                                 keyboard=subjects_keyboard(subjects, id, False))

    elif check_action(id) == 'Session_choose_group':
        answer_is_found = True
        group = message.text
        with open('Session_Schedule.json', 'r', encoding='utf-8') as f:
            session = json.load(f)
            try:
                session = session[group]

                days_left = []
                for exam in session:
                    date_str = f'{exam["date"][:5]} {exam["time"]}'
                    date = datetime.datetime.strptime(date_str, "%d.%m %H:%M").replace(year=2024)
                    if date > datetime.datetime.today():
                        days_left.append(date - datetime.datetime.today())
                        check_mark_sticker = '&#9745;'
                    else:
                        check_mark_sticker = '&#9989;'

                    text = f'{check_mark_sticker}{exam["name"]}\n\n' \
                           f'&#128198; Дата:  {exam["date"]}\n' \
                           f'&#8986; Время: {exam["time"]}\n' \
                           f'&#128205; Место: {exam["room"]}\n' \
                           f'🎓 Преподаватель:  {exam["teacher"]}'
                    await message.answer(text, keyboard=standard_keyboard(id))

                days_left.sort()
                days_left = days_left[0]

                hours = days_left.seconds // 3600
                minutes = days_left.seconds // 60 % 60
                seconds = days_left.seconds % 60

                answer = f'До ближайшего экзамена'

                if days_left.days == 1:
                    answer += f' {days_left.days} день'
                elif 1 < days_left.days < 5:
                    answer += f' {days_left.days} дня'

                elif days_left.days > 0:
                    answer += f' {days_left.days} дней'

                if hours % 10 == 1:
                    answer += f' {hours} час'
                elif 1 < hours % 10 < 5 and not 11 < hours < 15:
                    answer += f' {hours} часа'
                elif hours > 0:
                    answer += f' {hours} часов'

                if minutes % 10 == 1 and minutes != 11:
                    answer += f' {minutes} минута'
                elif 1 < minutes % 10 < 5 and not 11 < minutes < 15:
                    answer += f' {minutes} минуты'
                elif minutes > 0:
                    answer += f' {minutes} минут'

                if seconds % 10 == 1 and seconds != 11:
                    answer += f' {seconds} секунда'
                elif 1 < seconds % 10 < 5 and not 11 < seconds < 15:
                    answer += f' {seconds} секунды'
                else:
                    answer += f' {seconds} секунд'

                await message.answer(answer,
                                     keyboard=standard_keyboard(id))

            except KeyError:
                await message.answer(
                    'Не могу найти твою группу в расписании. Пожалуйста, ответь в свободной форме, '
                    'а потом позови человека, чтобы мы исправили ошибку',
                    keyboard=standard_keyboard(id))
                answer_is_found = False

        change_action(id, 'Start')
        

    elif 'KKO' in check_action(id):
        # answer_is_found, answer, keyboard = kko(id, message.text, ' '.join([first_name, last_name]))
        # if type(answer) is tuple or type(answer) is list:
        #     for i in answer:
        #         if i == answer[-1] and keyboard is not None:
        #             await message.answer(i, keyboard=keyboard)
        #         else:
        #             await message.answer(i)
        # else:
        #     if keyboard is not None:
        #         await message.answer(answer, keyboard=keyboard)
        #     else:
        #         await message.answer(answer)
        change_action(id, 'Start')
        await message.answer('Сбор отзывов в рамках Контроля качества образования завершён. Перехожу в главное меню',
                             keyboard=standard_keyboard(id))

    elif check_action(id) == 'Workshop':
        if 'Отмена' in message.text:
            answer_is_found = True
            await message.answer('Возвращаюсь в главное меню', keyboard=standard_keyboard(id))
        else:
            answer_is_found = True
            link = collect_books(message.text)
            if 'doc' in link:
                await message.answer('Кабинет: %s. Держи' % search_workshop_room(message.text),
                                     attachment='%s' % collect_books(message.text), keyboard=standard_keyboard(id))
            else:
                await message.answer('Не знаю, что со мной сегодня. Не могу найти методичку..',
                                     keyboard=standard_keyboard(id))
        change_action(id, 'Start')

    elif check_action(id) == "Settings":
        if 'Сменить группу' in message.text:
            answer_is_found = True
            if check_headman(id) and not check_admin(id):
                await message.answer(
                    'Староста не может менять группу. Староста, как капитан: покидает корабль последним',
                    keyboard=standard_keyboard(id))
                change_action(id, 'Start')
            else:
                delete_all_groups(id)
                change_action(id, 'Change_main_group')
                await message.answer('Введи новый номер твоей группы, которая будет считаться основной')

        elif 'Добавить группу' in message.text:
            answer_is_found = True
            if len(check_group(id).split(', ')) < 3:
                change_action(id, 'Add_group')
                await message.answer('Введи номер группы, которую ты хочешь добавить',
                                     keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                          color=KeyboardButtonColor.NEGATIVE))
            else:
                await message.answer(
                    'Ты не можешь добавить больше 3 групп. Чтобы добавить новую, удали одну из старых в настройках',
                    keyboard=standard_keyboard(id))
                change_action(id, 'Start')

        elif 'Удалить группу' in message.text:
            answer_is_found = True
            change_action(id, 'Delete_group')
            await message.answer('Введи номер группы, которую ты хочешь удалить',
                                 keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                      color=KeyboardButtonColor.NEGATIVE))

        elif 'Вернуться в главное меню' in message.text:
            answer_is_found = True
            change_action(id, 'Start')
            await message.answer('Мы в главном меню', keyboard=standard_keyboard(id))

        elif 'Время перехода на новый день' in message.text:
            answer_is_found = True
            await message.answer(
                'После %s я присылаю тебе расписание на следующий день. Чтобы изменить этот параметр, введи время в том же формате:' % check_time_schedule(
                    id), keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
            change_action(id, 'Change_time')

        elif 'История разработки' in message.text:
            answer_is_found = True
            stages = history()
            for stage in stages:
                await message.answer(stage, keyboard=standard_keyboard(id))
            change_action(id, 'Start')

    elif check_action(id) == 'Change_time':
        if 'Отмена' in message.text:
            answer_is_found = True
            await message.answer('Мы в главном меню', keyboard=standard_keyboard(id))
            change_action(id, 'Start')
        else:
            answer_is_found = True
            time_trans = message.text.split(':')
            if len(time_trans) == 2:
                time_trans[0] = int(time_trans[0])
                time_trans[1] = int(time_trans[1])
                if 0 <= time_trans[0] < 24:
                    if 0 <= time_trans[1] < 60:
                        change_time_schedule(id, message.text)
                        change_action(id, 'Start')
                        await message.answer(
                            'Теперь после %s я буду присылать расписание на следующий день' % check_time_schedule(
                                id),
                            keyboard=standard_keyboard(id))
                    else:
                        await message.answer('Не могу распознать минуты. Они должен быть в диапазоне [00, 60)',
                                             keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                                  color=KeyboardButtonColor.NEGATIVE))
                else:
                    await message.answer('Не могу распознать час. Он должен быть в диапазоне [00, 24)',
                                         keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                              color=KeyboardButtonColor.NEGATIVE))
            else:
                await message.answer('Проверь правильность ввода. Напоминаю, что формат должен быть ЧЧ:ММ',
                                     keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                          color=KeyboardButtonColor.NEGATIVE))

    elif check_action(id) == 'Change_main_group':
        if message.text in groups:
            answer_is_found = True
            change_main_group(id, message.text)
            change_action(id, 'Start')
            await message.answer(
                'Отлично, %s! Я запомнил, что ты из группы %s. Этот параметр можно будет изменить в настройках. Теперь я буду искать информацию для тебя персонально' % (
                    first_name, message.text), keyboard=standard_keyboard(id))
        else:
            answer_is_found = True
            await message.answer(
                'Не могу отыскать такую группу в своей базе. Проверь, нет ли ошибки. Я брал назваия с официального сайта с расписанием: http://ras.phys.msu.ru')

    elif check_action(id) == 'Delete_group':
        if 'Отмена' in message.text:
            answer_is_found = True
            change_action(id, 'Start')
            await message.answer('Мы в главном меню', keyboard=standard_keyboard(id))
        else:
            answer_is_found = True
            user_groups = check_group(id).split(', ')
            if message.text in user_groups[0]:
                await message.answer(
                    'Ты не можешь удалить группу, которая в моей памяти обозначена как твоя. Если ты указал её неправильно, смени её в настройках. Введи номер группы, которую нужно удалить',
                    keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
            elif message.text not in user_groups:
                await message.answer(
                    'Не могу отыскать такую группу в своей базе. Проверь, нет ли ошибки. Список своих групп ты можешь посмотреть в настройках',
                    keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
            elif message.text in user_groups:
                group_for_delete = message.text
                list_group = ''
                for group in user_groups:
                    if group != group_for_delete:
                        if group != user_groups[0]:
                            list_group += ', ' + group
                        else:
                            list_group += group
                await message.answer('%s' % delete_group(id, list_group))
                await message.answer(settings(id)[0], keyboard=standard_keyboard(id))
                change_action(id, 'Start')

    elif check_action(id) == 'Choose_group_week_schedule':
        if message.text in check_group(id).split(', '):
            answer_is_found = True
            await message.answer('&#10071; Расписание проходило выборочную проверку и может содержать неточности. '
                                 'Если видишь ошибку, пиши в свободной форме и отправляй, а потом зови человека',
                                 keyboard=standard_keyboard(id))
            week_schedule_temp = week_schedule(id, message.text)
            await message.answer(week_schedule_temp, keyboard=standard_keyboard(id))

            del week_schedule_temp
            gc.collect()

            change_action(id, 'Start')
        else:
            answer_is_found = True
            await message.answer('Выбери группу из предложенных', keyboard=group_keyboard(id))

    elif check_action(id) == 'Choose_group':
        if message.text in check_group(id).split(', '):
            answer_is_found = True
            await message.answer('&#10071; Расписание проходило выборочную проверку и может содержать неточности. '
                                 'Если видишь ошибку, пиши в свободной форме и отправляй, а потом зови человека',
                                 keyboard=standard_keyboard(id))
            schedule_temp = schedule(id, message.text)
            await message.answer(schedule_temp, keyboard=standard_keyboard(id))

            del schedule_temp
            gc.collect()

            change_action(id, 'Start')
        else:
            answer_is_found = True
            await message.answer('Выбери группу из предложенных', keyboard=group_keyboard(id))

    elif check_action(id) == 'Not_student':
        if ('Я студент физфака' in message.text) or ('Я студентка физфака' in message.text):
            answer_is_found = True
            await message.answer(
                'Для полноценной работы мне необходимо знать твою группу. Напиши её, пожалуйста. Если ты не студент физического факультета, нажми на кнопку',
                keyboard=Keyboard(one_time=True).add(Text('Я не студент физфака'), color=KeyboardButtonColor.NEGATIVE))
            change_action(id, 'Add_group')

    # elif check_action(id) == 'Quize':
    #     answer_is_found = True
    #     if 'Вернусь позже' in message.text:
    #         change_action(id, 'Start')
    #         await message.answer('Я буду ждать тебя &#129303;', keyboard=standard_keyboard(id))
    #     else:
    #         answer = quize(id, message.text)
    #
    #         if len(answer) == 4:
    #             await message.answer(answer[0])
    #             if len(answer[1]) > 0:
    #                 await message.answer(answer[1])
    #                 await asyncio.sleep(1)
    #             else:
    #                 await asyncio.sleep(2)
    #             await message.answer(answer[2], keyboard=answer[3])
    #
    #         elif len(answer) == 5:
    #             await message.answer(answer[0])
    #             await message.answer(f'Правильный ответ: {answer[1]}')
    #             if len(answer[2]) > 0:
    #                 await message.answer(answer[2])
    #                 await asyncio.sleep(1)
    #             else:
    #                 await asyncio.sleep(2)
    #             await message.answer(answer[3], keyboard=answer[4])
    #
    #         elif len(answer) == 3:
    #             if type(answer[1]) == str:
    #                 await message.answer(answer[0])
    #                 await message.answer(answer[1])
    #                 await message.answer(answer[2], keyboard=standard_keyboard(id))
    #             else:
    #                 await message.answer(answer[0], keyboard=answer[1])
    #
    #         elif len(answer) == 2:
    #             if type(answer[1]) == str:
    #                 await message.answer(answer[0])
    #                 await message.answer(answer[1], keyboard=standard_keyboard(id))
    #             else:
    #                 await message.answer(answer[0], keyboard=answer[1])
    #
    #         else:
    #             await message.answer(answer, keyboard=standard_keyboard(id))
    #             change_action(id, 'Start')

    elif check_headman(id):

        if check_action(id) == 'Headman_mode':
            answer_is_found = True
            group = check_group(id).split(', ')[0]
            if 'Редактировать учебники' in message.text:
                add_group_for_books(group)
                dictionary = check_books(group)
                for num in range(len(dictionary['Title'])):
                    await message.answer('%d. %s' % (num + 1, dictionary['Title'][num]),
                                         attachment=dictionary['Link'][num])
                await message.answer('Мы в меню редактирования учебников', keyboard=headman_keyboard('Учебник'))
                change_action(id, 'Books_editing')

            elif 'Редактировать ДЗ' in message.text:
                if check_group_homework(group) is None:
                    add_group_for_homework(group)
                if check_subject(group) is None:
                    await message.answer(
                        'Пока предметы не добавлены. Введи название первого предмета',
                        keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
                    change_action(id, 'Subjects_editing_add')
                else:
                    subjects = check_subject(group)
                    await message.answer(
                        'Выбери предмет для редактирования домашних заданий',
                        keyboard=subjects_keyboard(subjects, id, True))
                    change_action(id, 'Subjects_editing')

            elif 'Вернуться в главное меню' in message.text:
                change_action(id, 'Start')
                await message.answer('Starosta_Mode: OFF', keyboard=standard_keyboard(id))

            else:
                await message.answer('Что мне с этим делать? &#128563;', keyboard=headman_keyboard())

        elif 'Subjects' in check_action(id):
            answer_is_found = True
            group = check_group(id).split(', ')[0]
            if 'editing' in check_action(id):
                if 'add' in check_action(id):
                    if 'Отмена' in message.text:
                        change_action(id, 'Headman_mode')
                        await message.answer('Мы в главном меню старосты', keyboard=headman_keyboard())
                    else:
                        if len(message.text) < 40:
                            add_subject(group, message.text)
                            await message.answer('Добавлен новый предмет:\n\n%s' % message.text)
                            subjects = check_subject(group)
                            await message.answer(
                                'Выбери предмет для редактирования домашних заданий',
                                keyboard=subjects_keyboard(subjects, id, True))
                            change_action(id, 'Subjects_editing')

                        else:
                            await message.answer(
                                'Введено:\n\n%s\n\nДлина:   %d символов' % (message.text, len(message.text)))
                            await message.answer(
                                'Название предмета не может быть больше 40 символов, однако мы рекомендуем использовать не больше 15 для корректоного отображения. Введите другое название',
                                keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                     color=KeyboardButtonColor.NEGATIVE))

                elif 'delete' in check_action(id):
                    if 'Отмена' in message.text:
                        change_action(id, 'Headman_mode')
                        subjects = check_subject(group)
                        await message.answer(
                            'Выбери предмет для редактирования домашних заданий',
                            keyboard=subjects_keyboard(subjects, id, True))
                        change_action(id, 'Subjects_editing')

                    elif check_subject(group) is None:
                        await message.answer('Список предметов пуст', keyboard=headman_keyboard())

                    else:
                        subjects = check_subject(group)
                        if int(message.text) <= len(subjects):
                            await message.answer('Удалён предмет:\n\n%s' % subjects[int(message.text) - 1],
                                                 keyboard=headman_keyboard())
                            delete_subject(group, subjects[int(message.text) - 1])
                        else:
                            await message.answer('Не могу найти такой предмет', keyboard=headman_keyboard())

                        subjects = check_subject(group)
                        await message.answer('Возвращаюсь к списку предметов',
                                             keyboard=subjects_keyboard(subjects, id, True))
                        change_action(id, 'Subjects_editing')

                else:
                    subjects = check_subject(group)

                    if 'Удалить предмет' in message.text:
                        for subject in range(len(subjects)):
                            await message.answer('%d. %s' % (subject + 1, subjects[subject]))
                        await message.answer(
                            'Выберите номер предмета, который нужно удалить.\n\nОсторожно! Все домашние задания по этому предмету удалятся. Отменить действие невозможно.',
                            keyboard=custom_keyboard(range(1, len(subjects) + 1)))
                        change_action(id, 'Subjects_editing_delete')

                    elif 'Добавить предмет' in message.text:
                        await message.answer(
                            'Введи название нового предмета',
                            keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
                        change_action(id, 'Subjects_editing_add')

                    elif 'Вернуться в меню старосты' in message.text:
                        change_action(id, 'Headman_mode')
                        await message.answer('Мы в меню старосты', keyboard=headman_keyboard())

                    elif message.text in subjects:
                        add_editing_subject(group, message.text)
                        await message.answer('Для редактирования выбран предмет:    %s' % message.text)
                        homework = check_homework(group)[message.text]
                        for number in range(len(homework['Homeworks'])):
                            task = homework['Homeworks'][number]
                            attach = homework['Attachments'][number]
                            await message.answer('%d. %s' % (number + 1, task), attachment=attach)
                        await message.answer('Выбери действие:', keyboard=headman_keyboard('ДЗ'))
                        add_editing_subject(group, message.text)
                        change_action(id, 'Change_homework')

                    else:
                        await message.answer('Что мне с этим делать? &#128563;',
                                             keyboard=subjects_keyboard(subjects, id, True))

        elif 'Change_homework' in check_action(id):
            answer_is_found = True
            group = check_group(id).split(', ')[0]
            if 'add' in check_action(id):
                if 'Отмена' in message.text:
                    change_action(id, 'Subjects_editing')
                    subjects = check_subject(group)
                    await message.answer('Выбери предмет', keyboard=subjects_keyboard(subjects, id, True))
                else:
                    attach = parse_attachments(id)
                    date = message.date
                    editing_subject = check_editing_subject(group)
                    add_homework(group, message.text, attach, date, editing_subject)
                    homework = check_homework(group)[editing_subject]
                    await message.answer('Добавлено:\n\n%s' % message.text, attachment=attach)

                    for number in range(len(homework['Homeworks'])):
                        task = homework['Homeworks'][number]
                        attach = homework['Attachments'][number]
                        await message.answer('%d. %s' % (number + 1, task), attachment=attach)

                    await message.answer('Выбери действие:', keyboard=headman_keyboard('ДЗ'))
                    change_action(id, 'Change_homework')

            elif 'delete' in check_action(id):
                if 'Отмена' in message.text:
                    change_action(id, 'Headman_mode')
                    await message.answer('Мы в главном меню старосты', keyboard=headman_keyboard())
                else:
                    subject = check_editing_subject(group)
                    answer = delete_homework(group, int(message.text) - 1, subject)
                    await message.answer('Удалено:\n\n%s' % answer)

                    homework = check_homework(group)[subject]
                    for number in range(len(homework['Homeworks'])):
                        task = homework['Homeworks'][number]
                        attach = homework['Attachments'][number]
                        await message.answer('%d. %s' % (number + 1, task), attachment=attach)

                    await message.answer('Выбери действие:', keyboard=headman_keyboard('ДЗ'))
                    change_action(id, 'Change_homework')

            elif 'Добавить ДЗ' in message.text:
                await message.answer('Введи домашнее задание, которое хочешь добавить',
                                     keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                          color=KeyboardButtonColor.NEGATIVE))
                change_action(id, 'Change_homework_add')
            elif 'Удалить ДЗ' in message.text:

                subject = check_editing_subject(group)
                homeworks = check_homework(group)[subject]
                if 'Домашнее задание не добавлено' in homeworks['Homeworks']:
                    await message.answer('У тебя нет домашних заданий по этому предмету')
                    await message.answer('Возвращаюсь к редактированию ДЗ', keyboard=headman_keyboard('ДЗ'))
                    change_action(id, 'Change_homework')
                else:
                    await message.answer('Выбери номер домашнего задания, которое нужно удалить',
                                         keyboard=custom_keyboard(range(1, len(homeworks['Homeworks']) + 1)))
                    change_action(id, 'Change_homework_delete')
            elif 'Вернуться к списку предметов' in message.text:
                change_action(id, 'Subjects_editing')
                subjects = check_subject(group)
                await message.answer('Выбери предмет', keyboard=subjects_keyboard(subjects, id, True))
            else:
                await message.answer('Что мне с этим делать? &#128563;', keyboard=headman_keyboard('ДЗ'))

        elif 'Books_editing' in check_action(id):
            answer_is_found = True
            if 'add' in check_action(id):
                if 'Отмена' in message.text:
                    change_action(id, 'Headman_mode')
                    await message.answer('Мы в меню редактирования учебников', keyboard=headman_keyboard('Учебник'))
                else:
                    group = check_group(id).split(', ')[0]
                    dictionary = check_books(group)

                    link = parse_attachments(id)
                    date = message.date

                    if link in dictionary['Link']:
                        await message.answer('Этот учебник уже добавлен', keyboard=headman_keyboard())
                    else:
                        add_books(group, message.text, link, date)
                        await message.answer('Добавлено:\n\n%s' % message.text, attachment=link,
                                             keyboard=headman_keyboard())

                    dictionary = check_books(group)
                    for num in range(len(dictionary['Title'])):
                        await message.answer('%d. %s' % (num + 1, dictionary['Title'][num]),
                                             attachment=dictionary['Link'][num])
                    await message.answer('Возвращаюсь в меню редактирования учебников',
                                         keyboard=headman_keyboard('Учебник'))
                change_action(id, 'Books_editing')


            elif 'delete' in check_action(id):
                group = check_group(id).split(', ')[0]
                dictionary = check_books(group)
                try:
                    if 'Отмена' in message.text:
                        change_action(id, 'Books_editing')
                        await message.answer('Мы в меню редактирования учебников', keyboard=headman_keyboard('Учебник'))
                    elif (int(message.text) - 1) > len(dictionary['Title']):
                        await message.answer('Указан неправильный номер. Возвращаюсь в меню редактирования учебников',
                                             keyboard=headman_keyboard('Учебник'))
                        change_action(id, 'Books_editing')
                    else:
                        index = int(message.text) - 1
                        if 'Отмена' in message.text:
                            change_action(id, 'Headman_mode')
                            await message.answer('Мы в главном меню старосты', keyboard=headman_keyboard())
                        else:
                            await message.answer('Удалено:\n\n%s' % dictionary['Title'][index],
                                                 attachment=dictionary['Link'][index],
                                                 keyboard=headman_keyboard())
                            delete_books(group, int(message.text) - 1)

                            dictionary = check_books(group)
                            for num in range(len(dictionary['Title'])):
                                await message.answer('%d. %s' % (num + 1, dictionary['Title'][num]),
                                                     attachment=dictionary['Link'][num])
                            await message.answer('Возвращаюсь к редактированию учебников',
                                                 keyboard=headman_keyboard('Учебник'))
                            change_action(id, 'Books_editing')
                except:
                    await message.answer('Не совсем понимаю, что ты хочешь', keyboard=headman_keyboard('Учебник'))
                    change_action(id, 'Books_editing')

            else:
                if 'Добавить учебник' in message.text:
                    change_action(id, 'Books_editing_add')
                    await message.answer('Прикрепи файл к сообщению. Переименовывай файл так, чтобы его название легко '
                                         'читалось. Ты можешь написать сообщение, которое будет отправляться каждому '
                                         'студенту из группы. Рекомендую прикреплять к сообщению по одному файлу',
                                         keyboard=Keyboard(one_time=True)
                                         .add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
                elif 'Удалить учебник' in message.text:
                    group = check_group(id).split(', ')[0]
                    dictionary = check_books(group)
                    change_action(id, 'Books_editing_delete')
                    await message.answer('Выбери номер учебника, который нужно удалить',
                                         keyboard=custom_keyboard(range(1, len(dictionary['Title']) + 1)))

                elif 'Вернуться в меню старосты' in message.text:
                    change_action(id, 'Headman_mode')
                    await message.answer('Мы в главном меню старосты', keyboard=headman_keyboard())

                else:
                    await message.answer('Что мне с этим делать? &#128563;', keyboard=headman_keyboard('Учебник'))

    if check_action(id) != 'Not_student':
        if ('пасиб' in message.text.lower() or 'благодар' in message.text.lower()) and len(message.text) < 100:
            await message.answer('Рады помочь &#128521;', keyboard=standard_keyboard(id))
            change_action(id, 'Start')

        elif 'Нужен человек' in message.text:
            api = API(token=token)
            await api.messages.send(peer_id=2000000001, random_id=0, message=f'Пользователь {last_name} '
                                                                             f'{first_name} ждёт ответа')
            await message.answer(f'{first_name}, твоё обращение зарегистрировано. Как только появится возможность, '
                                 f'тебе сразу ответят. А пока можешь продолжать пользоваться Валерой &#128521;',
                                 keyboard=standard_keyboard(id))

        elif (len(message.text) < 100) and (answer_is_found is False):
            if (check_last_connection(id) - datetime.datetime.now()).total_seconds() < 1:
                if check_action(id) != 'Not_student' or check_group(id) is not None:
                    await message.answer('Не совсем тебя понял. Тебе нужна моя помощь?',
                                         keyboard=Keyboard(one_time=True)
                                         .add(Text('Валера!'), color=KeyboardButtonColor.POSITIVE).row() \
                                         .add(Text('Нужен человек'), color=KeyboardButtonColor.PRIMARY))
                    change_action(id, 'Start')

    if len(message.text) > 500:
        api = API(token=token)
        await api.messages.send(peer_id=2000000001, random_id=0, message=f'Сообщение от пользователя: {last_name} '
                                                                         f'{first_name}\n\n{message.text}')


bot.run_forever()
