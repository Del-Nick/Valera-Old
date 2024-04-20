import asyncio
from vkbottle import API
from vkbottle.bot import Bot, Message
from vkbottle import GroupEventType, GroupTypes, Keyboard, Text, KeyboardButtonColor
from Database import *
from Arrays import groups, workshop_rooms
from Functions import *
from History_of_development import history
from config import token
from loguru import logger
import sys
import requests
import re
import gc
import datetime

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="DEBUG")

bot = Bot(token=token)

checking()

@bot.on.private_message()
async def message_handler(message: Message):

    user = await bot.api.users.get(message.from_id)
    id = user[0].id
    first_name = user[0].first_name
    last_name = user[0].last_name

    num_of_conn(id)

    if not check_id(id):
        add_new_user(id, first_name, last_name)
        await message.answer(
            'Привет, %s! Меня зовут Валера, я твой чат-бот. Если вдруг ты запутался и не знаешь выход, просто позови меня по имени, и я тебя вытащу.' % user[0].first_name)
        await message.answer(
                'Давай немного познакомимся.Для полноценной работы мне необходимо знать твою группу. Напиши её, пожалуйста. '
                'Если ты не студент физического факультета, нажми на кнопку.',
                 keyboard=Keyboard(one_time=True).add(Text('Я не студент физфака')))

    elif check_action(id) == 'Add_group':
        if message.text == 'Отмена':
            change_action(id, 'Start')
            await message.answer('Мы в главном меню', keyboard=standard_keyboard(id))
        else:
            if message.text in groups:
                if check_group(id) is None:
                    change_action(id, 'Start')
                    add_group(id, message.text)
                    await message.answer(
                        'Отлично, %s! Я запомнил, что ты из группы %s. Этот параметр можно будет изменить в настройках. Теперь я буду искать информацию для тебя персонально' % (
                        first_name, message.text), keyboard=standard_keyboard(id))
                else:
                    add_group(id, message.text)
                    await message.answer('Отлично, %s! Я добавил в список твоих групп %s. Этот параметр можно будет изменить в настройках. Теперь ты сможешь выбирать, для какой группы смотреть информацию' % (
                            first_name, message.text), keyboard=standard_keyboard(id))
                change_action(id, 'Start')

            elif message.text == 'Я не студент физфака':
                change_action(id, 'Not_student')
                await message.answer(
                    "Хорошо, %s. Я запомнил, что ты не с физического факультета. Пожалуйста, продублируй сообщение, чтобы мы его не пропустили.\n\nP.s. Если кнопка была нажата по ошибке, ты всегда можешь написать 'Я студент физфака' или 'Я студентка физфака', чтобы зарегистрироваться." % user[0].first_name)
            else:
                await message.answer(
                    "Не могу найти такую группу. Я брал все названия отсюда: http://ras.phys.msu.ru . Проверь правильность ввода и попробуй ещё раз")

    elif ('Валера' in message.text) or ('Валерий' in message.text):
        change_action(id, 'Start')
        await message.answer('Любовь, надежда и вера-а-а', keyboard=standard_keyboard(id))

    if check_action(id) == 'Start':
        if 'расписание' in word_normalized(message.text):
            if len(check_group(id).split(', ')) > 1:
                await message.answer('Выбери номер группы', keyboard=group_keyboard(id))
                if 'недел' in word_normalized(message.text):
                    change_action(id, 'Choose_group_week_schedule')
                else:
                    change_action(id, 'Choose_group')
            else:
                if 'недел' in word_normalized(message.text):
                    await message.answer(week_schedule(id, check_group(id)), keyboard=standard_keyboard(id))
                else:
                    await message.answer(schedule(id, check_group(id)), keyboard=standard_keyboard(id))

        elif 'Настройки' in message.text:
            change_action(id, 'Settings')
            await message.answer(settings(id)[0], keyboard=settings(id)[1])

        elif 'Cтароста Mode' in message.text:
            change_action(id, 'Headman_mode')
            await message.answer('Starosta_mode: ON', keyboard=headman_keyboard())

        elif 'Учебник' in message.text:
            group = check_group(id).split(', ')[0]
            print('check_books(group)', check_books(group))
            if (check_books(group) is None) or (check_books(group) == 'Error'):
                await message.answer('Староста ещё не добавил учебники. Возвращаюсь в главное меню',
                                     keyboard=standard_keyboard(id))
            else:
                answer = check_books(group)['Books']
                for num in range(len(answer['Title'])):
                    await message.answer('%d. %s' % (num+1, answer['Title'][num]), attachment=answer['Link'][num])
                await message.answer('Возвращаюсь в главное меню', keyboard=standard_keyboard(id))

        elif 'ДЗ' in message.text:
            group = check_group(id).split(', ')[0]
            if check_subject(group) is None:
                await message.answer('Предметы ещё не добавлены. Обратись к своему старосте. Если возникают проблемы, напиши в сообщения группы',
                                     keyboard=standard_keyboard(id))
                change_action(id, 'Start')
            else:
                subjects = check_subject(group)
                await message.answer('Выбери предмет', keyboard=subjects_keyboard(subjects, id, False))
                change_action(id, 'Homework')

        elif 'Практикум' in message.text:
            group = check_group(id).split(', ')[0]
            first_sem = ['127', '126', '125', '124', '123', '122', '121', '120', '119', '118', '117. Рекомендации', '117', '116', '114',
             '112', '110', '108', '106', '105', '104', '103', '102', '101']
            second_sem = ['240б', '240', '238', '234', '233', '232', '230',
             '228', '227', '226', '219m', '219', '218', '210', '208', '207', '206', '205', '204', '202', '201']
            third_sem = ['340', '339', '338', '337', '336', '325', '324', '323', '322', '319', '309',
             '308М', '308', '307', '305А', '305', '304', '302', '301']
            forth_sem = ['419', '413', '412', '411', '410', '409', '408', '403', '401', '169', '152', '147', '142', '140', '136',
             '135', '132А', '132', '128']


            answer = workshop(id, group)
            await message.answer('%s' % answer)

            if group[0] == '1':

                if datetime.datetime.today().month > 8:
                    await message.answer('Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                                         keyboard=custom_keyboard(list(reversed(first_sem))))
                else:
                    await message.answer(
                        'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                        keyboard=custom_keyboard(list(reversed(second_sem))))
            elif group[0] == '2':
                if datetime.datetime.today().month > 8:
                    await message.answer('Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                                         keyboard=custom_keyboard(list(reversed(third_sem))))
                else:
                    await message.answer(
                        'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                        keyboard=custom_keyboard(list(reversed(forth_sem))))
            else:
                await message.answer('Введи номер общего физического практикума, и я пришлю тебе методичку',
                                     keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
            change_action(id, 'Workshop')
            # await message.answer('%s' % answer, keyboard=standard_keyboard(id))

    elif check_action(id) == 'Homework':
        group = check_group(id).split(', ')[0]
        subjects = check_subject(group)

        if 'Вернуться в главное меню' in message.text:
            change_action(id, 'Start')
            await message.answer('Возвращаюсь в главное меню', keyboard=standard_keyboard(id))

        elif subjects is None:
            await message.answer(
                'Предметы ещё не добавлены. Обратись к своему старосте. Если возникают проблемы, напиши в сообщения группы',
                keyboard=standard_keyboard(id))
            change_action(id, 'Start')

        elif message.text in subjects:
            homeworks = check_homework(group)[message.text]
            for num in range(len(homeworks['Homeworks'])):
                homework = homeworks['Homeworks'][num]
                attach = homeworks['Attachments'][num]
                await message.answer('%d. %s' % (num+1, homework), attachment=attach)
            await message.answer('Возвращаюсь к списку предметов', keyboard=subjects_keyboard(subjects, id, False))
            change_action(id, 'Homework')

        else:
            await message.answer('Не могу найти такой предмет. Для твоего удобства я сделал клавиатуру', keyboard=subjects_keyboard(subjects, id, False))

    elif check_action(id) == 'Workshop':
        if 'Отмена' in message.text:
            await message.answer('Возвращаюсь в главное меню', keyboard=standard_keyboard(id))
        else:
            link = collect_books(message.text)
            if 'doc' in link:
                await message.answer('Кабинет: %s. Держи' % search_workshop_room(message.text),
                                     attachment='%s' % collect_books(message.text), keyboard=standard_keyboard(id))
            else:
                await message.answer('Не знаю, что со мной сегодня. Не могу найти методичку..', keyboard=standard_keyboard(id))
        change_action(id, 'Start')

    elif check_action(id) == "Settings":
        if 'Сменить группу' in message.text:
            if check_headman(id) and not check_admin(id):
                await message.answer('Староста не может менять группу. Староста, как капитан: покидает корабль последним', keyboard=standard_keyboard(id))
                change_action(id, 'Start')
            else:
                delete_all_groups(id)
                change_action(id, 'Change_main_group')
                await message.answer('Введи новый номер твоей группы, которая будет считаться основной')

        elif 'Добавить группу' in message.text:
            if len(check_group(id).split(', ')) < 3:
                change_action(id, 'Add_group')
                await message.answer('Введи номер группы, которую ты хочешь добавить',
                                     keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
            else:
                await message.answer(
                    'Ты не можешь добавить больше 3 групп. Чтобы добавить новую, удали одну из старых в настройках',
                    keyboard=standard_keyboard(id))
                change_action(id, 'Start')

        elif 'Удалить группу' in message.text:
            change_action(id, 'Delete_group')
            await message.answer('Введи номер группы, которую ты хочешь удалить',
                                 keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))

        elif 'Вернуться в главное меню' in message.text:
            change_action(id, 'Start')
            await message.answer('Мы в главном меню', keyboard=standard_keyboard(id))

        elif 'Время перехода на новый день' in message.text:
            await message.answer(
                'После %s я присылаю тебе расписание на следующий день. Чтобы изменить этот параметр, введи время в том же формате:' % check_time_schedule(
                    id), keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
            change_action(id, 'Change_time')

        elif 'История разработки' in message.text:
            await message.answer('%s' % history(), keyboard=standard_keyboard(id))
            change_action(id, 'Start')

    elif check_action(id) == 'Change_time':
        if 'Отмена' in message.text:
            await message.answer('Мы в главном меню', keyboard=standard_keyboard(id))
            change_action(id, 'Start')
        else:
            time = message.text.split(':')
            if len(time) == 2:
                time[0] = int(time[0])
                time[1] = int(time[1])
                if 0 <= time[0] < 24:
                    if 0 <= time[1] < 60:
                        change_time_schedule(id, message.text)
                        change_action(id, 'Start')
                        await message.answer(
                            'Теперь после %s я буду присылать расписание на следующий день' % check_time_schedule(
                                id),
                            keyboard=standard_keyboard(id))
                    else:
                        await message.answer('Не могу распознать минуты. Они должен быть в диапазоне [00, 60)',
                                             keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
                else:
                    await message.answer('Не могу распознать час. Он должен быть в диапазоне [00, 24)',
                                         keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
            else:
                await message.answer('Проверь правильность ввода. Напоминаю, что формат должен быть ЧЧ:ММ',
                                     keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))

    elif check_action(id) == 'Change_main_group':
        if message.text in groups:
            change_main_group(id, message.text)
            change_action(id, 'Start')
            await message.answer(
                'Отлично, %s! Я запомнил, что ты из группы %s. Этот параметр можно будет изменить в настройках. Теперь я буду искать информацию для тебя персонально' % (
                    first_name, message.text), keyboard=standard_keyboard(id))
        else:
            await message.answer(
                'Не могу отыскать такую группу в своей базе. Проверь, нет ли ошибки. Я брал назваия с официального сайта с расписанием: http://ras.phys.msu.ru')

    elif check_action(id) == 'Delete_group':
        if 'Отмена' in message.text:
            change_action(id, 'Start')
            await message.answer('Мы в главном меню', keyboard=standard_keyboard(id))
        else:
            user_groups = check_group(id).split(', ')
            if message.text in user_groups[0]:
                await message.answer(
                    'Ты не можешь удалить группу, которая в моей памяти обозначена как твоя. Если ты указал её неправильно, смени её в настройках. Введи номер группы, которую нужно удалить', keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
            elif message.text not in user_groups:
                await message.answer(
                    'Не могу отыскать такую группу в своей базе. Проверь, нет ли ошибки. Список своих групп ты можешь посмотреть в настройках', keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
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
            await message.answer(week_schedule(id, message.text), keyboard=standard_keyboard(id))
            change_action(id, 'Start')
        else:
            await message.answer('Выбери группу из предложенных', keyboard=group_keyboard(id))

    elif check_action(id) == 'Choose_group':

        if message.text in check_group(id).split(', '):
            await message.answer(schedule(id, message.text), keyboard=standard_keyboard(id))
            change_action(id, 'Start')
        else:
            await message.answer('Выбери группу из предложенных', keyboard=group_keyboard(id))

    elif check_action(id) == 'Not_student':
        if ('Я студент физфака' in message.text) or ('Я студентка физфака' in message.text):
            await message.answer(
                'Для полноценной работы мне необходимо знать твою группу. Напиши её, пожалуйста. Если ты не студент физического факультета, нажми на кнопку',
                keyboard=Keyboard(one_time=True).add(Text('Я не студент физфака'), color=KeyboardButtonColor.NEGATIVE))
            change_action(id, 'Add_group')

    elif check_headman(id):
        if check_action(id) == 'Headman_mode':
            group = check_group(id).split(', ')[0]
            if 'Редактировать учебники' in message.text:
                add_group_for_books(group)
                dictionary = check_books(group)['Books']
                for num in range(len(dictionary['Title'])):
                    await message.answer('%d. %s' % (num+1, dictionary['Title'][num]), attachment=dictionary['Link'][num])
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

        elif 'Subjects' in check_action(id):
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
                            await message.answer('Удалён предмет:\n\n%s' % subjects[int(message.text)-1], keyboard=headman_keyboard())
                            delete_subject(group, subjects[int(message.text)-1])
                        else:
                            await message.answer('Не могу найти такой предмет', keyboard=headman_keyboard())

                        subjects = check_subject(group)
                        await message.answer('Возвращаюсь к списку предметов', keyboard=subjects_keyboard(subjects, id, True))
                        change_action(id, 'Subjects_editing')

                else:
                    subjects = check_subject(group)

                    if 'Удалить предмет' in message.text:
                        for subject in range(len(subjects)):
                            await message.answer('%d. %s' % (subject+1, subjects[subject]))
                        await message.answer(
                            'Выберите номер предмета, который нужно удалить.\n\nОсторожно! Все домашние задания по этому предмету удалятся. Отменить действие невозможно.',
                            keyboard = custom_keyboard(range(1, len(subjects)+1)))
                        change_action(id, 'Subjects_editing_delete')

                    elif 'Добавить предмет' in message.text:
                        await message.answer(
                            'Введи название нового предмета',
                            keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
                        change_action(id, 'Subjects_editing_add')

                    elif 'Вернуться в меню старосты' in message.text:
                        change_action(id, 'Headman_mode')
                        await message.answer('Мы в меню старосты', keyboard=headman_keyboard())

                    # elif 'add' in check_action_answer:


                    elif message.text in subjects:
                        add_editing_subject(group, message.text)
                        await message.answer('Для редактирования выбран предмет:    %s' % message.text)
                        homework = check_homework(group)[message.text]
                        for number in range(len(homework['Homeworks'])):
                            task = homework['Homeworks'][number]
                            attach = homework['Attachments'][number]
                            await message.answer('%d. %s' % (number+1, task), attachment=attach)
                        await message.answer('Выбери действие:', keyboard=headman_keyboard('ДЗ'))
                        add_editing_subject(group, message.text)
                        change_action(id, 'Change_homework')

                    else:
                        await message.answer('Произошла какая-то ошибка. Возвращаюсь в меню старосты', keyboard=headman_keyboard())
                        change_action(id, 'Headman_mode')

        elif 'Change_homework' in check_action(id):
            group = check_group(id).split(', ')[0]
            if 'add' in check_action(id):
                if 'Отмена' in message.text:
                    change_action(id, 'Subjects_editing')
                    subjects = check_subject(group)
                    await message.answer('Выбери предмет', keyboard=subjects_keyboard(subjects, id, True))
                else:
                    attach = parse_attachments(id)
                    editing_subject = check_editing_subject(group)
                    add_homework(group, message.text, attach, editing_subject)
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
                    answer = delete_homework(group, int(message.text)-1, subject)
                    await message.answer('Удалено:\n\n%s' % answer)

                    homework = check_homework(group)[subject]
                    for number in range(len(homework['Homeworks'])):
                        task = homework['Homeworks'][number]
                        attach = homework['Attachments'][number]
                        await message.answer('%d. %s' % (number + 1, task), attachment=attach)

                    await message.answer('Выбери действие:', keyboard=headman_keyboard('ДЗ'))
                    change_action(id, 'Change_homework')

            elif 'Добавить ДЗ' in message.text:
                await message.answer('Введи домашнее задание, которое хочешь добавить', keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
                change_action(id, 'Change_homework_add')
            elif 'Удалить ДЗ' in message.text:

                subject = check_editing_subject(group)
                homeworks = check_homework(group)[subject]
                if 'Домашнее задание не добавлено' in homeworks['Homeworks']:
                    await message.answer('У тебя нет домашних заданий по этому предмету')
                    await message.answer('Возвращаюсь к редактированию ДЗ', keyboard=headman_keyboard('ДЗ'))
                    change_action(id, 'Change_homework')
                else:
                    await message.answer('Выбери номер домашнего задания, которое нужно удалить', keyboard=custom_keyboard(range(1, len(homeworks['Homeworks'])+1)))
                    change_action(id, 'Change_homework_delete')
            elif 'Вернуться к списку предметов' in message.text:
                change_action(id, 'Subjects_editing')
                subjects = check_subject(group)
                await message.answer('Выбери предмет', keyboard=subjects_keyboard(subjects, id, True))

        elif 'Books_editing' in check_action(id):
            if 'add' in check_action(id):
                if 'Отмена' in message.text:
                    change_action(id, 'Headman_mode')
                    await message.answer('Мы в меню редактирования учебников', keyboard=headman_keyboard('Учебник'))
                else:
                    group = check_group(id).split(', ')[0]
                    dictionary = check_books(group)['Books']

                    link = parse_attachments(id)

                    if link in dictionary['Link']:
                        await message.answer('Этот учебник уже добавлен', keyboard=headman_keyboard())
                    else:
                        add_books(group, message.text, link)
                        await message.answer('Добавлено:\n\n%s' % message.text, attachment=link, keyboard=headman_keyboard())

                    dictionary = check_books(group)['Books']
                    for num in range(len(dictionary['Title'])):
                        await message.answer('%d. %s' % (num+1, dictionary['Title'][num]), attachment=dictionary['Link'][num])
                    await message.answer('Возвращаюсь в меню редактирования учебников', keyboard=headman_keyboard('Учебник'))
                change_action(id, 'Books_editing')


            elif 'delete' in check_action(id):
                group = check_group(id).split(', ')[0]
                dictionary = check_books(group)['Books']
                try:
                    if 'Отмена' in message.text:
                        change_action(id, 'Books_editing')
                        await message.answer('Мы в меню редактирования учебников', keyboard=headman_keyboard('Учебник'))
                    elif (int(message.text)-1) > len(dictionary['Title']):
                        await message.answer('Указан неправильный номер. Возвращаюсь в меню редактирования учебников',
                                             keyboard=headman_keyboard('Учебник'))
                        change_action(id, 'Books_editing')
                    else:
                        index = int(message.text)-1
                        if 'Отмена' in message.text:
                            change_action(id, 'Headman_mode')
                            await message.answer('Мы в главном меню старосты', keyboard=headman_keyboard())
                        else:
                            await message.answer('Удалено:\n\n%s' % dictionary['Title'][index],
                                                 attachment=dictionary['Link'][index],
                                                 keyboard=headman_keyboard())
                            delete_books(group, int(message.text)-1)

                            dictionary = check_books(group)['Books']
                            for num in range(len(dictionary['Title'])):
                                await message.answer('%d. %s' % (num+1, dictionary['Title'][num]), attachment=dictionary['Link'][num])
                            await message.answer('Возвращаюсь к редактированию учебников', keyboard=headman_keyboard('Учебник'))
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
                    dictionary = check_books(group)['Books']
                    change_action(id, 'Books_editing_delete')
                    await message.answer('Выбери номер учебника, который нужно удалить',
                                         keyboard=custom_keyboard(range(1, len(dictionary['Title'])+1)))


                elif 'Вернуться в меню старосты' in message.text:
                    change_action(id, 'Headman_mode')
                    await message.answer('Мы в главном меню старосты', keyboard=headman_keyboard())


    if len(message.text) > 100:
        api = API(token=token)
        await api.messages.send(peer_id=2000000001, random_id=0, message=f'Сообщение от пользователя: {last_name} {first_name}\n\n{message.text}')

bot.run_forever()

