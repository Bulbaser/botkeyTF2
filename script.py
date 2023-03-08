import asyncio
from aiogram import Bot
from sql import *
from files.parsing_inv_steam import inv_steam
from files.parsing_price_keys_tf2 import tf2lavka
import time
from files.dannie import api_tg_bot

bot = Bot(token=api_tg_bot)

async def spam():
    while True:
        try:
            buy, sold = keyses()
            rbuy, rsold = tf2lavka()
            text = mess_admin('12')
            if buy != rbuy or sold != rsold:
                for i in range(len(text)):
                    time.sleep(1)
                    await bot.send_message(text[i][0], f'''Прайсы обновлены :
➕Купить ключи по цене : {float(rbuy)}
➖Продать ключи : {float(rsold)}
🔑Наличие ключей : {inv_steam()} шт''')
                    keys_tf2(rbuy, rsold)
            time.sleep(3600)
        except:
            pass

if __name__ == '__main__':
    asyncio.run(spam())

