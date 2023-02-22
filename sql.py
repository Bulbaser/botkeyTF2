import sqlite3
from files.parsing_price_keys_tf2 import tf2lavka

connect = sqlite3.connect('user.db', check_same_thread = False)
cursor = connect.cursor()
# Добавление нового пользователя в базу данных
try:
    def add_user(user_id: int, user_name: str):
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', [user_id])
        data = cursor.fetchone()
        if data is None:
            cursor.execute('INSERT INTO users (user_id, first_name_id, money) VALUES(?, ?, ?);', [user_id, user_name, 0])
            connect.commit()
except sqlite3.ProgrammingError:
    pass

#Работа с админкой
def mess_admin(text):
    cursor.execute('SELECT user_id FROM users')
    row = cursor.fetchall()
    return row

#Просмотр количества пользователей в боте
def stats():
    row = cursor.execute('SELECT user_id FROM users').fetchone()
    amount_user_all = 0
    while row is not None:
        amount_user_all += 1
        row = cursor.fetchone()
    msg = 'Людей которые когда либо заходили в бота:' + str(amount_user_all)
    return msg

# Обновление цен ключей TF2 с сайта tf2lavka
def keys_tf2(buy_keys_tf2, sold_keys_tf2):
    cursor.execute('UPDATE keys SET buy_id = ?, sold_id = ?;', (buy_keys_tf2, sold_keys_tf2))
    connect.commit()
#Просмотр цен ключей
def keyses():
    rbuy = cursor.execute('SELECT buy_id FROM keys').fetchone()[0]
    rsold = cursor.execute('SELECT sold_id FROM keys').fetchone()[0]
    return rbuy, rsold

# Добавление кол-во денег пользователя для вывода
def add_money_user(money: int,user_id: int):
    cursor.execute('UPDATE users SET money = ? WHERE user_id = ?;', [money, user_id])
    connect.commit()
#Просмотр кол-ва денег у пользователя
def see_user_money(user_id):
    money = cursor.execute('SELECT money FROM users WHERE user_id = ?;', [user_id]).fetchone()[0]
    return money
# Удаления баланса юзера с бд, который поставил на вывод
def block(user, money_set):
    money = cursor.execute('SELECT money FROM users WHERE user_id = ?;', [user]).fetchone()[0]
    cursor.execute('UPDATE users SET money = ? WHERE user_id = ?', [money - money_set, user])
    connect.commit()

# Удаление пользователя, который занёс бота в чс
def delete(user):
    cursor.execute('DELETE FROM users WHERE user_id = ?', [user])
    connect.commit()

# Добавление ключей в статистику при покупке
def buyKeys(statsBuy):
    statBuyKeys = cursor.execute('SELECT keysBuy FROM stats').fetchone()[0]
    cursor.execute('UPDATE stats SET keysBuy = ?', [statBuyKeys + statsBuy])
    connect.commit()

# Добавление ключей в статистику при продаже
def soldKeys(statsSold):
    statsSoldKeys = cursor.execute('SELECT keysSold FROM stats').fetchone()[0]
    cursor.execute('UPDATE stats SET keysSold = ?', [statsSold + statsSoldKeys])
    connect.commit()

# Показ статистики в боте через админку
def showStatsInBot():
    sold = cursor.execute('SELECT keysSold FROM stats').fetchone()[0]
    buy = cursor.execute('SELECT keysBuy FROM stats').fetchone()[0]
    return sold, buy