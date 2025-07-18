# Документация Telegram-бота для изучения английских слов

![Ссылка на БОТ](/QR.jpg)

## 📌 Общее описание
Бот предназначен для изучения английских слов через систему викторин. Основные возможности:
- Изучение слов по 4 уровням сложности
- Добавление пользовательских слов
- Удаление слов из личного словаря
- Интерактивный интерфейс с клавиатурой

## 🛠 Технические требования
- Python 3.8+
- Библиотеки:
  - `telebot`
  - `psycopg2`
  - `random`
- База данных PostgreSQL

## 🗄 Структура базы данных
Бот использует 3 таблицы:

1. **words** - хранит словарные карточки:
   ```sql
   CREATE TABLE words (
       id SERIAL PRIMARY KEY,
       word VARCHAR(80),
       part_of_speech VARCHAR(40),
       translation TEXT,
       level VARCHAR(10),
       added_by_user BOOLEAN
   );
2. **users** - информация о пользователях:
   ```sql
   CREATE TABLE words (
       id SERIAL PRIMARY KEY,
       word VARCHAR(80),
       part_of_speech VARCHAR(40),
       translation TEXT,
       level VARCHAR(10),
       added_by_user BOOLEAN
3. **words_for_users** - связь пользователей и слов:
   ```sql
   CREATE TABLE words_for_users (
    user_id INT REFERENCES users(id),
    word_id INT REFERENCES words(id))

## 🚀 Основные команды
Стартовые команды
* /start, /начать - начало работы
* /reset, /сброс - сброс прогресса

## Уровни сложности
Доступно 4 уровня:
1.Новичок (A)
2.Средний (B)
3.Продвинутый (C1)
4.Профессионал (C2)

## 🖥 Интерфейс пользователя
# Главное меню
* Добавить слово ➕ - добавление нового слова
* Удалить слово 🔙 - удаление слова из личного словаря
* Дальше ⏭ - следующий вопрос
* Сброс 𖣘 - сброс текущей сессии

## Процесс обучения
Пользователь выбирает уровень сложности
Бот показывает русское слово и 4 варианта перевода
При правильном ответе - похвала, при ошибке - показ правильного ответа

# ✨ Особенности реализации
## Хранение состояния
Используется глобальный словарь states для хранения:
Выбранного уровня
Текущих слов
Статуса добавления новых слов
Обработка текстовых файлов

## Формирование Базы данных 
Исходные слова загружаются из файлов, сформированных нейросетью:
Awords.txt (новичок)
Bwords.txt (средний)
Cwords.txt (продвинутый)
Prowords.txt (профессионал)

## ⚠️ Ограничения
* Изначально для пользователя доступна большая база слов
* Оригинальная база слов копируется для каждого пользователя при команде /start
* Пользователь может удалить слово только из своей копии базы, но добавляет в обе

## 📝 Пример сессии
Пользователь: /start
Бот: Привет, Иван! Начнем обучение?
Выбери уровень сложности: [Новичок(A)] [Средний(B)]...

Пользователь выбирает "Новичок(A)"
Бот: Переведи "стол" на английский
[table] [chair] [door] [window]

Пользователь выбирает "table"
Бот: Верно! 😃

