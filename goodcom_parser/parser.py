import requests
from bs4 import BeautifulSoup
import csv
import os

URL = 'https://goodcom.ru/catalog/smartfony-i-kommunikatory'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
           'accept': '*/*'}
FILE = 'goods.txt'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='full')
    devices = []

    for item in items:
        devices.append({
            'title': item.find('a', class_='title').find_next('span').get_text(strip=True),
            'link': item.find('a', class_='title').get('href'),
            #'picture': item.find('div', class_='img').find_next('img').get('src'),
            'price': item.find('p', class_='cur').get_text(strip=True),
            #'shop': 'В наличии' + item.find('span', class_='_popup_addrs').get_text(strip=True).strip('\n')
        })
    return devices


def save_file(items, path):
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Модель', 'Цена', 'Ссылка'])
        for item in items:
            writer.writerow([item['title'], item['price'], item['link']])


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        devices = get_content(html.text)

    save_file(devices, FILE)
    print(f'Отображено {len(devices)} моделей')
    os.startfile(FILE)

parse()
