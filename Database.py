import pymorphy2
import psycopg2
from config import host, user, password, db_name, port
import traceback
import datetime
from openpyxl import Workbook
import json


def connecting():
    conn = psycopg2.connect(user=user,
                            password=password,
                            host=host,
                            port=port,
                            database=db_name)
    cursor = conn.cursor()
    return conn, cursor


def disconnecting(conn, cursor):
    if conn:
        cursor.close()
        conn.close()


def checking():
    try:
        conn, cursor = connecting()
        print("Информация о сервере PostgreSQL")
        parameters = conn.get_dsn_parameters()
        for key in parameters.keys():
            print(f'{key}:      {parameters[key]}')
        # Выполнение SQL-запроса
        cursor.execute("SELECT version();")
        # Получить результат
        record = cursor.fetchone()
        print("Вы подключены к - ", record, "\n")
        # cursor.execute('create database Test')
    except Exception:
        traceback.print_exc()
        print('Ошибка при подключении к базе данных')
    finally:
        disconnecting(conn, cursor)


def check_id(id):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT * FROM users WHERE id = %s""", (id,))
        count = cursor.fetchall()
        if len(count) > 0:
            return True
        else:
            return False
    except Exception:
        traceback.print_exc()
        print('Ошибка при подключении к базе данных check_id')
    finally:
        disconnecting(conn, cursor)


def check_action(id):
    try:
        conn, cursor = connecting()

        cursor.execute('SELECT action FROM users WHERE id = %s', (id,))
        check = cursor.fetchone()
        return check[0]
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def check_group(id):
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT group_user FROM users WHERE id = %s' % id)
        check = cursor.fetchone()[0]
        return check
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def add_new_user(id, first_name, last_name):
    gender = pymorphy2.MorphAnalyzer()
    if gender.parse(first_name)[0].tag.gender == 'masc':
        sex = 'Мужской'
    else:
        sex = 'Женский'

    try:
        conn, cursor = connecting()
        cursor.execute(
            """INSERT INTO users (id, first_name, last_name, sex, action, first_conn, last_conn, num_of_conn, headman, time_new_schedule) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (id, first_name, last_name, sex, 'Add_group', str(datetime.datetime.now()), str(datetime.datetime.now()), 1,
             False, '18:00',))
        conn.commit()

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def add_group(id, group):
    try:
        conn, cursor = connecting()
        if check_group(id) is not None:
            group = check_group(id) + ', ' + group
        cursor.execute("""UPDATE users SET group_user = '%s' WHERE id = %d""" % (group, id))
        conn.commit()

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def change_main_group(id, group):
    conn, cursor = connecting()
    groups = check_group(id).split(', ')
    groups[0] = group
    cursor.execute(
        """UPDATE users SET group_user = '%s', action = '%s' WHERE id = %d""" % (', '.join(groups), 'Start', id))
    conn.commit()


def check_time_schedule(user_id):
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT time_new_schedule FROM users WHERE id = %s', (user_id,))
        data = str(cursor.fetchone()[0])
        return data
    except Exception as _ex:
        print("[INFO] Error check_time_schedule while working with PostgreSQL", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def check_last_connection(user_id):
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT last_conn FROM users WHERE id = %s', (user_id,))
        data = datetime.datetime.strptime(cursor.fetchone()[0], '%Y-%m-%d %H:%M:%S.%f')
        return data
    except Exception as _ex:
        print("[INFO] Error check_last_connection while working with PostgreSQL", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def update_last_connection(user_id):
    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE users SET last_conn = %s WHERE id = %s""", (str(datetime.datetime.now()), user_id,))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def change_time_schedule(id, time):
    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE users SET time_new_schedule = %s WHERE id = %s""", (time, id,))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def change_action(id, action):
    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE users SET action = '%s' WHERE id = %d""" % (action, id))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def delete_group(id, group):
    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE users SET group_user = '%s', action = '%s' WHERE id = %d""" % (group, 'Start', id))
        conn.commit()
        return 'Группа успешно удалена'

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
        return 'Произошла непредвиденная ошибка'

    finally:
        disconnecting(conn, cursor)


def delete_all_groups(id):
    try:
        conn, cursor = connecting()
        groups = check_group(id).split(', ')
        groups[0] = 'NULL'
        cursor.execute("""UPDATE users SET group_user = '%s' WHERE id = %d""" % (', '.join(groups), id))
        conn.commit()
        change_action(id, 'Add_group')
        return 'Группа успешно удалена'

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL in delete_all_groups", _ex)
        return 'Произошла непредвиденная ошибка'

    finally:
        disconnecting(conn, cursor)


def all_data(id):
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
        data = cursor.fetchone()
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL all_data", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def check_headman(id):
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT headman FROM users WHERE id = %d' % id)
        data = cursor.fetchone()[0]

        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_headman", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def check_admin(id):
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT admin FROM users WHERE id = %d' % id)
        data = cursor.fetchone()[0]
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_headman", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def add_group_for_homework(group):
    try:
        conn, cursor = connecting()
        cursor.execute(
            """INSERT INTO homeworks (group_user) VALUES (%s)""", (group,))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def check_group_homework(group):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT homeworks FROM homeworks WHERE group_user = '%s'""" % group)
        data = cursor.fetchone()[0]
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return None
    finally:
        disconnecting(conn, cursor)


def check_homework(group):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT homeworks FROM homeworks WHERE group_user = %s""", (group,))
        data = cursor.fetchone()[0]
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return None
    finally:
        disconnecting(conn, cursor)


def check_subject(group):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT homeworks FROM homeworks WHERE group_user = '%s'""" % group)
        data = cursor.fetchone()[0]
        return [*data]
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return None
    finally:
        disconnecting(conn, cursor)


def add_subject(group, subject):
    try:
        conn, cursor = connecting()
        dictionary = check_homework(group)

        if dictionary is None:
            dictionary = {subject: {'Homeworks': ['Домашнее задание не добавлено'],
                                    'Attachments': ['Вложений нет']}}
        else:
            dictionary[subject] = {'Homeworks': ['Домашнее задание не добавлено'],
                                   'Attachments': ['Вложений нет']}

        cursor.execute(
            """UPDATE homeworks SET homeworks = '%s' WHERE group_user = '%s'""" % (
                json.dumps(dictionary, ensure_ascii=False), group))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL add_subject", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def delete_subject(group, subject):
    try:
        conn, cursor = connecting()
        dictionary = check_homework(group)

        del dictionary[subject]

        cursor.execute(
            """UPDATE homeworks SET homeworks = '%s' WHERE group_user = '%s'""" % (
                json.dumps(dictionary, ensure_ascii=False), group))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL add_subject", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def add_homework(group, homework, attachment, date, subject):
    try:
        conn, cursor = connecting()
        dictionary = check_homework(group)

        if dictionary[subject]['Homeworks'][0] == 'Домашнее задание не добавлено':
            dictionary[subject]['Homeworks'] = [homework]
            dictionary[subject]['Attachments'] = [attachment]
            dictionary[subject]['Date'] = [date]
        else:
            dictionary[subject]['Homeworks'].append(homework)
            dictionary[subject]['Attachments'].append(attachment)
            dictionary[subject]['Date'].append(date)

        # if dictionary[subject]['Homeworks'][0] == 'Домашнее задание не добавлено':
        #     dictionary[subject]['Homeworks'] = [homework]
        #     dictionary[subject]['Attachments'] = [attachment]
        # else:
        #     dictionary[subject]['Homeworks'].append(homework)
        #     dictionary[subject]['Attachments'].append(attachment)

        cursor.execute(
            """UPDATE homeworks SET homeworks = %s WHERE group_user = %s""",
            (json.dumps(dictionary, ensure_ascii=False), group,))
        conn.commit()
        print(dictionary)
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def delete_homework(group, index, subject):
    try:
        conn, cursor = connecting()
        dictionary = check_homework(group)

        answer = dictionary[subject]['Homeworks'][index]

        if len(dictionary[subject]['Homeworks']) == 1:
            dictionary[subject]['Homeworks'][index] = 'Домашнее задание не добавлено'
            dictionary[subject]['Attachments'][index] = 'Вложений нет'
            dictionary[subject]['Date'][index] = ''
        else:
            dictionary[subject]['Homeworks'].pop(index)
            dictionary[subject]['Attachments'].pop(index)
            dictionary[subject]['Date'].pop(index)

        cursor.execute(
            """UPDATE homeworks SET homeworks = %s WHERE group_user = %s""", (json.dumps(dictionary), group,))
        conn.commit()
        return answer
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL delete_homework", _ex)
        return 'При загрузке базы данных произошла непредвиденная ошибка. Мы уже работаем над её странением'
    finally:
        disconnecting(conn, cursor)


def add_editing_subject(group, subject):
    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE homeworks SET editing_subject = '%s' WHERE group_user = '%s'""" % (subject, group))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL add_subject", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def check_editing_subject(group):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT editing_subject FROM homeworks WHERE group_user = '%s'""" % group)
        data = cursor.fetchone()[0]
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return None
    finally:
        disconnecting(conn, cursor)


def num_of_conn(id):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT num_of_conn FROM users WHERE id = %d""" % id)
        num = cursor.fetchone()[0] + 1
        cursor.execute("""UPDATE users SET num_of_conn = %d WHERE id = %d""" % (num, id))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def add_group_for_books(group):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT * FROM books WHERE group_user = '%s'""" % group)
        count = cursor.fetchone()
        if count is None:
            dictionary = {'Title': ['Учебники не добавлены'],
                          'Link': [''],
                          'Date': []}
            cursor.execute(
                """INSERT INTO books (group_user, books) VALUES('%s', '%s')""" % (
                    group, json.dumps(dictionary, ensure_ascii=False)))
            conn.commit()

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def add_books(group, name, link, date):
    try:
        dictionary = check_books(group)

        if dictionary['Title'][0] == 'Учебники не добавлены':
            dictionary['Title'][0] = name
            dictionary['Link'][0] = link
            dictionary['Date'] = [date]
        else:
            dictionary['Title'].append(name)
            dictionary['Link'].append(link)
            dictionary['Date'].append(date)

        conn, cursor = connecting()
        cursor.execute("""UPDATE books SET books = '%s' WHERE group_user = '%s'""" % (
            json.dumps(dictionary, ensure_ascii=False), group))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def delete_books(group, index):
    try:
        dictionary = check_books(group)
        if len(dictionary['Title']) == 1:
            dictionary = {'Title': ['Учебники не добавлены'],
                          'Link': [''],
                          'Date': []
                          }
        else:
            dictionary['Title'].pop(index)
            dictionary['Link'].pop(index)
            dictionary['Date'].pop(index)

        conn, cursor = connecting()
        cursor.execute("""UPDATE books SET books = '%s' WHERE group_user = '%s'""" % (
            json.dumps(dictionary, ensure_ascii=False), group))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def check_books(group):
    conn, cursor = connecting()
    try:
        cursor.execute("""SELECT books FROM books WHERE group_user = '%s'""" % group)
        data = cursor.fetchone()[0]
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return 'Error'
    finally:
        disconnecting(conn, cursor)


def list_headman():
    conn, cursor = connecting()
    try:
        cursor.execute("""SELECT id FROM users WHERE headman = true""")
        data = cursor.fetchall()
        data = [i[0] for i in data]
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return 'Error'
    finally:
        disconnecting(conn, cursor)


def list_groups_from_books():
    conn, cursor = connecting()
    try:
        cursor.execute("""SELECT group_user FROM books""")
        data = cursor.fetchall()
        data = [i[0] for i in data]
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return 'Error'
    finally:
        disconnecting(conn, cursor)


def list_groups_from_homeworks():
    conn, cursor = connecting()
    try:
        cursor.execute("""SELECT group_user FROM homeworks""")
        data = cursor.fetchall()
        data = [i[0] for i in data]
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL list_groups_from_homeworks", _ex)
        return 'Error'
    finally:
        disconnecting(conn, cursor)


def add_group_for_session(group):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT * FROM session WHERE group_user = '%s'""" % group)
        count = cursor.fetchone()
        if count is None:
            dictionary = {'Date': [],
                          'Subject': [],
                          'Room': [],
                          'Type': []}
            cursor.execute(
                """INSERT INTO session (group_user, session) VALUES('%s', '%s')""" % (
                    group, json.dumps(dictionary, ensure_ascii=False)))
            conn.commit()

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL add_group_for_session", _ex)

    finally:
        disconnecting(conn, cursor)


def check_session(group):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT session FROM session WHERE group_user = '%s'""" % group)
        data = cursor.fetchone()[0]
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return None
    finally:
        disconnecting(conn, cursor)


def add_session(group, dict):
    try:
        conn, cursor = connecting()
        dictionary = check_homework(group)

        cursor.execute("""UPDATE session SET session = '%s' WHERE group_user = '%s'""" % (
            json.dumps(dict, ensure_ascii=False), group))
        conn.commit()
        print(dictionary)
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def start_quize(id):
    try:
        name, last_name = all_data(id)[1:3]
        conn, cursor = connecting()
        print(' '.join([last_name, name]))
        if id in [240971040, 299407304]:
            cursor.execute("insert into quize values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (id, datetime.datetime.now(), 0, 0, 0, False, datetime.datetime.now(),
                            ' '.join([last_name, name]), True))
        else:
            cursor.execute("insert into quize values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (id, datetime.datetime.now(), 0, 0, 0, False, datetime.datetime.now(),
                            ' '.join([last_name, name]), False))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL start_quize", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def quize_all_data(id):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT * FROM quize WHERE id = %s""", (id,))
        row_data = cursor.fetchone()
        data = {'start_time': row_data[1],
                'number': row_data[2],
                'timer': row_data[3],
                'score': row_data[4],
                'end': row_data[5],
                'end_time': row_data[6],
                'admin': row_data[8]}
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL quize_all_data", _ex)
        return None
    finally:
        disconnecting(conn, cursor)


def reset_quize(id):
    try:
        conn, cursor = connecting()
        cursor.execute("""DELETE FROM quize WHERE id =  %s""", (id,))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL quize_delete_date", _ex)
    finally:
        disconnecting(conn, cursor)


def quize_change_number_and_score(id, number, score):
    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE quize SET (number_question, score) = (%s, %s) WHERE id = %s""", (number, score, id,))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL check_books", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def quize_end(id, num, timer, score):
    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE quize SET (number_question, timer, score, end_time, end_quize) = (%s, %s, %s, %s, %s) 
        WHERE id = %s""", (num,
                           timer,
                           score,
                           datetime.datetime.now(),
                           True,
                           id,))
        conn.commit()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def studsovet():
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT id FROM users WHERE studsovet = %s', (True,))
        ids = cursor.fetchall()
        disconnecting(conn, cursor)
    except:
        ids = []
    return ids


def check_studsovet(id):
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT studsovet FROM users WHERE id = %s', (id,))
        data = cursor.fetchone()[0]
        print('check_studsovet      ', data)
        return data
    except:
        traceback.print_exc()
        pass
    finally:
        disconnecting(conn, cursor)


def delete_user(id):
    try:
        conn, cursor = connecting()
        cursor.execute('DELETE FROM users WHERE id = %s', (id,))
        conn.commit()
        return True
    except Exception as Ex:
        print(Ex)
        return False
    finally:
        disconnecting(conn, cursor)