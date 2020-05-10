import os

import requests
from bs4 import BeautifulSoup
import csv

URL = 'https://www.bonprix.ru/kategoriya/dlya-muzhchin-odezhda/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
           'accept': '*/*'}
FILE = 'clother.txt'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

#функция нужна так как на странице муж.одежды есть несколько категорий(футболки, джинсы и тд.)
def get_links_on_category(html):
    soup = BeautifulSoup( html, 'html.parser' )
    pages = soup.find_all('a', class_='teaser-slice teaser-custom-element teaser-element-variant-default')
    links_on_category = []
    for page in pages:
        links_on_category.append(page.get('href'))
    return links_on_category


#в каждой категории есть внутренние страницы с товарами
def get_page_on_good(html):
    soup = BeautifulSoup( html, 'html.parser' )
    pages = soup.find_all('li', class_='product-pager-page')
    if pages:
        return int(pages[-1].get_text()) #возвращает последнюю страницу с конца, ее число
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='product-list-item')
    goods = []

    for item in items:
        new = item.find( 'span', class_='new' )
        if new:
            new = new.get_text()
        else:
            new = 'Товар не новый.'
        goods.append({
            'title': item.find('div', class_='product-title').get_text(),
            'price': item.find('span', class_='price-tag').get_text(),
            'new': new,
            'link': item.find('a', class_='product-link').get('href').rstrip('#image'),
        })
    return goods


def save_file(items, path):
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Наименование', 'Цена', 'Новинка', 'Ссылка'])
        for item in items:
            writer.writerow([item['title'], item['price'], item['new'], item['link']])


#тут сложная логика, поэтому 2 цикла
def parse():
    html = get_html(URL)
    all_goods = []
    if html.status_code == 200:
        links = get_links_on_category(html.text) #на главное странице есть несколько категорий
        for link in links: #начиная с 1й категории начинаем
            html = get_html( link ) #открываем страницу с категорией
            pages = get_page_on_good( html.text ) #смотрим есть ли внутренние страницы с товарами
            goods = [] #сюда добавляем все товары из цикла, то есть у нас 3 страницы футболок...
            print(f"look {link}")
            for page in range(1, pages + 1):#...каждый цикл собирает все товары со страницы и добавляет в goods
                html = get_html( link, params={'page': page})
                get = get_content(html.text)
                goods.extend(get)
            all_goods.extend(goods) #по завершению цикла, все что есть в goods мы расширяем(extend) главный список
            print(f"Найдено {len(goods)} товаров.")
        save_file(all_goods, FILE) #и теперь главныцй список пишем в файл.
        os.startfile(FILE)
    else:
        print(f'Парсинг не сработал, code - {html.status_code}')


parse()