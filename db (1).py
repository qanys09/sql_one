import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# 05 Подключение из Python
# 1. Реализуйте connect_db в db.py с загрузкой .env рядом с файлом.
# 2. Подключитесь через Psycopg 3 с dict_row и выполните 
# SELECT 1 AS result.
# 3. При отсутствии DATABASE_URL выдайте понятную ошибку.
# Закройте соединение через with.

def connect_db():
    load_dotenv(Path(__file__).with_name(".env"))
    url = os.getenv("DATABASE_URL")
    if not url:
        return ValueError("Добавьте DATABASE_URL в .env")
    return psycopg2.connect(url, connect_timeout=15 )
    

with connect_db() as conn, conn.cursor() as cur:
    cur.execute("SELECT 1 AS result")
    print(cur.fetchone()[0])


connect_db()


# 06 Список дронов
# 1. Подготовьте образец готовым импортом из README один раз.
# 2. Реализуйте list_drones с полями id, name, model и порядком по id.
# 3. Верните список словарей. Для пустой таблицы допустим пустой список.


def list_drones():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, model FROM drones ORDER BY id')
            return cur.fetchall()

# 07 Новый дрон с необычным именем
# 1. Реализуйте add_drone с параметрами name и model.
# 2. Уберите пробелы по краям, отклоните пустые значения, верните созданный ID.
# 3. Передайте значения отдельно от SQL. Проверьте имя Дрон O'Brien и обработайте повтор имени в меню.


def add_drone(name, model):
    if not isinstance(name, str) or not isinstance(model, str):
        raise ValueError('Имя и модель должны быть строками')
    name = name.strip()
    model = model.strip()
    if not name or not model:
        raise ValueError('Имя и модель дрона не могут быть пустыми')

    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO drones (name, model) VALUES (%s, %s) RETURNING id',
                    (name, model),
                )
                return cur.fetchone()['id']
    except errors.UniqueViolation as exc:
        raise ValueError(f'Дрон с именем {name!r} уже существует') from exc
# 08 Понятный журнал
# 1. Реализуйте list_deliveries через JOIN, показывая имя дрона вместо одного drone_id.
# 2. Верните id доставки, drone, cargo, price, status с сортировкой по id доставки.
# 3. На неизменённом образце должно быть шесть строк, без случайных повторов от неверного соединения.

def list_deliveries():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT d.id, dr.name AS drone, d.cargo, d.price, d.status
                FROM deliveries AS d
                JOIN drones AS dr ON dr.id = d.drone_id
                ORDER BY d.id
            ''')
            return cur.fetchall()

# 09 Срочная посылка
# 1. Реализуйте add_delivery с ID существующего дрона, грузом и целой неотрицательной стоимостью.
# 2. Новая заявка должна получать ready из DEFAULT. Верните её ID.
# 3. Проверьте отрицательную цену, пустой груз и неизвестный ID дрона. Исходные заявки не изменяйте.

def add_delivery(drone_id, cargo, price):
    if type(drone_id) is not int or drone_id <= 0:
        raise ValueError('ID дрона должен быть положительным целым числом')
    if not isinstance(cargo, str) or not cargo.strip():
        raise ValueError('Груз не может быть пустым')
    if type(price) is not int or price < 0:
        raise ValueError('Стоимость должна быть целым неотрицательным числом')

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM drones WHERE id = %s', (drone_id,))
            if cur.fetchone() is None:
                raise ValueError(f'Дрон с ID {drone_id} не найден')
            try:
                cur.execute('''
                    INSERT INTO deliveries (drone_id, cargo, price)
                    VALUES (%s, %s, %s)
                    RETURNING id
                ''', (drone_id, cargo.strip(), price))
            except errors.ForeignKeyViolation as exc:
                raise ValueError(f'Дрон с ID {drone_id} не найден') from exc
            return cur.fetchone()['id']


if __name__ == '__main__':
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT 1 AS result')
            print('Проверка подключения:', cur.fetchone()['result'])

    print('Дроны:', list_drones())
    print('Доставки:', list_deliveries())