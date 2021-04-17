import requests
import constants
import datetime
import sqlite3
import random
url = "https://api.telegram.org/bot" + constants.token + "/"
conn = sqlite3.connect('db.db')
c = conn.cursor()
class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()
        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = []
        return last_update

    def  send_picture(self, chat_id, photo_id):
        params = {'chat_id': chat_id, 'photo': photo_id}
        method = 'sendPhoto'
        resp = requests.post(self.api_url + method, params)
        return resp

greet_bot = Bot(constants.token)
greetings = ('здравствуй', 'привет', 'ку', 'здорово','хай')
now = datetime.datetime.now()

def main():
    new_offset = None
    today = now.day
    hour = now.hour
    while True:
        greet_bot.get_updates(new_offset)
        last_update = greet_bot.get_last_update()
        if len(last_update) > 0:
            print(last_update)
            last_update_id = last_update['update_id']
            last_update_message = last_update['message']

            if 'text' in last_update_message:
                last_chat_text = last_update['message']['text']
                last_chat_id = last_update['message']['chat']['id']
                last_chat_name = last_update['message']['chat']['first_name']
                if last_chat_text.lower() in greetings and 0 <= hour < 12:
                    greet_bot.send_message(last_chat_id, 'Доброе утро, {}'.format(last_chat_name))
                elif last_chat_text.lower() in greetings and 12 <= hour < 17:
                    greet_bot.send_message(last_chat_id, 'Добрый день, {}'.format(last_chat_name))
                elif last_chat_text.lower() in greetings and 17 <= hour <= 23:
                    greet_bot.send_message(last_chat_id, 'Добрый вечер, {}'.format(last_chat_name))

                if last_chat_text.lower() == '/art':
                    c.execute('SELECT * FROM events')
                    evt = c.fetchall()
                    print(evt)
                    if (len(evt) == 0):
                        greet_bot.send_message(last_chat_id, "Картинок нет!")
                    else:
                        c.execute('SELECT COUNT(*) FROM events')
                        count = c.fetchall()
                        conn.commit()
                        count = count[0][0]
                        print(count)
                        greet_bot.send_picture(last_chat_id,evt[random.randint(0,count-1)][1])

                if last_chat_text.lower() == '/help':
                    greet_bot.send_message(last_chat_id,"""
                    /help - Список всех команд \n/art - Получить картинку\nТакже вы можете поздороваться с ботом или загрузить свою картинку, попробуйте!
                    """)
                new_offset = last_update_id + 1

            if 'photo' in last_update_message:
                file_id = last_update['message']['photo'][0]['file_id']
                last_chat_id = last_update['message']['chat']['id']
                print(file_id)
                insert_query = 'INSERT INTO events (file_id) VALUES ("{}")'.format(file_id)
                c.execute(insert_query)
                conn.commit()
                greet_bot.send_message(last_chat_id,"Ваша картинка добавлена в базу!")
                new_offset = last_update_id + 1

if __name__ == '__main__':
    init_query = 'CREATE TABLE IF NOT EXISTS events(id integer PRIMARY KEY AUTOINCREMENT NOT NULL ,file_id text)'
    c.execute(init_query)
    conn.commit()
    try:
        main()
    except KeyboardInterrupt:
        exit()