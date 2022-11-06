import os
import time
from typing import Any

import telebot
import requests
import fake_useragent
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()

USER = fake_useragent.UserAgent()
HEADERS = {'user-agent': USER.random}


def get_vacancies(position):
    """Получаем список ссылок на вакансии для запрашиваемой позиции."""
    try:
        ref_list = []
        data = requests.get(
            url=f'https://career.habr.com/vacancies?q={position}&sort=date&type=all',
            headers=HEADERS
        )
        if data.status_code != 200:
            return
        soup = BeautifulSoup(data.content, 'lxml')
        for reference in soup.find_all('a', attrs={'class': 'vacancy-card__title-link'}):
            ref_list.append(f'https://career.habr.com{reference.attrs["href"]}')
        return ref_list
    except Exception as error:
        print(f'{error}')


def get_detail(reference):
    """Получение деталей вакансии."""
    data = requests.get(
        url=reference,
        headers=HEADERS
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    name = soup.find(
        'div', attrs={'class': 'vacancy-company__title'}
    ).text
    info = soup.find('div', attrs={'class': 'style-ugc'}).text
    detail = f'{name}\n{reference}\n{info}'
    return detail


bot = telebot.TeleBot(os.getenv('TOKEN'))


@bot.message_handler(content_types=['text'])
def show_info(message):
    """Выдача вакансий на первой странице сайта."""
    references = get_vacancies(position=message)
    for ref in references:
        result = get_detail(ref)
        bot.send_message(
            message.chat.id,
            f'{result}'
        )


bot.polling()
