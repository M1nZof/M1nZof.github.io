import math
import os
import sys
import time
import requests

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from requests import HTTPError
from livereload import Server

from parsing_methods import check_for_redirect, parse_book_page, download_image


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template('template.html')

    books_quantity = 57
    books_per_page = 10
    pages_quantity = math.ceil(books_quantity / books_per_page)

    for index, books_on_page in enumerate(chunked(range(1, books_quantity + 1), books_per_page), start=1):
        books = []
        for book_id in books_on_page:
            try:
                book_url = f'https://tululu.org/b{book_id}/'
                book_text_url = f'https://tululu.org/txt.php?id={book_id}/'
                book_page_response = requests.get(book_url)
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response)

                title, author, image_link, genres = parse_book_page(book_page_response)
                image = download_image(image_link)

                books.append(
                    {
                        'title': title,
                        'author': author,
                        'image': image,
                        'url': book_text_url,
                        'genres': genres
                    }
                )
            except HTTPError:
                print('Книга отсутствует в свободном доступе\n', file=sys.stderr)
                continue
            except requests.exceptions.ConnectionError:
                print('Ошибка соединения', file=sys.stderr)
                print('Попытка повторного подключения\n')
                time.sleep(10)
        books = chunked(books, 2)
        rendered_page = template.render(
            books=books,
            current_page_number=index,
            pages_quantity=pages_quantity
        )

        if index != 1:
            page_name = f'index{index}.html'
        else:
            page_name = 'index.html'

        with open(os.path.join('pages', page_name), 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    os.makedirs('pages', exist_ok=True)
    os.makedirs('media/images', exist_ok=True)

    main()

    server = Server()
    server.watch('render_website.py', main)
    server.watch('template.html', main)

    server.serve(root='.')
