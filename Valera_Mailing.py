import time
from config import token
import requests
from Database import studsovet
import random
import schedule

link = 'https://api.vk.com/method/'
method = 'messages.send?'


def studsovet_table():
    method = 'messages.send'
    message = 'Привет!\n\nНе забудь заполнить табличку с результатами работы за неделю 😉'

    row_ids = studsovet()
    ids = list(map(lambda i: row_ids[i][0], range(len(row_ids))))

    for id in ids:
        try:
            random_id = random.randint(0, 2 ** 32)
            address = f'https://api.vk.com/method/{method}?access_token={token}&user_id={id}&random_id={random_id}&message={message}&v=5.131'
            print(requests.get(address).text)
            print(address)
            print(f'Сообщение отправлено для {id}\n')
        except:
            print(f'Не удалось отправить сообщение для {id}')


schedule.every().sunday.at("18:40").do(studsovet_table)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as Ex:
        print(Ex)