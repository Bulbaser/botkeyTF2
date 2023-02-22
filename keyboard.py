from aiogram import types



#Админ-команды
adminMenu = types.InlineKeyboardMarkup(row_width=1)
adminMenu.add (
    types.InlineKeyboardButton(text = 'Рассылка', callback_data= 'newsLetter'),
    types.InlineKeyboardButton(text = 'Кол-во пользователей', callback_data = 'statsUserInBot'),
    types.InlineKeyboardButton(text = 'Статистика ключей', callback_data = 'keysStats')
)

#Команды пользователя
userMenu = types.InlineKeyboardMarkup(row_width = 3)
userMenu.add (
    types.InlineKeyboardButton('Продать', callback_data= 'sellTf'),
    types.InlineKeyboardButton('Купить', callback_data= 'buyTf'),
    types.InlineKeyboardButton('Количество ключей', callback_data='numberOfKeys'),
    types.InlineKeyboardButton('Помощь', callback_data='helpUsers'),
    types.InlineKeyboardButton('Способы оплаты/перевода', callback_data='paymentSystem'),
    types.InlineKeyboardButton('Информация', callback_data='info'),
    types.InlineKeyboardButton('Цена за 1 ключ', callback_data='pricePerKey')
)

#Команда для вывода
withdrawalOfFunds = types.InlineKeyboardMarkup(row_width = 1)
withdrawalOfFunds.add (
    types.InlineKeyboardButton(text = 'Вывод', callback_data= 'withdraw')
)

#Кнопки бота
userButtonMenu = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard= True)
userButtonMenu.add (
    types.KeyboardButton(text = 'Меню'),
    types.KeyboardButton(text = 'Профиль')
)

paymentChoise = types.ReplyKeyboardMarkup(resize_keyboard=True ,row_width= 2, one_time_keyboard= True)
paymentChoise.add (
    types.KeyboardButton(text = 'Lolz + 5%'),
    types.KeyboardButton(text = 'Qiwi'),
    types.KeyboardButton(text = 'Отмена')
)
def check_code(code, amount, url, total, link):
    checkPayment = types.InlineKeyboardMarkup(row_width=2)
    checkPayment.add (
        types.InlineKeyboardButton('Оплатить', callback_data= 'pay', url=url),
        types.InlineKeyboardButton('Проверить платёж', callback_data=f'pay|{code}|{amount}|{total}|{link}')
)
    return checkPayment

def check_codeQiwi(code, amount, url, total, link):
    checkPayment = types.InlineKeyboardMarkup(row_width=2)
    checkPayment.add (
        types.InlineKeyboardButton('Оплатить', callback_data= 'pay', url=url),
        types.InlineKeyboardButton('Проверить платёж', callback_data=f'payQ|{code}|{amount}|{total}|{link}')
)
    return checkPayment