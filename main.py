import schedule
import telebot
import json
from telebot import types
import info_to_course
import requests
import random
from datetime import datetime
import threading
import time

# Token нашего бота
bot = telebot.TeleBot("7163981394:AAHjvJx0lL32TDWOCRaLkove42L1KFl3hWo")
type_game = False
# Константные значения
GIPHY_TOKEN = 'XRfycODPWFq9xjduMF6BxaqibbVgVDtN'

HELP = '''
Список команд:
/start - первый запуск
/help - основные команды
/Mini_game - мини игра
/rules_mini_game - правила мини игры
/Course - курсы валют
/find_gif - получить гифку
/registration - регистрация в приложение
/Magic - чудо

У бота можно спросить:
"Сколько времени?"
'''
tutorial_game = "Данная игра является наподобие Wordle. " \
                "Основная цель игры — угадать спрятанное слово за n попыток. " \
                "В каждую строку нужно ввести любое слово длины n, " \
                "чтобы узнать, какие буквы есть в искомом слове. " \
                "В зависимости от того, какое слово вы ввели, буквы будут выделены тремя цветами. " \
                "Чтобы выйти игры напишите 'Я всё'"


@bot.message_handler(commands=['Magic'])
def start_handler(message):
    linkss = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    bot.send_message(message.chat.id,linkss)


# Приветсвие с ботом
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, "Здравствуйте, данный бот представляет из себя онлайн-банк")


# Узнать какие команды существуют у бота
@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.reply_to(message, HELP)


# Библиотека всех пользователей
@bot.message_handler(commands=['library'])
def all_users(message):
    with open("User_info.json", "r") as my_file:
        User_info_json = my_file.read()
    User_info = json.loads(User_info_json)
    print(User_info)


# Курсы валют
@bot.message_handler(commands=['Course'])
def take_course(message):
    markup = types.InlineKeyboardMarkup()
    btn_ten = types.InlineKeyboardButton(text="Тенге", callback_data="course_tg")
    btn_byn = types.InlineKeyboardButton(text="Белорусский рубль", callback_data="course_byn")
    btn_dol = types.InlineKeyboardButton(text="Доллар", callback_data="course_dol")
    btn_euro = types.InlineKeyboardButton(text="Евро", callback_data="course_euro")
    markup.row(btn_ten, btn_byn)
    markup.row(btn_dol, btn_euro)
    bot.send_message(message.from_user.id, "Выберите валюту", reply_markup=markup)


# Кнопочки для выбора валюты
@bot.callback_query_handler(func=lambda call: "course" in call.data)
def course_callback(call):
    if call.data == "course_tg":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Курс тенге: {info_to_course.convert_kzt()}")
    if call.data == "course_byn":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Курс белорусского рубля : {info_to_course.convert_byn()}")
    if call.data == "course_dol":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Курс доллара : {info_to_course.convert_usd_euro(1)}")
    if call.data == "course_euro":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Курс евро : {info_to_course.convert_usd_euro(2)}")


ans = ''


# Запуск мини игры
@bot.message_handler(commands=['Mini_game'])
def begin(message):
    word_url = 'https://itoven-ai.co/images/words.txt'
    r = requests.get(word_url)
    soup = r.text.split()
    global ans
    ans = str(random.choice(soup)).lower()
    bot.reply_to(message, f"Длина слова {len(ans)}")
    bot.register_next_step_handler(message, play_game)


# Логика игры
def play_game(message):
    if message.text == 'я всё':
        bot.reply_to(message, "Спасибо что поиграли в мою игру")
        return
    if len(message.text) != len(ans):
        bot.reply_to(message, f"Введити слово длины {len(ans)}")
        bot.register_next_step_handler(message, play_game)
        return
    check_ans = ['🟩'] * 100
    s = message.text
    s = list(s)
    k = [''] * len(ans)
    for j in range(len(s)):
        if (ans[j] == s[j]):
            k[j] = '🟩'
            s[j] = '-'
    for j in range(len(s)):
        if (s[j] == '-'):
            continue
        for ii in range(len(ans)):
            if (ans[ii] == s[j]):
                k[j] = '🟨'
                s[j] = '-'
    for j in range(len(s)):
        if (s[j] == '-'):
            continue
        else:
            k[j] = '🟥'
    ok = 0
    for j in range(len(k)):
        if (k[j] != check_ans[j]):
            ok = 1
            break
    if (ok == 0):
        bot.reply_to(message, f"Вы угадали слово {ans}")
        return
    else:
        k = str(k)
        bot.reply_to(message, k)
        bot.register_next_step_handler(message, play_game)


# правила мини игры
@bot.message_handler(commands=['rules_mini_game'])
def rules(message):
    bot.reply_to(message, tutorial_game)


# регистрация
@bot.message_handler(commands=['registration'])
def registration_handler(message):
    if check_client_in_db(message.from_user.id):
        bot.send_message(message.from_user.id, "Вы уже зарегистрированы")
    else:
        bot.send_message(message.from_user.id, "Введите ваше имя:")
        bot.register_next_step_handler(message, name)


# ввод имени пользователя
def name(message):
    global client
    client = {"id": message.from_user.id, "name": message.text}
    bot.send_message(message.chat.id, "Введите вашу фамилию:")
    bot.register_next_step_handler(message, surname)


# ввод фамилии пользователя
def surname(message):
    client["surname"] = message.text
    bot.send_message(message.from_user.id, "Введите вашу почту:")
    bot.register_next_step_handler(message, balance)


# ввод суммы вложения
def balance(message):
    client["balance"] = message.text
    bot.send_message(message.from_user.id, "Сумму которую хотите внести")
    bot.register_next_step_handler(message, email)


# ввод почты пользователя
def email(message):
    client["email"] = message.text
    save_client_info()
    bot.send_message(message.from_user.id, f"Спасибо, мы сохранили ваши данные.\n {str(client)}")


# добавление пользователя в базу данных
def save_client_info():
    # Сначала загружаем уже известные данные
    with open('data.txt') as f:
        data = json.load(f)

    data.append(client)

    with open('data.txt', "w") as f:
        json.dump(data, f)
        print("Данные обновлены")


# проверка на то что действительно пользователь существует
def check_client_in_db(id):
    with open('data.txt') as f:
        data = json.load(f)
        for i in data:
            if i["id"] == id:
                return True
    return False


# Получение гифки
def get_gif_by_name(name):
    """Функция, которая получает одну гифку по поиску"""

    url = "http://api.giphy.com/v1/gifs/search"

    param = {
        "api_key": GIPHY_TOKEN,
        "rating": "g",
        "q": name,
        "limit": 1,
        "lang": "ru"
    }

    result = requests.get(url, params=param)
    result_dict = result.json()
    # print(json.dumps(result_dict, sort_keys=True, indent=4))
    link_origin = result_dict["data"][0]["images"]["original"]["url"]

    return link_origin


# Поиск гифки
@bot.message_handler(commands=['find_gif'])
def find_gif_handler(message):
    """Обработчик команды find_gif"""
    bot.send_message(message.from_user.id, "Введите слово или словосочетание для поиска")
    bot.register_next_step_handler(message, get_find_name)


# Поиск по имени гифки
def get_find_name(message):
    """Обработчик поиска для гифки"""
    bot.send_message(message.from_user.id, f"Вот ваша гифка:")
    link = get_gif_by_name(message.text)
    bot.send_animation(message.from_user.id, link)


# вывод рандомного изображения
def get_random_image_url():
    response = requests.get("https://source.unsplash.com/random")
    if response.status_code == 200:
        return response.url
    return 1


def get_subscribes_id_list():
    """Получаем список id зарегистрированных"""
    with open('data.txt') as f:
        data = json.load(f)
        result_id = []
        for i in data:
            result_id.append(i["id"])

    return result_id


def send_random_gif_at_18_00(bot):
    """Планировщик для отправки сообщений по времени"""

    def send_gif():
        """Функция для отправки сообщения"""

        for client_id in get_subscribes_id_list():
            bot.send_message(client_id, get_random_image_url())

    schedule.every(12).hours.do(send_gif)

    while True:
        schedule.run_pending()
        time.sleep(1)


thread_scheduler = threading.Thread(target=send_random_gif_at_18_00, args=(bot,))
thread_scheduler.start()


# Узнать сколько времени
@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    if text == "сколько времени?":
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        bot.send_message(message.chat.id, current_time)


bot.infinity_polling()
