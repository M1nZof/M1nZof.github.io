import os
import requests

from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from requests import HTTPError


def parse_book_image(soup, book_url):
    image_tag = soup.find('div', {'class': 'bookimage'}).select('img')
    image_endlink = image_tag[0]['src']
    image_link = urljoin(book_url, image_endlink)

    return image_link


def parse_book_genres(soup):
    genres_tag = soup.find('span', {'class': 'd_book'}).find_all('a')

    return [genre.text for genre in genres_tag]


def parse_book_page(book_page):
    soup = BeautifulSoup(book_page.text, 'lxml')
    title, _, author = soup.find('h1').text.split('\xa0')

    image_link = parse_book_image(soup, book_page.url)
    genres = parse_book_genres(soup)

    return title, author, image_link, genres


def download_image(image_link):
    response = requests.get(image_link)
    response.raise_for_status()

    image_name = urlparse(image_link).path.split('/')[2]
    image_path = os.path.join('media/images', str(image_name))

    with open(image_path, 'wb') as image:
        image.write(response.content)

    return image_path


def check_for_redirect(response):
    if response.history:
        raise HTTPError
