import json
from bs4 import BeautifulSoup
import requests
import re


def tf2lavka():
    try:
        while True:
            slovarCookie = {}
            with open(r'C:\Users\admin\Desktop\projects\refactor bota\files\cookie.json', 'r') as cookie:
                cookieForWork = json.loads(cookie.read())
            for i in cookieForWork:
                slovarCookie[i['name']] = i['value']
            headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.72'
            }
            url_tf2 = "https://tf2lavka.ru"
            a = []
            response = requests.get(url_tf2, headers = headers, cookies= slovarCookie)
            soup = BeautifulSoup(response.text, 'lxml')
            items = soup.find_all('div', class_ = 'col-md-6 srv')
            for i in items:
                pars = i.find('b').text.strip()
                for j in pars.split():
                    a.append(j)
            x = re.findall('[0-9.]+', a[0])
            y = re.findall('[0-9.]+', a[1])
            buy_keys_tf2 = round(float(x[0]) + 4, 2)
            sold_keys_tf2 = round(float(y[0]) - 4, 2)
            return(buy_keys_tf2, sold_keys_tf2)
    except Exception as f:
        print(f)

if __name__ == "__main__":
    tf2lavka()
