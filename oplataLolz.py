from lolzapi import LolzteamApi
from files.dannie import lolz_token, id_lolz

api = LolzteamApi(lolz_token, id_lolz)


def check_pay(id_pay, amount):
    if api.market_payments(type_='income', pmin=amount, pmax=amount, comment=id_pay)['payments']:
        return True
