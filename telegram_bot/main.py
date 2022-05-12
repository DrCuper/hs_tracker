"""Bot for bg"""
from random import randint
from threading import Thread
from time import sleep
import datetime
import logging
import ssl
import telebot
import json
import requests
import random

import markups

from aiohttp import web

logging.basicConfig(filename='logs/telegram_bot.log', filemode='a', format='[%(asctime)s] %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

API_URL = "http://158.69.169.128:8765"

API_TOKEN = '2091843643:AAHUq-hDiXRnRJT8YIPN5b4DdKOvAB0azmA'

WEBHOOK_HOST = '158.69.169.128'
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = 'webhook_cert.pem'
WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'

WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
WEBHOOK_URL_PATH = f"/{API_TOKEN}/"

bad_words_user = [
    'Жаль что твоя мать это не увидела',
    'С таким столом можно и без семьи жить',
    'Не знал, что в даркнете у вас есть карта постоянного клиента на продажу родственников',
    'Зато можете не думать о подарках родственникам',
    'Опять ты включил свой 3D-принтер'
]

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = web.Application()

async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle)

@bot.message_handler(commands=['start', 'random', 'test'])
def commands(message):
    """Answer to commands"""
    try:

        if message.text.split(' ')[0] == '/random':

            if len(message.text.split(' ')) == 1:

                bot.send_message(message.chat.id, randint(1, 100))

            elif len(message.text.split(' ')) == 2:


                numbers = []
                even, odd = 0, 0

                for i in range(int(message.text.split(' ')[1])):

                    numbers.append(randint(1, 100))

                    if numbers[-1] % 2 == 0:

                        even += 1

                    else:

                        odd += 1

                bot.send_message(message.chat.id, f'Четных - {even}, Нечетных - {odd}')
                bot.send_message(message.chat.id, str(numbers)[:])

                logger.info(f'{message.from_user.first_name} заролял {str(numbers[:])}')
                even, odd = 0, 0

            elif len(message.text.split(' ')) == 3:

                numbers = []
                even, odd = 0, 0

                if message.text.split(' ')[2] == 'even':

                    while True:

                        numbers.append(randint(1, 100))

                        if numbers[-1] % 2 == 0:

                            even += 1

                        else:

                            odd += 1

                        if even == int(message.text.split(' ')[1]): 
                            break

                elif message.text.split(' ')[2] == 'odd':

                    while True:

                        numbers.append(randint(1, 100))

                        if numbers[-1] % 2 == 0:

                            even += 1

                        else:

                            odd += 1

                        if odd == int(message.text.split(' ')[1]): break

                bot.send_message(message.chat.id, f'Четных - {even}, Нечетных - {odd}')
                bot.send_message(message.chat.id, str(numbers)[:])

                logger.info(f'{message.from_user.first_name} заролял {str(numbers[:])}')

        elif message.text == '/start':

            bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.first_name}!')
            bot.send_message(message.chat.id, 'Выберите нужную функцию', reply_markup = markups.markup_layout())

        elif message.text == '/test':

            th = Thread(target=test(message), daemon=True)

        else:

            bot.send_message(message.chat.id, "Wrong value",
                                    reply_markup = markups.markup_layout())  # 'https://youtu.be/fO27eOMwaYk'

    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)



@bot.message_handler(func=lambda message: True, content_types=['text'])
def answer(message):
    try:
            
        if message.text in ('1', '2', '3', '4', '5', '6', '7', '8'):

            add_place(message)
            
        elif message.text == "Личная статистика":

            msg = bot.reply_to(message, "Выберете статистику", reply_markup= markups.personal_layout())
            bot.register_next_step_handler(msg, personal_stats)

        elif message.text == "Еженедельная сводка":

            msg = bot.reply_to(message, "Выберете тип сводки", reply_markup = markups.weekly_agenda_layout())
            bot.register_next_step_handler(msg, weekly_agenda)

        elif message.text == "Последние 10 игр":

            msg = bot.reply_to(message, "Что хотите узнать ?", reply_markup = markups.last_ten_games_layout())
            bot.register_next_step_handler(msg, last_ten_games)
            
        elif message.text == "Рейтинги":

            msg = bot.reply_to(message, "Выберите рейтинг", reply_markup = markups.bg_rating_layout())
            bot.register_next_step_handler(msg, bg_rating)

        elif message.text == "Удалить запись":

            id_records = json.loads(requests.request("GET", f'{API_URL}/ten_last?id_player={message.chat.id}').text)
            
            msg = bot.reply_to(message, "Выберете запись", reply_markup = markups.delete_record_layout(id_records))
            bot.register_next_step_handler(msg, delete_record, id_records)

        elif message.text == "Другое":

            msg = bot.reply_to(message, "Другое", reply_markup=markups.others_layout())
            bot.register_next_step_handler(msg, others)

        else:
            bot.send_message(message.chat.id, "Wrong value",
                             reply_markup = markups.markup_layout())  # 'https://youtu.be/fO27eOMwaYk'

    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)


def personal_stats(message):

    try:

        if message.text == "Среднее место по патчам":

            response = sorted(json.loads(requests.request("GET", f'{API_URL}/total_avg_user_per_version?id_player={message.chat.id}').text),
                                   key=lambda d: d['bg_version'], reverse=True)

            for line in response:

                bot.send_message(message.chat.id, f"Ваш средний рейтинг за патч {line.get('bg_version')} - {format(line.get('avg'), '.2f')}", reply_markup = markups.markup_layout())

        elif message.text == "Итоговых мест":

            response = sorted(json.loads(requests.request("GET", f'{API_URL}/total_games_user_per_place?id_player={message.chat.id}').text),
                                   key=lambda d: d['place'], reverse=False)

            for line in response:

                bot.send_message(message.chat.id, f"Топ-{line.get('place')} - {line.get('count')} раз", reply_markup = markups.markup_layout())
      
        
        elif message.text == "Назад":
            bot.send_message(message.chat.id, "Главное меню", reply_markup = markups.markup_layout())

        else:
            bot.send_message(message.chat.id, "Wrong value",
                             reply_markup = markups.markup_layout())

    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)   

def test(message):

    try:

        for i in range(1000):
            
            bot.send_message(message.chat.id, f"Test message №{i}")
            sleep(1)
    
    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)

def others(message):

    try:
        
        if message.text == "Назад":
            bot.send_message(message.chat.id, "Главное меню", reply_markup = markups.markup_layout())

        else:
            bot.send_message(message.chat.id, "Wrong value",
                             reply_markup = markups.markup_layout())

    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)    

def add_place(message):

    try:

        if message.text in ('1', '2', '3', '4', '5', '6', '7', '8'):

            payload = json.dumps({
                                "id_player": message.chat.id,
                                "place": message.text,
                                "dt_insert": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
            headers = {
                      'Content-Type': 'application/json'
                      }

            response = requests.request("POST", f'{API_URL}/add_place', headers=headers, data=payload).text

            if response != '1':

                logger.error('Something went wrong with add_place !')
                bot.send_message(message.chat.id, f'Something went wrong !\nRespose= {response}',
                             reply_markup = markups.markup_layout())
                return 'Something went wrong !'


            logger.info(f"{message.from_user.first_name} занял {message.text} место")

            if message.text in ('1', '8'):

                response = json.loads(requests.request("GET", f'{API_URL}/all_players_except_one?id_player={message.chat.id}').text)

                if message.text == '1':

                    for line in response:

                        bad_words_other = [
                            f'Жаль, что мать {message.from_user.first_name} не увидела его победы',                                                
                            f'C таким столом, как у {message.from_user.first_name}, можно и без семьи жить',                                                 
                            f'Никто не знал, что у {message.from_user.first_name} в даркнете есть карта постоянного клиента на продажу родственников',
                            f'Зато {message.from_user.first_name} может не думать о подарках родственникам',                             
                            f'{message.from_user.first_name} в очередной раз включил свой 3D-принтер'
                        ]

                        bot.send_message(line.get('id_player'), random.choice(bad_words_other))

                    bot.send_message(message.chat.id, random.choice(bad_words_user))
                    
                elif message.text == '8':

                    bot.send_message(line[0], f"Какая жалость, {message.from_user.first_name} занял топ-8 !")


            avg_place = json.loads(requests.request("GET", f'{API_URL}/total_avg_user?id_player={message.chat.id}', headers=headers, data=payload).text)

            bot.send_message(message.chat.id, f"Ваше среднее место - {format(avg_place[0].get('avg'), '.2f')}",
                             reply_markup = markups.markup_layout())

        elif message.text == "Назад":
            bot.send_message(message.chat.id, "Главное меню", reply_markup = markups.markup_layout())

        else:
            bot.send_message(message.chat.id, "Wrong value",
                             reply_markup = markups.markup_layout())


    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)


def delete_record(message, records):

    try:
        
        id_records = []

        for record in records:
            id_records.append(record.get('id_record'))

        if message.text[0] == '№':

            id_record = int(message.text[1::].split(',')[0])

            if id_record in id_records:

                response = requests.request("DELETE", f'{API_URL}/delete_record?id_record={id_record}').text

                if response == '1':

                    bot.send_message(message.chat.id, "Удалено", reply_markup = markups.markup_layout())
                    logger.info(f"{message.from_user.first_name} удалил {message.text[1::].split(',')[1]} место")

                else:

                    bot.send_message(message.chat.id, "Что-то пошло не так", reply_markup = markups.markup_layout())

            else:

                bot.send_message(message.chat.id, "Что-то пошло не так", reply_markup = markups.markup_layout())

        elif message.text == "Назад":

            bot.send_message(message.chat.id, "Главное меню", reply_markup = markups.markup_layout())

        else:
            bot.send_message(message.chat.id, "Wrong value",
                             reply_markup = markups.markup_layout())


    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)


def last_ten_games(message):

    try:

        if message.text == "Показать":

            response = json.loads(requests.request("GET", f'{API_URL}/ten_last?id_player={message.chat.id}').text)

            for line in response:

                bot.send_message(message.chat.id, f"{line.get('id_record')}. Место - {line.get('place')}, время - {line.get('dt_insert')}, версия игры - {line.get('bg_version')}", reply_markup = markups.markup_layout())

        elif message.text == "Среднее":

            response = json.loads(requests.request("GET", f'{API_URL}/ten_last_avg?id_player={message.chat.id}').text)

            bot.send_message(message.chat.id, f"Ваш средний рейтинг за последние 10 игр - {format(response[0].get('avg'), '.2f')}", reply_markup = markups.markup_layout())

        elif message.text == "Назад":

            bot.send_message(message.chat.id, f"Главное меню", reply_markup = markups.markup_layout())

        else:

            bot.reply_to(message, 'Что-то пошло не так', reply_markup = markups.markup_layout())


    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)

patches = []

def avg_rating(message):

    try:

        if message.text == "Общий":

            response = sorted(json.loads(requests.request("GET", f'{API_URL}/total_avg').text),
                                    key=lambda d: d['avg'], reverse=False)

            line = f"Лидер по среднему рейтингу - {response[0].get('v_name')}, со средним местом - {format(response[0].get('avg'), '.2f')}"

            cnt = 0

            for person in response:

                cnt = cnt + 1

                if person.get('v_name') == response[0].get('v_name'): 
                    continue

                line = line + f"\n{cnt}. {person.get('v_name')}, со средним местом - {format(person.get('avg'), '.2f')}"

            bot.send_message(message.chat.id, line, reply_markup = markups.markup_layout())

        elif message.text == "Текущий":

            bg_version = json.loads(requests.request("GET", f'{API_URL}/bg_version_bd').text).get('bg_version')
            
            response = sorted(json.loads(requests.request("GET", f'{API_URL}/total_avg_per_special_version?version={bg_version}').text),
                    key=lambda d: d['avg'], reverse=False)

            line = f"Лидер по среднему рейтинга текущего патча - {response[0].get('v_name')}, со средним местом - {format(response[0].get('avg'), '.2f')}"

            cnt = 0

            for person in response:

                cnt = cnt + 1

                if person.get('v_name') == response[0].get('v_name'): 
                    continue

                line = line + f"\n{cnt}. {person.get('v_name')}, со средним местом - {format(person.get('avg'), '.2f')}"

            bot.send_message(message.chat.id, line, reply_markup = markups.markup_layout())
        
        elif message.text == "Устаревший":

            response = sorted(json.loads(requests.request("GET", f'{API_URL}/bg_version_old').text),
                                    key=lambda d: d['bg_version'], reverse=True)

            for line in response:

                patches.append(line.get('bg_version'))

            msg = bot.reply_to(message, "Выберете интересующий вас устаревший патч", reply_markup = markups.choose_old_layout(patches))
            bot.register_next_step_handler(msg, avg_rating)  

        elif message.text in patches:

            response = sorted(json.loads(requests.request("GET", f'{API_URL}/total_avg_per_special_version?version={message.text}').text),
                    key=lambda d: d['avg'], reverse=False)

            line = f"Лидер по среднему рейтинга патча {response[0].get('bg_version')} - {response[0].get('v_name')}, со средним местом - {format(response[0].get('avg'), '.2f')}"

            cnt = 0

            for person in response:

                cnt = cnt + 1

                if person.get('v_name') == response[0].get('v_name'): 
                    continue

                line = line + f"\n{cnt}. {person.get('v_name')}, со средним местом - {format(person.get('avg'), '.2f')}"

            bot.send_message(message.chat.id, line, reply_markup = markups.markup_layout())

            patches.clear()

    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)


def weekly_agenda(message):

    try:

        if message.text == "По местам":

            for i in range(1,9):
            
                response = sorted(json.loads(requests.request("GET", f'{API_URL}/weekly_place?place={i}').text),
                                    key=lambda d: d['count'], reverse=True)

                if response[0].get('count') in (2,3,4):

                    bot.send_message(message.chat.id, f"{i}. {response[0].get('v_name')} - {response[0].get('count')} разa топ-{i}")
    
                else:

                    bot.send_message(message.chat.id, f"{i}. {response[0].get('v_name')} - {response[0].get('count')} раз топ-{i}", reply_markup = markups.markup_layout())

        elif message.text == "По среднему рейтингу":

            response = sorted(json.loads(requests.request("GET", f'{API_URL}/weekly_avg').text),
                                    key=lambda d: d['avg'])

            bot.send_message(message.chat.id, f"Лидер по среднему рейтинга - {response[0].get('v_name')}, со средним местом - {format(response[0].get('avg'), '.2f')}", reply_markup = markups.markup_layout())    

            cnt = 0

            for line in response:

                cnt = cnt + 1
                    
                if line.get('v_name') == response[0].get('v_name'):
                    continue
           
                bot.send_message(message.chat.id, f"{cnt}. {line.get('v_name')}, среднее место - {format(line.get('avg'), '.2f')}")

        elif message.text == "По количеству игр":

            response = sorted(json.loads(requests.request("GET", f'{API_URL}/weekly_games').text),
                                    key=lambda d: d['count'], reverse=True)
            print(response)
            bot.send_message(message.chat.id, f"{1}. {response[0].get('v_name')} сыграл {response[0].get('count')} игр", reply_markup = markups.markup_layout())
            cnt = 0

            for line in response:

                cnt = cnt + 1

                if line.get('v_name') == response[0].get('v_name'):

                    continue

                bot.send_message(message.chat.id, f"{cnt}. {line.get('v_name')} сыграл {line.get('count')} игр")

        elif message.text == "Назад":

            bot.send_message(message.chat.id, f"Главное меню", reply_markup = markups.markup_layout())

        else:

            bot.reply_to(message, 'Что-то пошло не так', reply_markup = markups.markup_layout())

 
    except Exception as e:
        
       bot.reply_to(message, 'oooops')
       logger.error(e)



def bg_rating(message):

    try:

        if message.text == 'По топ-1':

            response = sorted(json.loads(requests.request("GET", f'{API_URL}/total_top_place?place=1').text),
                                    key=lambda d: d['count'], reverse=True)
            
            bot.send_message(message.chat.id,
                            f"Лидер рейтинга по топ-1 - {response[0].get('v_name')}, занял топ-1 - {response[0].get('count')}", reply_markup = markups.markup_layout())

            cnt = 0

            for line in response:
                
                cnt = cnt + 1

                if line.get('v_name') == response[0].get('v_name'):

                    continue

                bot.send_message(message.chat.id, f"{cnt}. {line.get('v_name')}, занял топ-1 - {line.get('count')} раз")

        elif message.text == 'По среднему рейтингу':

            msg = bot.reply_to(message, "Выберете интересующий вас патч", reply_markup = markups.choose_layout())
            bot.register_next_step_handler(msg, avg_rating)       

        elif message.text == 'По периодичности места':

            msg = bot.reply_to(message, "Выберете интересующее вас место", reply_markup = markups.bg_markup_layout())
            bot.register_next_step_handler(msg, bg_period_rating)

        elif message.text == 'Антирейтинг':
            
            response = sorted(json.loads(requests.request("GET", f'{API_URL}/total_top_place?place=8').text),
                                    key=lambda d: d['count'], reverse=True)
            
            bot.send_message(message.chat.id,
                            f"Лидер рейтинга по топ-8 - {response[0].get('v_name')}, занял топ-8 - {response[0].get('count')}", reply_markup = markups.markup_layout())

            cnt = 0

            for line in response:
                
                cnt = cnt + 1

                if line.get('v_name') == response[0].get('v_name'):

                    continue

                bot.send_message(message.chat.id, f"{cnt}. {line.get('v_name')}, занял топ-8 - {line.get('count')} раз")

        elif message.text == 'Сыграно игр':

            response = sorted(json.loads(requests.request("GET", f'{API_URL}/total_games').text),
                                    key=lambda d: d['count'], reverse=True)
            
            bot.send_message(message.chat.id, f"1. {response[0].get('v_name')} сыграл {response[0].get('count')} игр", reply_markup = markups.markup_layout())
            cnt = 0

            for line in response:

                cnt = cnt + 1

                if line.get('v_name') == response[0].get('v_name'): 
                    continue

                bot.send_message(message.chat.id, f"{cnt}. {line.get('v_name')} сыграл {line.get('count')} игр")

        elif message.text == 'Назад':
            bot.send_message(message.chat.id, "Главное меню", reply_markup = markups.markup_layout())

    except Exception as e:
        bot.reply_to(message, 'oooops')
        logger.error(e)



def bg_period_rating(message):

    try:

        response = sorted(json.loads(requests.request("GET", f'{API_URL}/total_period?place={message.text}').text),
                                    key=lambda d: d['count'])
            
        bot.send_message(message.chat.id,
                        f"Лидер рейтинга периодичности топ-{message.text} - {response[0].get('v_name')}, с топ-{message.text} каждую {format(response[0].get('count'), '.2f')} игру", reply_markup = markups.markup_layout())

        cnt = 0

        for line in response:
                
            cnt = cnt + 1

            if line.get('v_name') == response[0].get('v_name'):

                continue

            bot.send_message(message.chat.id, f"{cnt}. {line.get('v_name')}, с топ-{message.text} каждую {format(line.get('count'), '.2f')} игру")

    except:
        bot.reply_to(message, 'oooops')
        logger.error(e)


def hs_bg_places(message):

    try:

        add_place(message)
        
    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)

def new_idea(message):

    try:

        f = open('/home/dr/obsidian/Dr/BG_bot.md', 'r')
        lines = f.readlines()

        do = lines.index('## Do\n')

        f.close()
        lines.insert(do + 1, f'- {message.text}\n')

        f = open('/home/dr/obsidian/Dr/BG_bot.md', 'w')
        f.writelines(lines)

        f.close()

        bot.send_message(message.chat.id, 'Добавлено !')
        logger.info(f'Пользователь {message.from_user.first_name} добавил идею {message.text} !')

    except Exception as e:

        bot.reply_to(message, 'oooops')
        logger.error(e)


bot.remove_webhook()

bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

logger.info("Launched !")

web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=8443,
    ssl_context=context,
)

logger.info("Stopped !")
