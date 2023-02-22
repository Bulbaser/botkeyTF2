from lolzapi import LolzteamApi
from files.dannie import lolzToken, idLolz
api = LolzteamApi(lolzToken, idLolz)

def check_pay(id_pay, amount):
    if api.market_payments(type_='income', pmin=amount, pmax=amount, comment=id_pay)['payments']:
        return True