import random
from idlelib.run import MyHandler

import telebot
from telebot import types
import psycopg2
# from telebot.states import StatesGroup, State

token = ''
password = ''
bot = telebot.TeleBot(token)
conn = psycopg2.connect(database='ignatev_english_db', user='postgres', password=password)
emo = [['😉', '😃', '🙃', '😀', '🤩', '☺', '🤗', '🫡', '🤓', '💯', '🤠'],
       ['😟', '😧', '😢', '🥺', '☹', '🙉', '🙈', '🙊', '🧐', '🤕', '🥴']]

my_states = {'level':'','words':[], 'target_word':'', 'translation':'', 'other_words':[]}
new_word = {'word': '', 'translation': '', 'level': ''}

menu = ['Добавить слово ➕', 'Удалить слово 🔙', 'Дальше ⏭', 'Сброс 𖣘']

def choose_level(level, id):
    user_id = id
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
    user_id = message.chat.id
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM users
        """)
        ids = [tup[0] for tup in cur.fetchall()]
        print(ids)

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

    bot.send_message(message.chat.id, f"""Привет, {message.from_user.first_name}! Начнем обучение?)""")
    markup = types.ReplyKeyboardMarkup(row_width=2)
    levels = ['Новичок(A)', 'Средний(B)', 'Продвинутый(C1)', 'Профессионал(C2)']
    level_btns = [types.KeyboardButton(level) for level in levels]
    markup.add(*level_btns)
    bot.send_message(message.chat.id, "Выбери уровень сложности:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Сброс 𖣘')
def reset(message):
    send_welcome(message)

@bot.message_handler(func=lambda m: True)
def pick_words(message):
    user_id = message.chat.id
    global my_states
    if message.text in ['Новичок(A)', 'Средний(B)', 'Продвинутый(C1)', 'Профессионал(C2)']:
        my_states['level'] = message.text
        bot.send_message(message.chat.id, f"Выбран уровень: {my_states['level']}")
    if message.text in my_states['other_words'] + [my_states['translation']]:
        if message.text == my_states['translation']:
            bot.reply_to(message, f'Верно! {random.choice(emo[0])}')
        else:
            bot.reply_to(message, f"""Неверно! {random.choice(emo[1])} \n"""
                                  f"""Слово "{message.text}" переводится как "{dict(my_states['words'])[message.text]}" \n"""
                                  f"""Правильный перевод - "{my_states['translation']}". Идем дальше!""")
    if message.text not in menu or message.text in ['Дальше ⏭', 'нет ✘']:
        my_states['words'] = choose_level(my_states['level'], id=user_id)
        my_states['target_word'] = my_states['words'][0][1]
        my_states['translation'] = my_states['words'][0][0]
        my_states['other_words'] = [my_states['words'][1][0], my_states['words'][2][0], my_states['words'][3][0]]
        print(my_states['words'])
        markup = types.ReplyKeyboardMarkup(row_width=2)
        translation_btn = types.KeyboardButton(my_states['translation'])
        other_words_btns = [types.KeyboardButton(word) for word in my_states['other_words']]
        option_btns = [translation_btn] + other_words_btns
        menu_btns = [types.KeyboardButton(b) for b in menu]
        random.shuffle(option_btns)
        markup.add(*option_btns)
        markup.add(*menu_btns)
        bot.send_message(message.from_user.id, f"""Переведи "{my_states['target_word']}" на английский""",
                         reply_markup=markup)

    if message.text == menu[0]:
        markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, "Какое английское слово вы хотите добавить? \n"
                              "Напечатайте его ...", reply_markup=markup)
        bot.register_next_step_handler(message, add_word)

    if message.text == menu[1]:
        markup = types.ReplyKeyboardRemove()
        bot.send_message(user_id, "Какое английское слово Вы хотите удалить из своей базы? \n"
                                  "Напечатайте его ...", reply_markup=markup)
        bot.register_next_step_handler(message, delete_word)

def add_word(message):
    global new_word
    user_id = message.chat.id

    # Проверяем что этого слова нет в базе пользователя
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT word
                    FROM words_for_users wu JOIN words w
                    ON wu.word_id = w.id 
                    WHERE user_id = %s AND word LIKE %s
                """, (user_id, message.text))
        res = cur.fetchone()
        if res:
            print('Это слово уже есть в вашей Базе')

        # Если слова нет в базе пользователя - добавим его
        else:
            new_word['word'] = message.text
            bot.reply_to(message, f"Какой русский перевод у этого слова? \n"
                                  f"Напечатайте его ...")
            bot.register_next_step_handler(message, add_translation)

def add_translation(message):
    global new_word
    new_word['translation'] = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    levels = ['Новичок(A)', 'Средний(B)', 'Продвинутый(C1)', 'Профессионал(C2)']
    level_btns = [types.KeyboardButton(level) for level in levels]
    markup.add(*level_btns)
    bot.reply_to(message, f"Какого уровня это слово?", reply_markup=markup)
    bot.register_next_step_handler(message, add_level)

def add_level(message):
    global new_word
    if message.text == 'Новичок(A)' or message.text == 'Средний(B)':
        new_word['level'] = str(message.text[-2])+'2'
    elif message.text == 'Продвинутый(C1)' or message.text == 'Профессионал(C2)':
        new_word['level'] = message.text[-3:-1]
    markup = types.ReplyKeyboardMarkup(row_width=2)
    options = ['да ✔', 'нет ✘']
    option_btns = [types.KeyboardButton(o) for o in options]
    markup.add(*option_btns)
    bot.send_message(message.chat.id, f"""Сохранить слово "{new_word['word']}"\n"""
                                        f"""с переводом "{new_word['translation']}"\n"""
                                        f"""уровня {new_word['level']}?""",
                     reply_markup=markup)
    bot.register_next_step_handler(message, confirm)

def confirm(message):
    global new_word
    user_id = int(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    next_btn = types.KeyboardButton(menu[2])
    markup.add(next_btn)
    if message.text == 'да ✔':
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO words (word, translation, level, added_by_user)
                VALUES (%s, %s, %s, True)
            """, (new_word['word'], new_word['translation'], new_word['level']))

            cur.execute("""
                INSERT INTO words_for_users
                VALUES (%s, (SELECT id FROM words WHERE word LIKE %s))
            """, (user_id, new_word['word']))
        conn.commit()
        bot.register_next_step_handler(message, pick_words)
        bot.send_message(user_id, f"Слово {new_word['word']} сохранено", reply_markup=markup)
    elif message.text == 'нет ✘':
        bot.send_message(user_id, 'Сохранение отменено', reply_markup=markup)
    else:
        bot.send_message(user_id, 'Команда не распознана')
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        options = ['да ✔', 'нет ✘']
        option_btns = [types.KeyboardButton(o) for o in options]
        markup.add(*option_btns)
        bot.send_message(message.chat.id, f"""Сохранить слово "{new_word['word']}"\n"""
                                          f"""с переводом "{new_word['translation']}"\n"""
                                          f"""уровня {new_word['level']}?""",
                         reply_markup=markup)
        bot.register_next_step_handler(message, confirm)

def delete_word(message):
    user_id = message.chat.id
    word = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    next_btn = types.KeyboardButton(menu[2])
    markup.add(next_btn)
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM words_for_users
            WHERE user_id = %s AND word_id = (SELECT id FROM words
                WHERE word LIKE %s AND added_by_user = True
            )
        """, (user_id, word))
        conn.commit()
        deleted_rows = cur.rowcount
        if deleted_rows == 0:
            bot.register_next_step_handler(message, pick_words)
            bot.send_message(user_id, f"""Слова "{word}" нет в вашей базе""", reply_markup=markup)
        else:
            bot.register_next_step_handler(message, pick_words)
            bot.send_message(user_id, f"""Слово "{word}" удалено из вашей базы""", reply_markup=markup)


if __name__ == '__main__':
    print('Бот запущен!')
    bot.polling()