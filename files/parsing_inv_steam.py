import requests
from bs4 import BeautifulSoup
import re
def inv_steam():
    try:
        a = []
        url = 'https://steamcommunity.com/profiles/76561199016413279/inventory/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.find_all('div', class_="games_list_tabs")
        for i in items:
            pars = i.find('a', id = "inventory_link_440").text.strip()
            for j in pars.split():
                a.append(j)
        b = a[3]
        str_example = re.findall(r'\(+(.*?)\)', b)
        keys = str_example[0]
        return keys
    except AttributeError:
        return 0
    except IndexError:
        return 0