import time
import requests
import logging
from files.steam_auto import session, steam_client
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.coantrib.fsm_storage.memory import MemoryStorage
from sql import *
import keyboard
from files.parsing_inv_steam import inv_steam
from steampy.utils import GameOptions
from steampy.client import Asset
from SimpleQIWI import *
from files.dannie import *
from steampy.exceptions import ApiException, InvalidCredentials
from SimpleQIWI import QIWIAPIError
from generator import gener
from lolzapi import LolzteamApi
from oplataLolz import check_pay
from oplataQiwi import checkQiwi

api_lolz = LolzteamApi(lolz_token, id_lolz)


# FSM состояние
class send(StatesGroup):
    buyKeysQiwi = State()
    buyKeysLolz = State()
    sellKeys = State()
    newsLetter = State()
    withdrawalOfMoney = State()
    payment = State()
    nextBuyTf = State()
    nextBuyQiwiTf = State()


bot = Bot(token=api_tg_bot)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(
    format="%(levelname)-8s [%(asctime)s]  %(message)s", level=logging.INFO
)


# Команда /start
@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(
        f"Добро пожаловать, {message.from_user.username}",
        reply_markup=keyboard.userButtonMenu,
    )


# Команда /admin
@dp.message_handler(commands="admin")
async def admin(message: types.Message):
    if message.from_user.id == int("878562927") or message.from_user.id == int(
        "1059195416"
    ):
        await message.answer(
            f"Привет, {message.from_user.username}. Ты авторизовался в админке",
            reply_markup=keyboard.adminMenu,
        )
    else:
        await message.answer("Не понял команды.")


# Работа с кнопками
@dp.message_handler(content_types="text")
async def main_commands(message: types.Message):
    if message.text == "Профиль":
        await message.answer(
            f"Имя : {message.from_user.username}",
            f"Баланс : {see_user_money(message.from_user.id)}",
            reply_markup=keyboard.withdrawalOfFunds,
        )
    elif message.text == "Меню":
        await message.answer(
            "Покупай/продавай ключи выгодно с нами!", reply_markup=keyboard.userMenu
        )


# Работа с инлайн-клавиатурой
@dp.callback_query_handler(lambda callback_query: True)
async def some_callback_handler(callback_query: types.CallbackQuery):
    if callback_query.data == "withdraw":
        await bot.send_message(
            callback_query.from_user.id,
            text="Введи свой номер телефона QIWI и сумму денег на вывод(Пример : 79999999999 500)",
        )
        await send.withdrawalOfMoney.set()
    elif callback_query.data == "newsLetter":
        await bot.send_message(
            callback_query.from_user.id, text="Введи текст для рассылки :"
        )
        await send.newsLetter.set()
    elif callback_query.data == "statsUserInBot":
        await bot.send_message(callback_query.from_user.id, text=stats())
    elif callback_query.data == "keysStats":
        stats_sold, stats_buy = showStatsInBot()
        await bot.send_message(
            callback_query.from_user.id,
            text=f"""Количество проданных ключей : {stats_sold}
                               Количество купленных ключей : {stats_buy}""",
        )
    elif callback_query.data == "numberOfKeys":
        try:
            await bot.send_message(
                callback_query.from_user.id,
                text=f"На данный момент ключей на продаже: {inv_steam()}",
            )
        except AttributeError:
            await bot.edit_message_text(callback_query.from_user.id, text="Ключей нет")
            logging.error(
                "%s | %s", callback_query.from_user.id, callback_query.message.text
            )
    elif callback_query.data == "helpUsers":
        await bot.send_message(
            callback_query.from_user.id,
            text="Чтобы узнать больше, обратитесь к " "данному админу : @malch2ik",
        )
    elif callback_query.data == "paymentSystem":
        await bot.send_message(
            callback_query.from_user.id,
            text="На данный момент поддерживается только QIWI.",
        )
    elif callback_query.data == "info":
        await bot.send_message(
            callback_query.from_user.id,
            text="""Продажа ключей:
1. Напишите " /start " после нажмите на кнопку < Продать >
2. Отправьте обмен по трейду которому пришлет вам бот
3. Пришлите сообщение боту слово " Готово "
4. После вы получите сообщение с информацией о статусе приёма ключей, а так же поступление денег в профиль.

Покупка ключей через Qiwi:
1. Напишите " /start " после нажмите на кнопку < Купить >
2. В ответ бот пришлёт сколько ключей на данный момент в наличий и попросит вас указать trade-link и (кол-во ключей) - пример "trade(ваша ссылка на обмен) 10(количество сколько вы хотите купить)"
3. В ответ бот вам пришлет информацию для оплаты
4. При получении платежа бот автоматически вышлет вам обмен с ключами.""",
        )
    elif callback_query.data == "pricePerKey":
        buy, sold = keyses()
        await bot.send_message(
            callback_query.from_user.id,
            text=f"""Купить ключи за {buy} Р/шт
Продать ключи за {sold} Р/шт""",
        )
    elif callback_query.data == "sellTf":
        await bot.send_message(
            callback_query.from_user.id,
            text=f"""Предложите обмен, с выбранными ключами для продажи
https://steamcommunity.com/tradeoffer/new/?partner=1056147551&token=LX8mR5Jd и в комментарии укажите *{gener()}* 
После того как вы отправили обмен, подтвердили трейд, отправьте после этого сообщения слово *Готово*, в ином случае 
вам придется делать процедуру заново""",
            parse_mode="Markdown",
        )
        await send.sellKeys.set()
    elif callback_query.data == "buyTf":
        await bot.send_message(
            callback_query.from_user.id,
            "Выберите метод оплаты",
            reply_markup=keyboard.paymentChoise,
        )
        await send.payment.set()
    elif callback_query.data.startswith("pay|"):
        await buyTfLolz(callback_query.data, callback_query)
    elif callback_query.data.startswith("payQ|"):
        await buyTfQiwi(callback_query.data, callback_query)


# Продажа ключей
@dp.message_handler(state=send.sellKeys)
async def sellTf(message: types.Message, state: FSMContext):
    await send.sellKeys.set()
    try:
        buy, sold = keyses()
        text_user = message.text
        if text_user.lower() == "готово":
            if session:
                url = f"https://api.steampowered.com/IEconService/GetTradeOffers/v1/?key={api_steam}&get_received_offers=1"
                response = requests.get(url)
                data = response.json()["response"]["trade_offers_received"]
                for i in data:
                    total = 0
                    if i["message"] == gener():
                        if "items_to_receive" in i:
                            for j in range(len(i["items_to_receive"])):
                                if i["items_to_receive"][0]["classid"] == "101785959":
                                    total += 1
                                    if total == len(i["items_to_receive"]):
                                        steam_trade_offer = i["tradeofferid"]
                                        kolvo_keys_TF2 = len(i["items_to_receive"])
                                        total_price = len(i["items_to_receive"]) * sold
                                        steam_client.accept_trade_offer(
                                            steam_trade_offer
                                        )
                                        time.sleep(3)
                                        await bot.send_message(
                                            message.from_user.id,
                                            f"Ваши ключи в количестве {total} были приняты, ожидайте пополнения баланса в профиле",
                                        )
                                        add_money_user(
                                            total_price, message.from_user.id
                                        )
                                        buyKeys(int(total))
                                        await bot.send_message(
                                            "878562927",
                                            f"{message.from_user.first_name}({message.from_user.id}) купил ключи в количестве {kolvo_keys_TF2}"
                                            f"штук за {total_price} рублей.",
                                        )
                                        await bot.send_message(
                                            message.from_user.id,
                                            "Денежные средства были успешно добавлены в профиль. "
                                            "Для вывода зайдите в свой профиль, и запросите вывод "
                                            "средств",
                                        )
                                        await bot.send_message(
                                            message.from_user.id,
                                            """Спасибо за покупку/продажу, 
                                        будем рады вам снова! Оставьте отзыв в нашей теме : 
                                        https://lolz.guru/threads/3443335/ Это помогает наш ему развитию, 
                                        спасибо вам!""",
                                        )
                                        break
                                else:
                                    await bot.send_message(
                                        message.from_user.id,
                                        "В трейде обнаружены лишние вещи, трейд был отменен, "
                                        "сделайте процедуру заново, будьте внимательны",
                                    )
                                    steam_client.decline_trade_offer(steam_trade_offer)
                                    break
                    else:
                        await bot.send_message(
                            message.from_user.id,
                            f"Трейда с комментарием {gener()} не найдено",
                        )
                        break
            else:
                await bot.send_message(message.from_user.id, "Обратить к тех поддержке")
        else:
            await bot.send_message(
                message.from_user.id, "Вы не ввели слово ГОТОВО, начните заново!"
            )
    except ApiException:
        await bot.send_message(message.from_user.id, "Трейда не найдено")
    except InvalidCredentials:
        await bot.send_message(message.from_user.id, "Неверный tradelink")
    await state.finish()


@dp.message_handler(state=send.payment)
async def choisePay(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.answer("Назад в меню", reply_markup=keyboard.userMenu)
        await state.finish()
    elif message.text == "Lolz + 5%":
        await message.answer(
            "Выбрана оплата через LOLZ", reply_markup=keyboard.userButtonMenu
        )
        try:
            await bot.send_message(
                message.from_user.id, text=f"Ключей в наличии : {inv_steam()}"
            )
            if int(inv_steam()) >= int(1):
                await bot.send_message(
                    message.from_user.id,
                    text="Введите свой трейд url и количество ключей для покупки(Пример : *URL* *5*)",
                    parse_mode="Markdown",
                )
                await send.nextBuyTf.set()
            else:
                await bot.send_message(
                    message.from_user.id,
                    text="К сожалению мы не обладаем ключами для продажи",
                )
        except AttributeError:
            await bot.send_message(message.from_user.id, text="Недостаточно ключей")
            logging.error(f"{message.from_user.id} | {message.text}")
    else:
        await message.answer(
            "Выбрана оплата через QIWI", reply_markup=keyboard.userButtonMenu
        )
        try:
            await bot.send_message(
                message.from_user.id, text=f"Ключей в наличии : {inv_steam()}"
            )
            if int(inv_steam()) >= int(1):
                await bot.send_message(
                    message.from_user.id,
                    text="Введите свой трейд url и количество ключей для покупки(Пример : *URL* *5*)",
                    parse_mode="Markdown",
                )
                await send.nextBuyQiwiTf.set()
            else:
                await bot.send_message(
                    message.from_user.id,
                    text="К сожалению мы не обладаем ключами для продажи",
                )
        except AttributeError:
            await bot.send_message(message.from_user.id, text="Недостаточно ключей")
            logging.error(f"{message.from_user.id} | {message.text}")


@dp.message_handler(state=send.nextBuyTf)
async def nextBuyTf(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.finish()
    try:
        urlSteam = message.text.split()[0]
        if urlSteam.startswith("https://steamcommunity.com/tradeoffer/new/"):
            urlLink = urlSteam[42:]
        else:
            await bot.send_message(message.from_user.id, "Неверная ссылка URL")
        user_lolz = name_lolz
        comment = gener()
        total = message.text.split()[1]
        if int(total) <= int(inv_steam()):
            buy, sold = keyses()
            price = (int(buy) * int(total)) + ((int(buy) * int(total)) * 0.05)
            url = f"https://zelenka.guru/market/balance/transfer?username={user_lolz}&amount={int(price)}&comment={comment}"
            await message.answer(
                f"❗️ Важно! Не меняйте сумму оплаты и комментарий, иначе зачисление не будет произведено!\n\nСсылка "
                f"для оплаты находится ниже 👇",
                reply_markup=keyboard.check_code(
                    comment, int(price), url, total, urlLink
                ),
            )
        else:
            await message.answer(
                f"❗️Ключей в количестве {total} штук у нас нет. Попробуйте меньшее число"
            )
    except ValueError:
        await message.answer("❗️Не правильное кол-во ключей")
    except UnboundLocalError:
        logging.error(f"{message.from_user.id} | {message.text}")


async def buyTfQiwi(call: CallbackQuery, message: types.Message):
    try:
        call_data = call.split("|")
        comment = call_data[1]
        total = call_data[2]
        counter = call_data[3]
        url = "https://steamcommunity.com/tradeoffer/new/" + call_data[4]
        if checkQiwi(comment, total):
            if int(counter) >= 1:
                if session:
                    game = GameOptions.TF2
                    my_items = steam_client.get_my_inventory(game)
                    items_for_trade = []
                    for _, value in my_items.items():
                        if value["classid"] == "101785959":
                            items_for_trade.append(Asset(value["id"], game))
                    steam_client.make_offer_with_url(
                        items_for_trade[: int(counter)], [], url, gener()
                    )
                    time.sleep(3)
                    soldKeys(int(counter))
                    await bot.send_message(message.from_user.id, "Обмен отправлен")
                    await bot.send_message(
                        message.from_user.id,
                        """Спасибо за покупку/продажу, будем рады вам снова!
    Оставьте отзыв в нашей еме : https://lolz.guru/threads/3443335/
    Это помогает нашему разитию, спасибо вам!""",
                    )
                    await bot.delete_message(
                        chat_id=message.from_user.id,
                        message_id=message.message.message_id,
                    )
                    userNameTg = message.from_user.first_name
                    userIdTg = message.from_user.id
                    await bot.send_message(
                        "878562927",
                        f"{userNameTg}({userIdTg}) купил ключи в количестве {int(counter)} штук за {counter} рублей.",
                    )
                else:
                    await bot.send_message(
                        message.from_user.id, "Напишите @malchik код 1"
                    )
            elif int(counter) == 0:
                await bot.send_message(
                    message.from_user.id,
                    "0 ключей купить нельзя. Напишите реальное кол-во ключей для покупки",
                )
        else:
            await bot.send_message(
                message.from_user.id, "❗️ К сожалению ваш платеж не обнаружен"
            )
    except ValueError:
        await bot.send_message(message.from_user.id, "Вы ввели некорректное число!")
        logging.error(f"{message.from_user.id} | {message.text}")
    except QIWIAPIError:
        await bot.send_message(
            message.from_user.id,
            "Входящего платежа не найдено. Проверьте кому вы отправили деньги",
        )
        logging.error(f"{message.from_user.id} | {message.text}")
    except AttributeError:
        await bot.send_message(message.from_user.id, "Нет ключей")
        logging.error(f"{message.from_user.id} | {message.text}")
    except IndexError:
        await bot.send_message(
            message.from_user.id,
            "Прочитай инструкцию, в вспылающем окне, перед отравкой *URL* и *кол-во ключей* и "
            "пробуйте продать ключи ещё раз",
            parse_mode="Markdown",
        )
        logging.error(f"{message.from_user.id} | {message.text}")


# Покупка ключей через LOLZ
async def buyTfLolz(call: CallbackQuery, message: types.Message):
    try:
        call_data = call.split("|")
        comment = call_data[1]
        total = call_data[2]
        counter = call_data[3]
        url = "https://steamcommunity.com/tradeoffer/new/" + call_data[4]
        if check_pay(comment, total):
            await bot.delete_message(
                chat_id=message.from_user.id, message_id=message.message.message_id
            )
            buy, _ = keyses()
            if int(counter) >= 1:
                price = int(counter) * buy
                if session:
                    my_items = steam_client.get_my_inventory(GameOptions.TF2)
                    items_for_trade = []
                    for _, value in my_items.items():
                        if value["classid"] == "101785959":
                            items_for_trade.append(Asset(value["id"], GameOptions.TF2))
                        steam_client.make_offer_with_url(
                            items_for_trade[: int(counter)], [], url, gener()
                        )
                    time.sleep(3)
                    soldKeys(int(counter))
                    await bot.send_message(message.from_user.id, "Обмен отправлен")
                    await bot.send_message(
                        message.from_user.id,
                        """Спасибо за покупку/продажу, будем рады вам снова!
    Оставьте отзыв в нашей еме : https://lolz.guru/threads/3443335/
    Это помогает нашему разитию, спасибо вам!""",
                    )
                    user_name_tg = message.from_user.first_name
                    user_id_tg = message.from_user.id
                    await bot.send_message(
                        "878562927",
                        f"{user_name_tg}({user_id_tg}) купил ключи в количестве "
                        f"{int(counter)} штук за {price} рублей.",
                    )
                else:
                    await bot.send_message(
                        message.from_user.id, "Напишите @malchik код 1"
                    )
            elif int(counter) == 0:
                await bot.send_message(
                    message.from_user.id,
                    "0 ключей купить нельзя. Напишите реальное кол-во ключей для покупки",
                )
        else:
            await bot.send_message(
                message.from_user.id, "❗️ К сожалению ваш платеж не обнаружен"
            )
    except ValueError:
        await bot.send_message(message.from_user.id, "Вы ввели некорректное число!")

    except QIWIAPIError:
        await bot.send_message(
            message.from_user.id,
            "Входящего платежа не найдено. Проверьте кому вы отправили деньги",
        )
        logging.error(f"{message.from_user.id} | {message.text}")
    except AttributeError:
        await bot.send_message(message.from_user.id, "Нет ключей")
        logging.error(f"{message.from_user.id} | {message.text}")
    except IndexError:
        await bot.send_message(
            message.from_user.id,
            "Прочитай инструкцию, в вспылающем окне, перед отравкой *URL* и *кол-во ключей* и "
            "пробуйте продать ключи ещё раз",
            parse_mode="Markdown",
        )
        logging.error(f"{message.from_user.id} | {message.text}")


@dp.message_handler(state=send.nextBuyQiwiTf)
async def nextBuyTf(message: types.Message, state: FSMContext):
    await state.finish()
    try:
        urlSteam = message.text.split()[0]
        if urlSteam.startswith("https://steamcommunity.com/tradeoffer/new/"):
            urlLink = urlSteam[42:]
        else:
            await bot.send_message(message.from_user.id, "Неверная ссылка URL")
        comment = gener()
        total = message.text.split()[1]
        if int(total) <= int(inv_steam()):
            buy, sold = keyses()
            price = (int(buy) * int(total)) + (int(buy) * int(total) * 0.05)
            b = str(float(price))
            sum = int(b[b.find(".") + 1 :])
            url = f"""https://qiwi.com/payment/form/99?amountInteger={int(price)}&amountFraction={sum}&extra['comment']={comment}&extra['account']={phone_qiwi}&currency=643&blocked[0]=account"""
            await message.answer(
                f"❗️ Важно! Не меняйте сумму оплаты и комментарий, иначе зачисление не будет произведено!\n\nСсылка "
                f"для оплаты находится ниже 👇",
                reply_markup=keyboard.check_codeQiwi(
                    comment, price, url, total, urlLink
                ),
            )
        else:
            await message.answer(
                f"❗️Ключей в количестве {total} штук у нас нет. Попробуйте меньшее число"
            )
    except ValueError:
        await message.answer("❗️Не правильное кол-во ключей")
    except:
        logging.error(f"{message.from_user.id} | {message.text}")


# Рассылка сообщений
@dp.message_handler(state=send.newsLetter)
async def newsLetter(message: types.Message, state: FSMContext):
    await send.newsLetter.set()
    text = message.text
    info = mess_admin(text)
    await bot.send_message(message.from_user.id, "Рассылка начата!")
    success_send_email = 0
    fail_send_email = 0
    for i in range(len(info)):
        try:
            time.sleep(1)
            await bot.send_message(info[i][0], str(text))
            success_send_email += 1
        except:
            delete(info[i][0])
            # await bot.send_message(878562927, f'{info[i][0]} заблочил бота')
            fail_send_email += 1
            continue
    await bot.send_message(
        message.from_user.id,
        f"Active users: {success_send_email}" f"Deads users: {fail_send_email}",
    )
    await state.finish()


# Заявка на вывод средств
@dp.message_handler(state=send.withdrawalOfMoney)
async def sellTf(message: types.Message, state: FSMContext):
    try:
        await send.withdrawalOfMoney.set()
        money = see_user_money(message.from_user.id)
        if float(money) < float(message.text.split()[1]):
            await bot.send_message(
                message.from_user.id, "У вас нет столько средств на балансе для вывода"
            )
        else:
            await bot.send_message(
                message.from_user.id,
                f"{message.from_user.username},"
                f" вывод успешно запрошен ожидайте денег от 30 минут до 24 часов",
            )
            await bot.send_message(
                878562927,
                f"Пользователь {message.from_user.id} запросил вывод средств на номер"
                f" {message.text.split()[0]} сумму {message.text.split()[1]}",
            )
            block(message.from_user.id, float(message.text.split()[1]))
        await state.finish()
    except ValueError:
        await bot.send_message(
            message.from_user.id, "Напишите кол-во средств через .\n(Например 499.1)"
        )
    except:
        logging.error(f"{message.from_user.id} | {message.text}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
