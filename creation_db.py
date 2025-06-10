import psycopg2
PASSWORD = ''
conn = psycopg2.connect(database='ignatev_english_db', user='postgres', password=PASSWORD)


def tables_creation():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id SERIAL PRIMARY KEY,
                word VARCHAR(80),
                part_of_speech VARCHAR(40),
                translation TEXT,
                level VARCHAR (10),
                added_by_user BOOLEAN
                );
        """)
        conn.commit()

        cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY,
                    name VARCHAR(100),
                    surname VARCHAR(100)
                    );
            """)
        cur.execute("""
                    INSERT INTO users
                    VALUES (%s, %s, %s)
                """, (1, 'Creator', 'Creator')
                    )
        conn.commit()

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS words_for_users (
                        user_id INT REFERENCES users(id),
                        word_id INT REFERENCES words(id)
                        );
                """)

        conn.commit()

def fill_db():
    with open('Awords.txt', encoding='UTF-8') as aw:
        for s in aw:
            word = s.split('|')[0]
            part_of_speech = s.split('|')[1]
            translation = s.split('|')[2]
            level = s.split('|')[3]
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO words (word, part_of_speech, translation, level, added_by_user)
                    VALUES (%s, %s, %s, %s, %s)
                """, (word.strip(), part_of_speech.strip(), translation.strip(), level.strip(), '0'))
                conn.commit()

    with open('Bwords.txt', encoding='UTF-8') as aw:
        for s in aw:
            word = s.split('|')[0]
            part_of_speech = s.split('|')[1]
            translation = s.split('|')[2]
            level = s.split('|')[3]
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO words (word, part_of_speech, translation, level, added_by_user)
                    VALUES (%s, %s, %s, %s, %s)
                """, (word.strip(), part_of_speech.strip(), translation.strip(), level.strip(), '0'))
                conn.commit()

    with open('Cwords.txt', encoding='UTF-8') as aw:
        for s in aw:
            word = s.split('|')[0]
            part_of_speech = s.split('|')[1]
            translation = s.split('|')[2]
            level = s.split('|')[3]
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO words (word, part_of_speech, translation, level, added_by_user)
                    VALUES (%s, %s, %s, %s, %s)
                """, (word.strip(), part_of_speech.strip(), translation.strip(), level.strip(), '0'))
                conn.commit()

    with open('Prowords.txt', encoding='UTF-8') as aw:
        for s in aw:
            word = s.split('|')[0]
            part_of_speech = s.split('|')[1]
            translation = s.split('|')[2]
            level = s.split('|')[3]

            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO words (word, part_of_speech, translation, level, added_by_user)
                    VALUES (%s, %s, %s, %s, %s)
                """, (word.strip(), part_of_speech.strip(), translation.strip(), level.strip(), '0'))
                conn.commit()

tables_creation()
fill_db()

conn.close()
