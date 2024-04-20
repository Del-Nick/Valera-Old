from Database_KKO import *
from Database import *
from vkbottle import Keyboard, KeyboardButtonColor, Text
from Arrays import groups
from Functions import standard_keyboard

subject_1 = ['Механика',
             'Иностранный язык',
             'Ан. геометрия',
             'Матанализ',
             'Программирование',
             'Практикум',
             'ВТЭК',
             'Физ. культура',
             'ОБРЕЗ']

subject_2 = ['Электромагнетизм',
             'Матанализ',
             'ТФКП',
             'Ядерная физика',
             'Иностранный язык',
             'Ядерный практикум',
             'Практикум',
             'Программирование',
             'Физ. культура']

subject_3 = ['Иностранный язык',
             'Атомная физика',
             'ММФ',
             'Теор. механика',
             'Электродинамика',
             'Радиофизика',
             'НИС',
             'Атомный практикум',
             'Радио практикум',
             'Астрономия']

subject_4 = ['Мат. статистика',
             'Термодинамика',
             'Квантовая теория',
             'Инженерная физика',
             'Теория волн',
             'Теория колебаний']

subject_5 = []

subject_6 = []

quest_five_points = [5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18]
quest_ten_points = [20, 21]
quest_percents = [4, 12]
quest_yes_no = [9, 17]


def buttons(type, num=0, workshop=False, inline=False,  studsovet: bool = False):
    if inline:
        keyboard = Keyboard(inline=True)
    else:
        keyboard = Keyboard(one_time=True)

    if type == 5:
        names = [1, 2, 3, 4, 5]
        keyboard.add(Text(names[0]), color=KeyboardButtonColor.NEGATIVE)
        for button in names[1:-1]:
            keyboard.add(Text(button), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Text(names[-1]), color=KeyboardButtonColor.POSITIVE)
        keyboard.row().add(Text('Затрудняюсь'), color=KeyboardButtonColor.SECONDARY)

    elif type == 10:
        names = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        keyboard.add(Text(names[0]), color=KeyboardButtonColor.NEGATIVE)
        for button in names[1:5]:
            keyboard.add(Text(button), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        for button in names[5:9]:
            keyboard.add(Text(button), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Text(names[-1]), color=KeyboardButtonColor.POSITIVE)

    elif type == '%':
        if num < 10:
            names = ['75-100%', '50-75%', '25-50%', '0-25%', 'Не было лекций']
        else:
            if workshop:
                names = ['75-100%', '50-75%', '25-50%', '0-25%']
            else:
                names = ['75-100%', '50-75%', '25-50%', '0-25%', 'Не было семинаров']
        keyboard.add(Text(names[0]), color=KeyboardButtonColor.NEGATIVE)
        for button in names[1:-2]:
            keyboard.add(Text(button), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Text(names[-2]), color=KeyboardButtonColor.POSITIVE)
        keyboard.row().add(Text(names[-1]), color=KeyboardButtonColor.SECONDARY)

    elif type == 'yes':
        keyboard.add(Text('Да'), color=KeyboardButtonColor.POSITIVE)
        keyboard.add(Text('Нет'), color=KeyboardButtonColor.NEGATIVE)

    if studsovet:
        try:
            keyboard.row().add(Text('Сброс'), color=KeyboardButtonColor.SECONDARY)
        except:
            keyboard.add(Text('Сброс'), color=KeyboardButtonColor.SECONDARY)

    return keyboard


def subjects_for_keyboard(id):
    try:
        print(all_data_kko(id))
        course = int(all_data_kko(id)[3])  # Клавиатура со списком Сбов
        if course == 1:
            names = subject_1
        elif course == 2:
            names = subject_2
        elif course == 3:
            names = subject_3
        elif course == 4:
            names = subject_4
        elif course == 5:
            names = subject_5
        elif course == 6:
            names = subject_6

        keyboard = Keyboard(one_time=True)
        if len(names) % 2 == 0:
            for i in range(0, len(names[:-2]), 2):
                keyboard.add(Text(names[i])).add(Text(names[i + 1])).row()
            keyboard.add(Text(names[-2])).add(Text(names[-1]))
        else:
            for i in range(0, len(names[:-1]), 2):
                keyboard.add(Text(names[i])).add(Text(names[i + 1])).row()
            keyboard.add(Text(names[-1]))

        if check_studsovet(id):
            try:
                keyboard.row().add(Text('Сброс'), color=KeyboardButtonColor.SECONDARY)
            except:
                keyboard.add(Text('Сброс'), color=KeyboardButtonColor.SECONDARY)

        return keyboard
    except:
        return None


def progressbar(num, total):
    return f'|{"█" * int(num / total * 8)}{"╍" * (8 - int(num / total * 8))}|ㅤ  ㅤ{num / total * 100:.2f}%ㅤ  ㅤ' \
           f'{num + 1}/{total}\n\n'


def keyboard_selection(num, workshop=False, studsovet: bool = False):
    if num + 1 in quest_five_points:
        keyboard = buttons(5, studsovet=studsovet)
    elif num + 1 in quest_ten_points:
        keyboard = buttons(10, studsovet=studsovet)
    elif num + 1 in quest_percents:
        keyboard = buttons('%', num, workshop, studsovet=studsovet)
    elif num + 1 in quest_yes_no:
        keyboard = buttons('yes', studsovet=studsovet)
    else:
        keyboard = None

    return keyboard


def kko(id, message, name_from_vk):
    group = check_group(id)
    try:
        num = int(check_action(id).split('_')[1])
        if num >= 3:
            subjects = check_subjects_kko(id)
            print(num, subjects)
            if len(subjects) > 0:
                if subjects[-1] == 'Практикум' or message == 'Практикум':
                    workshop = True
                else:
                    workshop = False
            else:
                if message == 'Практикум':
                    workshop = True
                else:
                    workshop = False

        else:
            workshop = False
    except:
        traceback.print_exc()
        workshop = False

    if workshop:
        questions = [
            'Введи свои реальные фамилию, имя и отчество в формате:\n\nИванов Иван Иванович\n\nЭта информация '  # 1
            'нужна для верификации отзывов и предотвращения многократного ввода данных одним пользователем. В '
            'учебную часть все оценки попадут анонимизированными. Подробнее читай в статье в группе Студенческого '
            'совета',

            f'Ты учишься в группе {group.split(", ")[0]}?\n\nЕсли нет, введи номер настоящей группы. Изменить этот '  # 2
            f'параметр впоследствии будет невозможно',

            'Выбери предмет, который хочешь оценить\n\n&#10071; P.s. Если предмета нет, введи название '  # 3
            'самостоятельно',

            f'Сколько лекций ты пропустил/пропустила по тем или иным причинам?',  # 4

            'Оцени качество технического обеспечения лекций\n\n🟥 1 - непригодное\n🟩 5 - очень хорошее ',  # 5

            'Насколько понятно лектор объяснял материал?\n\n🟥 1 - Совершенно непонятно\n🟩 5 - Всё понятно',  # 6

            'Достаточно ли, на твой взгляд, лекционного материала для успешной сдачи экзамена?'  # 7
            '\n\n🟥 1 - Нужно очень много дополнительного материала\n🟩 5 - Лекции полностью покрывают курс',

            'Насколько комфортно было воспринимать материал?\n\n🟥 1 - Абсолютно некомфортно'  # 8
            '\n🟩 5 - Полностью комфортно',

            'Достаточно ли профильной литературы по данному курсу лекций?\n\n🟥 1 - Совершенно недостаточно'  # 9
            '\n🟩 5 - Вполне достаточно',

            'Насколько информация, полученная в курсе лекций, по твоему мнению, будет для тебя полезна в '  # 10
            'будущем?\n\n🟥 1 - Абсолютно бесполезна\n🟩 5 - Очень полезна',

            'Можешь оставить развернутый комментарий о курсе лекций. Возможно, у тебя есть предложения по '  # 11
            'улучшению данной программы',

            'Сколько практикумов ты пропустил/пропустила по тем или иным причинам?',  # 12

            'Поняты ли тебе были правила получения зачёта и/или система ведения БРС?\n\n🟥 1 '  # 13
            '- Совершенно непонятны\n🟩 5 - Полностью понятны',

            'Оцени качество технического обеспечения практикумов\n\n🟥 1 - Непригодное\n'  # 14
            '🟩 5 - Очень хорошее ',

            'Достаточно ли, на твой взгляд, материала по практикумам для успешного их выполнения?'  # 15
            '\n\n🟥 1 - Нужно очень много дополнительного материала\n'
            '🟩 5 - Материалы полностью достаточно',

            'Насколько комфортно было воспринимать материал?\n\n🟥 1 - Абсолютно некомфортно'  # 16
            '\n🟩 5 - Полностью комфортно',

            'Достаточно ли профильной литературы по курсу практикумов?\n\n'  # 17
            '🟥 1 - Совершенно недостаточно\n🟩 5 - Вполне достаточно',

            'Насколько информация, полученная в курсе практикумов, по твоему мнению, будет для тебя '  # 18
            'полезна в будущем?\n\n🟥 1 - Абсолютно бесполезна\n🟩 5 - Очень полезна',

            'Можешь оставить развернутый комментарий о практикумах. Возможно, '  # 19
            'у тебя есть предложения по улучшению',

            'Перейдём к программе в целом. Достаточно ли знаний у тебя было к началу курса для '  # 20
            'освоения материала?\n\n🟥 1 - Абсолютно недостаточно\n🟩 10 - Вполне достаточно',

            'Оцени курс в целом\n\n🟥 1 - Курс совершенно не понравился\n🟩 10 - Отличный курс',  # 21

            'Ты можешь оставить развернутый комментарий о курсе в целом. Возможно, у тебя есть '  # 22
            'предложения по улучшению данной программы']
    else:
        questions = [
            'Введи свои реальные фамилию имя отчество в формате:\n\nИванов Иван Иванович\n\nЭта информация '  # 1
            'нужна для верификации отзывов и предотвращения многократного ввода данных одним пользователем. В '
            'учебную часть все оценки попадут анонимизированными. Подробнее читай в статье в группе Студенческого '
            'совета',

            f'Ты учишься в группе {group.split(", ")[0]}?\n\nЕсли нет, введи номер настоящей группы. Изменить этот '  # 2
            f'параметр впоследствии будет невозможно',

            'Выбери предмет, который хочешь оценить\n\n&#10071; P.s. Если предмета нет, введи название '  # 3
            'самостоятельно',

            f'Сколько лекций ты пропустил/пропустила по тем или иным причинам?',  # 4

            'Оцени качество технического обеспечения лекций\n\n🟥 1 - непригодное\n🟩 5 - очень хорошее ',  # 5

            'Насколько понятно лектор объяснял материал?\n\n🟥 1 - Совершенно непонятно\n🟩 5 - Всё понятно',  # 6

            'Достаточно ли, на твой взгляд, лекционного материала для успешной сдачи экзамена?'  # 7
            '\n\n🟥 1 - Нужно очень много дополнительного материала\n🟩 5 - Лекции полностью покрывают курс',

            'Насколько комфортно было воспринимать материал?\n\n🟥 1 - Абсолютно некомфортно'  # 8
            '\n🟩 5 - Полностью комфортно',

            'Достаточно ли профильной литературы по данному курсу лекций?\n\n🟥 1 - Совершенно недостаточно'  # 9
            '\n🟩 5 - Вполне достаточно',

            'Насколько информация, полученная в курсе лекций, по твоему мнению, будет для тебя полезна в '  # 10
            'будущем?\n\n🟥 1 - Абсолютно бесполезна\n🟩 5 - Очень полезна',

            'Можешь оставить развернутый комментарий о курсе лекций. Возможно, у тебя есть предложения по '  # 11
            'улучшению данной программы',

            'Перейдём к семинарам. Сколько семинаров по предмету ты пропустил/пропустила '  # 12
            'по тем или иным причинам?',

            'Поняты ли тебе были правила получения зачёта и/или система ведения БРС?\n\n🟥 1 '  # 13
            '- Совершенно непонятны\n🟩 5 - Полностью понятны',

            'Оцени качество технического обеспечения семинаров\n\n🟥 1 - Непригодное\n'  # 14
            '🟩 5 - Очень хорошее ',

            'Достаточно ли, на твой взгляд, семинарского материала для успешной сдачи зачёта?'  # 15
            '\n\n🟥 1 - Нужно очень много дополнительного материала\n'
            '🟩 5 - Семинары полностью покрывают курс',

            'Насколько комфортно было воспринимать материал?\n\n🟥 1 - Абсолютно некомфортно'  # 16
            '\n🟩 5 - Полностью комфортно',

            'Достаточно ли профильной литературы по данному курсу семинаров?\n\n'  # 17
            '🟥 1 - Совершенно недостаточно\n🟩 5 - Вполне достаточно',

            'Насколько информация, полученная в курсе семинаров, по твоему мнению, будет для тебя '  # 18
            'полезна в будущем?\n\n🟥 1 - Абсолютно бесполезна\n🟩 5 - Очень полезна',

            'Можешь оставить развернутый комментарий о курсе семинаров. Возможно, '  # 19
            'у тебя есть предложения по улучшению данной программы',

            'Перейдём к программе в целом. Достаточно ли знаний у тебя было к началу курса для '  # 20
            'освоения материала?\n\n🟥 1 - Абсолютно недостаточно\n🟩 10 - Вполне достаточно',

            'Оцени курс в целом\n\n🟥 1 - Курс совершенно не понравился\n🟩 10 - Отличный курс',  # 21

            'Ты можешь оставить развернутый комментарий о курсе в целом. Возможно, у тебя есть '  # 22
            'предложения по улучшению данной программы']

    answer_is_found = True
    answer = None
    keyboard = None
    action = check_action(id)
    total_quests = len(questions)
    if check_rate_the_survey(id) is None:
        total_quests += 1

    if message == 'Сброс' and check_studsovet(id) is True:
        delete_user_kko(id)
        if all_data_kko(id) is None:
            answer = 'Данные успешно удалены', \
                     'Мы запускаем опрос по качеству образования в весеннем семестре 2022/2023' \
                     ' учебного года для всех учебных курсов. Просим Вас уделить этому особое внимание, так как' \
                     ' нами будет представлен отчёт о реализации образовательных программ перед учебной частью и ' \
                     'деканом. Чем больше отзывов будет получено, тем выше вероятность изменений.\n\nПосле начала ' \
                     'прохождения нужно будет пройти опрос до конца. На это время другие функции бота будут ' \
                     'недоступны', \
                     'Начинаем?'
            keyboard = Keyboard(one_time=True).add(Text('Нет'), color=KeyboardButtonColor.NEGATIVE) \
                .add(Text('Да'), color=KeyboardButtonColor.POSITIVE)
            change_action(id, 'KKO_prestart')
        else:
            answer = 'Произошла какая-то ошибка'

    elif action == 'KKO_prestart':
        if message == 'Да':
            try:
                if all_data_kko(id)[5] is not None:
                    continue_survey = True
                else:
                    continue_survey = False
            except:
                continue_survey = False

            if continue_survey is False:
                answer_is_found = True

                answer = f'|__________|ㅤ  ㅤ0.00%ㅤ  ㅤ1/{total_quests}\n\n' + questions[0]
                change_action(id, 'KKO_1')
            else:
                number_of_reviews = len(all_data_kko(id)[5])
                if number_of_reviews == 1:
                    answer = f'У меня уже есть 1 твой отзыв. Так держать!', \
                             'Выбери предмет, который хочешь оценить\n\n&#10071; P.s. Если предмета нет, ' \
                             'введи название самостоятельно'
                elif number_of_reviews > 1 and number_of_reviews < 5:
                    answer = f'У меня уже есть {number_of_reviews} твоих отзыва. Так держать!', \
                             'Выбери предмет, который хочешь оценить\n\n&#10071; P.s. Если предмета нет, ' \
                             'введи название самостоятельно'
                else:
                    answer = f'У меня уже есть {number_of_reviews} твоих отзывов. Так держать!', \
                             'Выбери предмет, который хочешь оценить\n\n&#10071; P.s. Если предмета нет, ' \
                             'введи название самостоятельно'
                keyboard = subjects_for_keyboard(id)
                change_action(id, 'KKO_3')

        elif check_studsovet(id) and message == 'Мои ответы':
            data = all_data_kko(id)

            if len(check_subjects_kko(id)) > 1:
                answer = ['1. ' + questions[0] + '\n\n' + data[2], '2. ' + questions[1] + '\n\n' + data[4]]
                for sub in range(len(check_subjects_kko(id))):
                    # temp = ''
                    for i in range(2, len(questions)):
                        answer.append(f'{i + 1}. ' + questions[i] + '\n\n' + str(data[i + 3][sub]))
                    answer.append('&#128025;' * 10 + '\nПЕРЕХОЖУ К СЛЕДУЮЩЕМУ ПРЕДМЕТУ\n' + '&#128037;' * 10)
            else:
                answer = ['1. ' + questions[0] + '\n\n' + data[2], '2. ' + questions[1] + '\n\n' + data[4]]
                for i in range(2, len(questions)):
                    answer.append(f'{i + 1}. ' + questions[i] + '\n\n' + str(data[i + 3][0]))
            answer.append('23. Здесь ты можешь оставить отзыв об этом опросе. Возможно, у тебя есть мысли по его '
                          'улучшению\n\n' + data[-1])
            change_action(id, 'Start')
            keyboard = standard_keyboard(id)

        else:
            answer = 'Мы в главном меню'
            keyboard = standard_keyboard(id)
            change_action(id, 'Start')

    elif action == 'KKO_end':
        add_rate_the_survey(message, id)
        answer = 'Спасибо за твой отзыв! Если хочешь, ты можешь оставить свою оценку и другим курсам. Для этого ' \
                 'снова выбери ККО на клавиатуре'
        keyboard = standard_keyboard(id)
        change_action(id, 'Start')


    elif 'KKO_' in action:

        num_quest = int(action.split('_')[1])

        if num_quest - 1 == 0:
            if 2 < len(message.split(' ')) < 6:
                add_new_user_kko(id, message, name_from_vk)
                answer = progressbar(num_quest, total_quests) + questions[num_quest]
                change_action(id, f'KKO_{num_quest + 1}')
                keyboard = Keyboard(one_time=True).add(Text(f'{group.split(", ")[0]}'),
                                                       color=KeyboardButtonColor.POSITIVE)
            else:
                answer = 'Проверь правильность введённых данных. Введи ФИО в формате:\n\nИванов Иван Иванович'

        elif num_quest - 1 == 1:
            if message in groups or message == 'Да':
                if message in groups:
                    add_group_kko(message, id)
                else:
                    add_group_kko(group, id)
                answer = progressbar(num_quest, total_quests) + questions[num_quest]
                change_action(id, f'KKO_{num_quest + 1}')
                keyboard = subjects_for_keyboard(id)
            else:
                answer = 'Не могу найти такую группу. Я брал все названия отсюда: http://ras.phys.msu.ru . Проверь ' \
                         'правильность ввода и попробуй ещё раз'

        elif num_quest - 1 == 2:
            if message not in check_subjects_kko(id):
                if 'Практикум' in message:
                    add_subject_kko(message, id)
                    num_quest += 1
                    add_answers(id, num_quest, 'Не было лекций')
                    for i in range(num_quest + 1, 11):
                        add_answers(id, i, 0)
                    add_answers(id, 11, 'Не было лекций')
                    answer = progressbar(12, total_quests) + questions[11]
                    change_action(id, f'KKO_{12}')
                    keyboard = buttons('%', 12, studsovet=check_studsovet(id))
                else:
                    add_subject_kko(message, id)
                    answer = progressbar(num_quest, total_quests) + questions[num_quest]
                    change_action(id, f'KKO_{num_quest + 1}')
                    keyboard = buttons('%', studsovet=check_studsovet(id))

            else:
                answer = progressbar(num_quest - 1, total_quests) + \
                         'У меня уже есть отзыв по этому предмету от тебя. Выбери другой'
                keyboard = subjects_for_keyboard(id)

        elif num_quest == len(questions):
            add_answers(id, num_quest, message)
            if check_rate_the_survey(id) is None:
                answer = progressbar(num_quest, total_quests) + \
                         'Здесь ты можешь оставить отзыв об этом опросе. Возможно, у тебя есть мысли по его улучшению'
                change_action(id, f'KKO_end')
            else:
                answer = 'Спасибо за твой отзыв! Если хочешь, ты можешь оставить свою оценку и для других курсов. ' \
                         'Для этого снова выбери кнопку "ККО" в главном меню'
                keyboard = standard_keyboard(id)
                change_action(id, 'Start')

        elif num_quest in quest_five_points:
            if message in ['1', '2', '3', '4', '5']:
                add_answers(id, num_quest, int(message))
                answer = progressbar(num_quest, total_quests) + questions[num_quest]
                change_action(id, f'KKO_{num_quest + 1}')
                keyboard = keyboard_selection(num_quest, studsovet=check_studsovet(id))

            elif message == 'Затрудняюсь':
                add_answers(id, num_quest, 0)
                answer = progressbar(num_quest, total_quests) + questions[num_quest]
                change_action(id, f'KKO_{num_quest + 1}')
                keyboard = keyboard_selection(num_quest, studsovet=check_studsovet(id))

            else:
                answer = progressbar(num_quest - 1, total_quests) + \
                         'Пожалуйста, используй клавиатуру для ответов, если она есть\n\n' + questions[num_quest - 1]
                keyboard = buttons(5, studsovet=check_studsovet(id))

        elif num_quest in quest_ten_points:
            if message in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                add_answers(id, num_quest, int(message))
                answer = progressbar(num_quest, total_quests) + questions[num_quest]
                change_action(id, f'KKO_{num_quest + 1}')
                keyboard = keyboard_selection(num_quest, studsovet=check_studsovet(id))

            else:
                answer = progressbar(num_quest - 1, total_quests) + \
                         'Пожалуйста, используй клавиатуру для ответов, если она есть\n\n' + questions[num_quest - 1]
                keyboard = buttons(10, studsovet=check_studsovet(id))

        elif num_quest in quest_percents:
            if message in ['50-75%', '25-50%', '0-25%']:
                add_answers(id, num_quest, message)
                answer = progressbar(num_quest, total_quests) + questions[num_quest]
                change_action(id, f'KKO_{num_quest + 1}')

                keyboard = keyboard_selection(num_quest, studsovet=check_studsovet(id))

            elif message == '75-100%':
                if num_quest < 10:
                    add_answers(id, num_quest, message)
                    for i in range(num_quest + 1, 11):
                        add_answers(id, i, 0)
                    answer = progressbar(11, total_quests) + questions[10]
                    change_action(id, f'KKO_{11}')
                else:
                    add_answers(id, num_quest, message)
                    for i in range(num_quest + 1, 19):
                        add_answers(id, i, 0)
                    answer = progressbar(18, total_quests) + questions[18]
                    change_action(id, f'KKO_{19}')

            elif message == 'Не было лекций':
                add_answers(id, num_quest, message)
                for i in range(num_quest + 1, 11):
                    add_answers(id, i, 0)
                add_answers(id, 11, 'Не было лекций')
                answer = progressbar(11, total_quests) + questions[11]
                change_action(id, f'KKO_{12}')
                keyboard = buttons('%', 12, studsovet=check_studsovet(id))

            elif message == 'Не было семинаров':
                add_answers(id, num_quest, message)
                for i in range(num_quest + 1, 19):
                    add_answers(id, i, 0)
                add_answers(id, 19, 'Не было семинаров')
                answer = progressbar(19, total_quests) + questions[19]
                change_action(id, f'KKO_{20}')
                keyboard = buttons(10, studsovet=check_studsovet(id))
            else:
                answer = progressbar(num_quest - 1, total_quests) + \
                         'Пожалуйста, используй клавиатуру для ответов, если она есть\n\n' + questions[(num_quest - 1)]
                keyboard = buttons('%', num_quest, studsovet=check_studsovet(id))

        elif num_quest in quest_yes_no:
            if message in ['Да', 'Нет']:
                add_answers(id, num_quest, message)
                answer = progressbar(num_quest, total_quests) + questions[num_quest]
                change_action(id, f'KKO_{num_quest + 1}')
                keyboard = keyboard_selection(num_quest, studsovet=check_studsovet(id))

            else:
                answer = progressbar(num_quest - 1, total_quests) + \
                         'Пожалуйста, используй клавиатуру для ответов, если она есть\n\n' + questions[(num_quest - 1)]
                keyboard = buttons('yes', studsovet=check_studsovet(id))

        else:
            add_answers(id, num_quest, message)
            answer = progressbar(num_quest, total_quests) + questions[num_quest]
            keyboard = keyboard_selection(num_quest, studsovet=check_studsovet(id))
            change_action(id, f'KKO_{num_quest + 1}')

    return answer_is_found, answer, keyboard
