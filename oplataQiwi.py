import requests
import json
from files.dannie import token_qiwi, phone_qiwi


def checkQiwi(gener, price):
    h = requests.get('https://edge.qiwi.com/payment-history/v1/persons/' + phone_qiwi + '/payments?rows=50',
    headers={'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token_qiwi}'})
    req = json.loads(h.text)
    for i in range(len(req['data'])):
        b = req['data'][i]['comment']
        if req['data'][i]['comment'] == gener:
            a = req['data'][i]['sum']['amount']
            if req['data'][i]['sum']['amount'] == float(price):
                return True