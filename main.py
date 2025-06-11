"""
Это телеграм БОТ с привязкой к базе данных.
Работает как викторина с загаданным словом и 4 вариантами ответа.

Слова в базе разбиты по уровням сложности.
Имеется возможность добавлять новые слова в общую базу и в свою.
Удалять слова можно только из своей базы.

"""

import random
import telebot
from telebot import types
import psycopg2

PASSSWORD = ''
TOKEN = ''

bot = telebot.TeleBot(TOKEN)
conn = psycopg2.connect(database='ignatev_english_db', user='postgres', password=PASSSWORD)
emo = [['😉', '😃', '🙃', '😀', '🤩', '☺', '🤗', '🫡', '🤓', '💯', '🤠'],
       ['😟', '😧', '😢', '🥺', '☹', '🙉', '🙈', '🙊', '🧐', '🤕', '🥴']]

levels = ['Новичок(A)', 'Средний(B)', 'Продвинутый(C1)', 'Профессионал(C2)']

# Состояние пользователя сохраняется в словарь states
states = {'user_id':
              {'level':'','words':[],
               'target_word':'',
               'translation':'',
               'other_words':[],
               'step': 0,
               'new_word': '',
               'new_translation': '',
               'new_level': ''}}

menu = ['Добавить слово ➕', 'Удалить слово 🔙', 'Дальше ⏭', 'Сброс 𖣘']


def choose_level(level, id):
    if level == 'Новичок(A)':
        with conn.cursor() as cur:
            cur.execute(f"""
                    SELECT word, translation FROM words w RIGHT JOIN words_for_users wu
                    ON w.id = wu.word_id                
                    WHERE w.level LIKE '%A%' AND wu.user_id = {id}
                    ORDER BY RANDOM()
                    LIMIT 4
                """)
            conn.commit()
            words = cur.fetchall()
    elif level == 'Средний(B)':
        with conn.cursor() as cur:
            cur.execute(f"""
                    SELECT word, translation FROM words w RIGHT JOIN words_for_users wu
                    ON w.id = wu.word_id
                    WHERE w.level LIKE '%B%' AND wu.user_id = {id}
                    ORDER BY RANDOM()
                    LIMIT 4
                """)
            conn.commit()
            words = cur.fetchall()
    elif level == 'Продвинутый(C1)':
        with conn.cursor() as cur:
            cur.execute(f"""
                    SELECT word, translation FROM words w RIGHT JOIN words_for_users wu
                    ON w.id = wu.word_id
                    WHERE w.level LIKE '%C1%' AND wu.user_id = {id}
                    ORDER BY RANDOM()
                    LIMIT 4
                """)
            conn.commit()
            words = cur.fetchall()
    elif level == 'Профессионал(C2)':
        with conn.cursor() as cur:
            cur.execute(f"""
                    SELECT word, translation FROM words w RIGHT JOIN words_for_users wu
                    ON w.id = wu.word_id
                    WHERE w.level LIKE '%C2%' AND wu.user_id = {id}
                    ORDER BY RANDOM()
                    LIMIT 4
                """)
            conn.commit()
            words = cur.fetchall()
    return words


@bot.message_handler(commands=['старт', 'start', 'начать', 'сброс', 'reset'])
def send_welcome(message):

    global states
    user_id = message.chat.id
    states[user_id] = {'level': '', 'words': [], 'target_word': '',
                            'translation': '', 'other_words': [], 'step': 0}
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM users
        """)
        ids = [tup[0] for tup in cur.fetchall()]

    # Если пользователь новый - создаем для него свою базу слов, которую он будет изменять
    if user_id not in ids:
        with conn.cursor() as cur:
            # Записываем id, имя и фамилию нового пользователя в таблицу users
            cur.execute("""
                INSERT INTO users
                VALUES (%s, %s, %s)
            """, (user_id, message.from_user.first_name, message.from_user.last_name))

            # Наполняем промежуточную таблицу словами из общей базы для конкретного пользователя
            cur.execute("""
                INSERT INTO words_for_users (word_id, user_id)
                SELECT id, '%s' FROM words
                WHERE added_by_user = FALSE
            """, (user_id,))

            conn.commit()

    bot.send_message(message.chat.id,
                     f"""Привет, {message.from_user.first_name}!\nНачнем обучение?)""")
    markup = types.ReplyKeyboardMarkup(row_width=2)
    level_btns = [types.KeyboardButton(level) for level in levels]
    markup.add(*level_btns)
    bot.send_message(message.chat.id, "Выбери уровень сложности:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Сброс 𖣘')
def reset(message):
    send_welcome(message)

@bot.message_handler(func=lambda m: True)
def pick_words(message):
    user_id = message.chat.id
    global states

    # Если пользователь еще не выбрал уровень и не вводит его:
    if states[user_id]['step'] == 0 and message.text not in levels:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        level_btns = [types.KeyboardButton(level) for level in levels]
        markup.add(*level_btns)
        bot.send_message(message.chat.id, "Не распознано.\n"
                                          "Выберите уровень из предложенных:",
                         reply_markup=markup)

    elif message.text in levels:
        states[user_id]['level'] = message.text
        states[user_id]['step'] = 1
        bot.send_message(message.chat.id, f"Выбран уровень: {states[user_id]['level']}")

    if message.text.lower() in [k.lower() for k in states[user_id]['other_words']]+[states[user_id]['translation'].lower()]:
        if message.text.lower() == states[user_id]['translation'].lower():
            bot.reply_to(message, f'Верно! {random.choice(emo[0])}')
        else:
            bot.reply_to(message, f"""Неверно! {random.choice(emo[1])} \n"""
                                  f"""Слово "{message.text}" переводится как 
                                  "{dict(states[user_id]['words'])[message.text]}" \n"""
                                  f"""Правильный перевод - "{states[user_id]['translation']}". 
                                  Идем дальше!""")

    if states[user_id]['step'] ==1 and (message.text not in menu or
                                        message.text in ['Дальше ⏭', 'нет ✘']):
        states[user_id]['words'] = choose_level(states[user_id]['level'], id=user_id)
        states[user_id]['target_word'] = states[user_id]['words'][0][1]
        states[user_id]['translation'] = states[user_id]['words'][0][0]
        states[user_id]['other_words'] = [states[user_id]['words'][1][0],
                                          states[user_id]['words'][2][0],
                                          states[user_id]['words'][3][0]
                                          ]

        markup = types.ReplyKeyboardMarkup(row_width=2)
        translation_btn = types.KeyboardButton(states[user_id]['translation'])
        other_words_btns = [types.KeyboardButton(word) for word in states[user_id]['other_words']]
        option_btns = [translation_btn] + other_words_btns
        menu_btns = [types.KeyboardButton(b) for b in menu]
        random.shuffle(option_btns)
        markup.add(*option_btns)
        markup.add(*menu_btns)
        bot.send_message(message.from_user.id,
                         f"""Переведи "{states[user_id]['target_word']}" на английский""",
                         reply_markup=markup)

    # Добавить слово
    if message.text == menu[0]:
        markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, "Какое английское слово вы хотите добавить? \n"
                              "Напечатайте его ...", reply_markup=markup)
        bot.register_next_step_handler(message, add_word)

    # Удалить слово
    if message.text == menu[1]:
        markup = types.ReplyKeyboardRemove()
        bot.send_message(user_id, "Какое английское слово Вы хотите удалить из своей базы? \n"
                                  "Напечатайте его ...", reply_markup=markup)
        bot.register_next_step_handler(message, delete_word)

def add_word(message):
    global states
    user_id = message.chat.id
    states[user_id]['step'] = 2

    # Проверяем что этого слова нет в базе пользователя
    with conn.cursor() as cur:

        cur.execute("""
                    SELECT word
                    FROM words_for_users wu JOIN words w
                    ON wu.word_id = w.id 
                    WHERE user_id = %s AND lower(word) LIKE %s
                """, (user_id, message.text.lower()))
        res = cur.fetchone()
        if res:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            next_btn = types.KeyboardButton(menu[2])
            markup.add(next_btn)
            bot.register_next_step_handler(message, pick_words)
            bot.send_message(user_id, f"Слово {message.text} уже есть в вашей базе",
                             reply_markup=markup)
            states[user_id]['step'] = 1

        # Если слова нет в базе пользователя - добавим его
        else:
            states[user_id]['new_word'] = message.text
            bot.reply_to(message, f"Какой русский перевод у этого слова? \n"
                                  f"Напечатайте его ...")
            bot.register_next_step_handler(message, add_translation)

def add_translation(message):
    global states
    user_id = message.chat.id
    states[user_id]['new_translation'] = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)

    level_btns = [types.KeyboardButton(level) for level in levels]
    markup.add(*level_btns)
    bot.reply_to(message, f"Какого уровня это слово?", reply_markup=markup)
    bot.register_next_step_handler(message, add_level)

def add_level(message):
    global states
    user_id = message.chat.id
    if message.text not in levels and states[user_id]['step'] == 2:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        level_btns = [types.KeyboardButton(level) for level in levels]
        markup.add(*level_btns)
        bot.send_message(message.chat.id, "Не распознано.\n"
                                          "Выберите уровень из предложенных:",
                         reply_markup=markup)
        bot.register_next_step_handler(message, add_level)

    else:
        if message.text == 'Новичок(A)' or message.text == 'Средний(B)':
            states[user_id]['new_level'] = str(message.text[-2])+'2'
        elif message.text == 'Продвинутый(C1)' or message.text == 'Профессионал(C2)':
            states[user_id]['new_level'] = message.text[-3:-1]
        markup = types.ReplyKeyboardMarkup(row_width=2)
        options = ['да ✔', 'нет ✘']
        option_btns = [types.KeyboardButton(o) for o in options]
        markup.add(*option_btns)
        bot.send_message(message.chat.id,
                         f"""Сохранить слово "{states[user_id]['new_word']}"\n"""
                            f"""с переводом "{states[user_id]['new_translation']}"\n"""
                            f"""уровня {states[user_id]['new_level']}?""",
                         reply_markup=markup)
        bot.register_next_step_handler(message, confirm)

def confirm(message):

    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    next_btn = types.KeyboardButton(menu[2])
    markup.add(next_btn)
    if message.text == 'да ✔':
        with conn.cursor() as cur:
            cur.execute("""
                SELECT word FROM words WHERE lower(word) LIKE %s            
            """, (states[user_id]['new_word'].lower(), ))

            if cur.rowcount == 0:
                cur.execute("""
                    INSERT INTO words (word, translation, level, added_by_user)
                    VALUES (%s, %s, %s, True)
                """, (states[user_id]['new_word'],
                      states[user_id]['new_translation'],
                      states[user_id]['new_level']))

                cur.execute("""
                    INSERT INTO words_for_users
                    VALUES (%s, (SELECT id FROM words WHERE word LIKE %s))
                """, (user_id, states[user_id]['new_word']))
                conn.commit()

            else:
                cur.execute("""
                    SELECT translation FROM words WHERE lower(word) LIKE %s
                """, (states[user_id]['new_word'].lower(),))
                translation = cur.fetchone()[0]
                bot.send_message(user_id, f"""Слово {states[user_id]['new_word']}
                                                уже есть в общей базе.\n
                                                Его перевод - "{translation}"\n
                                                Теперь оно есть и в вашей)""")
                cur.execute("""
                    INSERT INTO words_for_users
                    VALUES (%s, (SELECT id FROM words WHERE word LIKE %s))
                """, (user_id, states[user_id]['new_word']))
                conn.commit()

        bot.send_message(user_id, f"Слово {states[user_id]['new_word']} сохранено",
                         reply_markup=markup)
        states[user_id]['step'] = 1
        bot.register_next_step_handler(message, pick_words)
    elif message.text == 'нет ✘':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        next_btn = types.KeyboardButton(menu[2])
        markup.add(next_btn)
        bot.send_message(user_id, 'Сохранение отменено', reply_markup=markup)
        states[user_id]['step'] = 1
        bot.register_next_step_handler(message, pick_words)
    else:
        bot.send_message(user_id, 'Команда не распознана')
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        options = ['да ✔', 'нет ✘']
        option_btns = [types.KeyboardButton(o) for o in options]
        markup.add(*option_btns)
        bot.send_message(message.chat.id,
                         f"""Сохранить слово "{states[user_id]['new_word']}"\n"""
                         f"""с переводом "{states[user_id]['new_translation']}"\n"""
                         f"""уровня {states[user_id]['new_level']}?""",
                         reply_markup=markup)
        bot.register_next_step_handler(message, confirm)

def delete_word(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    next_btn = types.KeyboardButton(menu[2])
    markup.add(next_btn)
    with conn.cursor() as cur:

        cur.execute("""
            DELETE FROM words_for_users
            WHERE user_id = %s AND word_id = (SELECT id FROM words
                WHERE lower(word) LIKE %s 
            )
        """, (user_id, message.text.lower()))
        conn.commit()
        deleted_rows = cur.rowcount
        if deleted_rows == 0:
            bot.register_next_step_handler(message, pick_words)
            bot.send_message(user_id, f"""Слова "{message.text}" нет в вашей базе""",
                             reply_markup=markup)
        else:
            bot.register_next_step_handler(message, pick_words)
            bot.send_message(user_id, f"""Слово "{message.text}" удалено из вашей базы""",
                             reply_markup=markup)


if __name__ == '__main__':
    print('Бот запущен!')
    bot.polling()
