import telebot

def markup_layout():

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("1")
    item2 = telebot.types.KeyboardButton("2")
    item3 = telebot.types.KeyboardButton("3")
    item4 = telebot.types.KeyboardButton("4")
    item5 = telebot.types.KeyboardButton("5")
    item6 = telebot.types.KeyboardButton("6")
    item7 = telebot.types.KeyboardButton("7")
    item8 = telebot.types.KeyboardButton("8")
    item9 = telebot.types.KeyboardButton("Личная статистика")
    item10 = telebot.types.KeyboardButton("Удалить запись")
    item11 = telebot.types.KeyboardButton("Последние 10 игр")
    item12 = telebot.types.KeyboardButton("Рейтинги")
    item13 = telebot.types.KeyboardButton("Еженедельная сводка")
    item14 = telebot.types.KeyboardButton("Другое")
    markup.row(item1, item2, item3, item4, item5, item6, item7, item8)
    markup.row(item9)
    markup.row(item13, item12)
    markup.row(item10, item11)
    markup.row(item14)
    return markup


def personal_layout():

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    item1 = telebot.types.KeyboardButton("Среднее место по патчам")
    item2 = telebot.types.KeyboardButton("Итоговых мест")

    markup.row(item1)
    markup.row(item2)
    markup.row(telebot.types.KeyboardButton("Назад"))

    return markup


def choose_layout():

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(telebot.types.KeyboardButton("Общий"))
    markup.row(telebot.types.KeyboardButton("Текущий"))
    markup.row(telebot.types.KeyboardButton("Устаревший"))

    markup.row(telebot.types.KeyboardButton("Назад"))

    return markup


def choose_old_layout(patches):

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    for patch in patches:

        markup.row(telebot.types.KeyboardButton(patch))

    markup.row(telebot.types.KeyboardButton("Назад"))

    return markup


def bg_markup_layout():

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1 = telebot.types.KeyboardButton("1")
    item2 = telebot.types.KeyboardButton("2")
    item3 = telebot.types.KeyboardButton("3")
    item4 = telebot.types.KeyboardButton("4")
    item5 = telebot.types.KeyboardButton("5")
    item6 = telebot.types.KeyboardButton("6")
    item7 = telebot.types.KeyboardButton("7")
    item8 = telebot.types.KeyboardButton("8")
    markup.row(item1, item2, item3, item4)
    markup.row(item5, item6, item7, item8)
    markup.row(telebot.types.KeyboardButton("Назад"))
    return markup


def bg_rating_layout():

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1 = telebot.types.KeyboardButton("По топ-1")
    item2 = telebot.types.KeyboardButton("По среднему рейтингу")
    item3 = telebot.types.KeyboardButton("По периодичности места")
    item4 = telebot.types.KeyboardButton("Антирейтинг")
    item5 = telebot.types.KeyboardButton("Сыграно игр")
    markup.row(item1, item4, item5)
    markup.row(item2, item3)
    markup.row(telebot.types.KeyboardButton("Назад"))
    return markup


def weekly_agenda_layout():

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    item1 = telebot.types.KeyboardButton("По среднему рейтингу")
    item2 = telebot.types.KeyboardButton("По местам")
    item3 = telebot.types.KeyboardButton("По количеству игр")
    markup.row(item2, item3)
    markup.row(item1)
    markup.row(telebot.types.KeyboardButton("Назад"))

    return markup


def delete_record_layout(id_records):

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    item1 = telebot.types.KeyboardButton(f"№{id_records[0].get('id_record')}, {id_records[0].get('place')}")
    item2 = telebot.types.KeyboardButton(f"№{id_records[1].get('id_record')}, {id_records[1].get('place')}")
    item3 = telebot.types.KeyboardButton(f"№{id_records[2].get('id_record')}, {id_records[2].get('place')}")
    item4 = telebot.types.KeyboardButton(f"№{id_records[3].get('id_record')}, {id_records[3].get('place')}")
    item5 = telebot.types.KeyboardButton(f"№{id_records[4].get('id_record')}, {id_records[4].get('place')}")
    item6 = telebot.types.KeyboardButton(f"№{id_records[5].get('id_record')}, {id_records[5].get('place')}")
    item7 = telebot.types.KeyboardButton(f"№{id_records[6].get('id_record')}, {id_records[6].get('place')}")
    item8 = telebot.types.KeyboardButton(f"№{id_records[7].get('id_record')}, {id_records[7].get('place')}")
    item9 = telebot.types.KeyboardButton(f"№{id_records[8].get('id_record')}, {id_records[8].get('place')}")
    item0 = telebot.types.KeyboardButton(f"№{id_records[9].get('id_record')}, {id_records[9].get('place')}")

    markup.row(item1, item2, item3, item4, item5)
    markup.row(item6, item7, item8, item9, item0)
    markup.row(telebot.types.KeyboardButton("Назад"))

    return markup

def last_ten_games_layout():

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    item1 =  telebot.types.KeyboardButton("Показать")
    item2 = telebot.types.KeyboardButton("Среднее") 

    markup.row(item1, item2)
    markup.row(telebot.types.KeyboardButton("Назад"))

    return markup

def others_layout():

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    item1 =  telebot.types.KeyboardButton("Добавить идею")
    item2 = telebot.types.KeyboardButton("Рандом") 

    markup.row(item1, item2)
    markup.row(telebot.types.KeyboardButton("Назад"))

    return markup