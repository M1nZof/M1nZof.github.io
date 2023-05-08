import json
import math
import os
from urllib import parse

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from livereload import Server


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template('template.html')

    books_per_page = 10
    books_on_page = []
    page_number = 0
    books_in_row = 2

    with open('books_properties.json', 'r', encoding='utf-8') as file:
        books_properties = json.load(file)
    books_quantity = len(books_properties)
    pages_quantity = math.ceil(books_quantity / books_per_page)

    for index, book_properity in enumerate(books_properties, start=1):
        book_properity['text_filename'] = parse.quote(book_properity['text_filename'])
        books_on_page.append(book_properity)
        if index % books_per_page == 0 or index == len(books_properties):
            chunked_books_on_page = chunked(books_on_page, books_in_row)
            rendered_page = template.render(
                books_properties=chunked_books_on_page,
                current_page_number=page_number + 1,
                pages_quantity=pages_quantity,
                books_in_row=books_in_row
            )

            if page_number != 0:
                page_name = f'index{page_number + 1}.html'
            else:
                page_name = 'index.html'

            books_on_page = []
            page_number += 1

            with open(os.path.join('pages', page_name), 'w', encoding="utf8") as file:
                file.write(rendered_page)

    os.makedirs('pages', exist_ok=True)
    os.makedirs('media/images', exist_ok=True)

    server = Server()
    server.watch('template.html', main)

    server.serve(root='.')


if __name__ == '__main__':
    main()
