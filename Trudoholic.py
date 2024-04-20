import time
import requests
from Database import *
from config import token
import datetime
import schedule
from tqdm import tqdm


def all_homework():
    conn, cursor = connecting()
    cursor.execute("""SELECT group_user FROM homeworks""")
    groups = [r[0] for r in cursor.fetchall()]
    cursor.execute("""SELECT homeworks FROM homeworks""")
    homeworks = [r[0] for r in cursor.fetchall()]
    disconnecting(conn, cursor)

    return groups, homeworks


def all_books():
    conn, cursor = connecting()
    cursor.execute("""SELECT group_user FROM books""")
    groups = [r[0] for r in cursor.fetchall()]
    cursor.execute("""SELECT books FROM books""")
    books = [r[0] for r in cursor.fetchall()]
    disconnecting(conn, cursor)

    return groups, books


def search_ids():
    conn, cursor = connecting()
    cursor.execute("""SELECT (id, first_name, last_name, group_user) FROM users WHERE headman = true""")
    headman = [r[0] for r in cursor.fetchall()]

    for i in range(len(headman)):
        temp = headman[i].replace('(', '').replace(')', '').replace('"', '').split(',')
        headman[i] = [temp[0]]
        for k in range(1, 4):
            headman[i].append(temp[k])
    disconnecting(conn, cursor)
    return headman


def history_messages(user_id, offset=0):
    time.sleep(.5)
    link = 'https://api.vk.com/method/'
    method = 'messages.getHistory'
    group_id = '34300772'
    request = f'{link}{method}?access_token={token}&offset={offset}&user_id={user_id}&count=200&group_id={group_id}&v=5.131'
    return requests.get(request).json()['response']['items']


def split_attachments_to_array(user_id):
    history_attachs = []
    for j in range(int(count_messages(user_id) / 200) + 1):
        messages = history_messages(user_id, offset=j * 200)
        time.sleep(.1)
        for i in messages:
            try:
                if i['from_id'] == user_id and len(i['attachments']) > 0:
                    if len(i['attachments']) > 1:
                        temp = []
                        for attach in i['attachments']:
                            type_attach = attach['type']
                            temp.append(f"{type_attach}{attach[type_attach]['owner_id']}_"
                                        f"{attach[type_attach]['id']}_{attach[type_attach]['access_key']}")
                        history_attachs.append([i['date'], temp])
                    else:
                        attach = i['attachments'][0]
                        type_attach = i['attachments'][0]['type']
                        history_attachs.append([i['date'], [f"{type_attach}{attach[type_attach]['owner_id']}_"
                                                            f"{attach[type_attach]['id']}_"
                                                            f"{attach[type_attach]['access_key']}"]])

            except:
                pass


    return history_attachs


def count_messages(user_id):
    link = 'https://api.vk.com/method/'
    method = 'messages.getHistory'
    group_id = '34300772'
    request = f'{link}{method}?access_token={token}&user_id={user_id}&count=1&group_id={group_id}&v=5.131'
    return requests.get(request).json()['response']['count']


def update_homework_db(homework, group):
    conn, cursor = connecting()
    try:
        cursor.execute(
            """UPDATE homeworks SET homeworks = %s WHERE group_user = %s""",
            (json.dumps(homework, ensure_ascii=False), group,))
        conn.commit()
    except Exception as _ex:
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def update_books_db(book, group):
    conn, cursor = connecting()
    try:
        cursor.execute(
            """UPDATE books SET books = %s WHERE group_user = %s""", (json.dumps(book, ensure_ascii=False), group,))
        conn.commit()
    except Exception as _ex:
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def homeworks_updater():
    groups, homeworks = all_homework()
    headman = search_ids()
    with tqdm(total=len(headman), desc='Обновление БД ДЗ') as pbar:
        for i in headman:
            time.sleep(.1)
            user_id = int(i[0])
            try:
                index_group = groups.index(i[3][:3])
                history_attachs = split_attachments_to_array(user_id)

                homework = homeworks[index_group]
                if len(history_attachs) > 0:
                    for subject in homework.keys():
                        for num_date in range(len(homework[subject]['Date'])):
                            for j in range(len(history_attachs)):
                                try:
                                    if history_attachs[j][0] == homework[subject]['Date'][num_date]:
                                        homework[subject]['Attachments'][num_date] = history_attachs[j][1]

                                except:
                                    pass
                        time.sleep(.1)

                    update_homework_db(homework, groups[index_group])
            except:
                pass

            pbar.update(1)
    print(f'{datetime.datetime.now()}:  Обновлены ссылки на вложения в homeworks')
    books_updater()


def books_updater():
    groups, books = all_books()
    headman = search_ids()
    with tqdm(total=len(headman), desc='Обновление БД учебников') as pbar:
        for i in headman:
            user_id = int(i[0])
            try:
                index_group = groups.index(i[3][:3])
                history_attachs = split_attachments_to_array(user_id)

                book = books[index_group]
                if len(history_attachs) > 0:
                    for num_date in range(len(book['Date'])):
                        for j in range(len(history_attachs)):
                            try:
                                if history_attachs[j][0] == book['Date'][num_date]:
                                    book['Link'][num_date] = history_attachs[j][1]

                            except:
                                pass

                        time.sleep(.1)

                update_books_db(book, groups[index_group])
            except:
                pass
            pbar.update(1)
    print(f'{datetime.datetime.now()}:  Обновлены ссылки на вложения в books\n\n')


schedule.every(12).hours.do(homeworks_updater)

while True:
    schedule.run_pending()
    time.sleep(1)
