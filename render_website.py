import sys
import time
import requests

from jinja2 import Environment, FileSystemLoader, select_autoescape
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from more_itertools import chunked
from requests import HTTPError
from livereload import Server, shell


def parse_book_image(soup, book_url):
    image_tag = soup.find('div', {'class': 'bookimage'}).select('img')
    image_endlink = image_tag[0]['src']
    image_link = urljoin(book_url, image_endlink)

    return image_link


def parse_book_page(book_page):
    soup = BeautifulSoup(book_page.text, 'lxml')
    title, _, author = soup.find('h1').text.split('\xa0')

    image_link = parse_book_image(soup, book_page.url)
    # genres = parse_book_genres(soup)
    # comments = parse_page_comments(soup)

    return title, author, image_link


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template('template.html')

    books = []

    for book_id in range(1, 20):
        try:
            book_url = f'https://tululu.org/b{book_id}/'
            book_page_response = requests.get(book_url)
            book_page_response.raise_for_status()
            check_for_redirect(book_page_response)

            title, author, image_link = parse_book_page(book_page_response)

            books.append({'title': title, 'author': author, 'image': image_link, 'url': book_url})
        except HTTPError:
            print('Книга отсутствует в свободном доступе\n', file=sys.stderr)
            continue
        except requests.exceptions.ConnectionError:
            print('Ошибка соединения', file=sys.stderr)
            print('Попытка повторного подключения\n')
            time.sleep(10)
    books = chunked(books, 2)
    rendered_page = template.render(
        books=books
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    server = Server()
    server.watch('render_website.py', main)
    server.watch('template.html', main)

    server.serve(root='.')
    # server.serve_forever()
