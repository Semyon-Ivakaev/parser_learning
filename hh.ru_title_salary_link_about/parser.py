import time

import requests
from bs4 import BeautifulSoup
import csv
import os

vac = input('Введите профессию: ')
url = f'https://spb.hh.ru/search/vacancy?L_is_autosearch=false&area=2&clusters=true&enable_snippets=true&text={vac}&page=0'
#url = 'https://spb.hh.ru/search/vacancy?L_is_autosearch=false&area=2&clusters=true&enable_snippets=true&text=%D0%A2%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA&page=0'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
           'accept': '*/*'}
FILE = 'vacancy.txt'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_all_pages(html):
    soup = BeautifulSoup( html, 'html.parser' )
    pages = soup.find_all('a', class_='bloko-button HH-Pager-Control')
    if pages:
        return int(pages[-1].get_text())
    else:
        return 1


def get_all_vacancy(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='vacancy-serp-item')
    vacancy = []
    for item in items:
        metro = item.find('span', class_='metro-station')
        if metro:
            metro = metro.get_text()
        else:
            metro = 'No information'
        vacancy.append({
            'title': item.find('a', class_='bloko-link HH-LinkModifier').get_text(),
            'salary': '-' + item.find('div', class_='vacancy-serp-item__sidebar').find_next('span').get_text(),
            'link': item.find('a', class_='bloko-link HH-LinkModifier').get('href'),
            'company_name': item.find('a', class_='bloko-link bloko-link_secondary').get_text(strip=True),
            'company_link': 'https://spb.hh.ru' + item.find('a', class_='bloko-link bloko-link_secondary').get('href'),
            'metro': metro,
            'info': f"{item.find('div', class_='g-user-content').find_next('div').get_text()} " +
                f"{item.find('div', class_='g-user-content').find_next('div').find_next('div').get_text()}",
        })
    return vacancy


def save_file(items, path):
    with open(path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Вакансия', 'Зарплата', 'Ссылка на вакансию', 'Название фирмы',
                         'Ссылка на фирму', 'Станция метро', 'Информация о вакансии'])
        for item in items:
            writer.writerow(["%s\n" % item['title'] + "%s\n" % item['salary'] + # "%s\n" в каждой строки каждую запись
                             "%s\n" % item['link'] + "%s\n" % item['company_name'] +
                             "%s\n" % item['company_link'] + "%s\n" % item['metro'] +
                             "%s\n" % item['info']])


def parse():
    html = get_html(url)
    if html.status_code == 200:
        print('Ожидайте... Ищем вакансии.')
        vacancy = []
        pages = get_all_pages(html.text)
        for page in range(0, pages + 1):
            html = get_html(url, params={'page': page})
            vacancy.extend(get_all_vacancy(html.text))
            print(f'Найдено вакансий - {len(vacancy)}')
            if len(vacancy) > 450:
                time.sleep(1.5)
        save_file(vacancy, FILE)
        os.startfile( FILE )
    else:
        print(f"Не удалось, ошибка сервера - {html.status_code}")


parse()