from typing import Any, Type, TypeVar
import urllib.request, urllib.parse, urllib.error, urllib.parse
from bs4 import BeautifulSoup
from bs4 import element
import requests
import ssl

from Cleanner import Cleanner

beautifulSoup = TypeVar('beautifulSoup', BeautifulSoup, None)


class MovieScrapping:
    # desktop user-agent
    DESKTOP_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                         "Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.63 "

    def __init__(self):
        self.movie_dict = {}
        self.cleanner = Cleanner()

    @staticmethod
    def urlBuilder(movie_title: str):
        paramters = {
            'hl': 'en',
            'q': movie_title,
            'oq': movie_title
        }
        encoded_params = urllib.parse.urlencode(paramters)
        return f'https://www.google.com/search?{encoded_params}'

    def getSubtitleText(self, container):
        if container is None:
            return ''
        subtitle_el1 = container.select_one('div[data-attrid="subtitle"] span')
        if subtitle_el1 is None:
            return ''
        return subtitle_el1.text

    def getDescription(self, container):
        if container is None:
            return ''
        description_el1 = container.select_one('div[data-attrid="description"] span')
        if description_el1 is None:
            return ''
        return description_el1.text

    def getRating(self, container):
        if container is None:
            return ''
        el1 = container.select_one('div[data-attrid="kc:/film/film:reviews"] span')
        if el1 is None:
            return ''
        rating = el1.text
        return rating

    def getReleaseDate(self, container):
        if container is None:
            return ''
        release_date = container.find('div',
                                      attrs={
                                          'data-attrid': 'kc:/film/film:initial theatrical regional release date'
                                      })
        if release_date is None:
            release_date = container.find(
                'div',
                attrs={
                    'data-attrid': 'kc:/film/film:theatrical region aware release date'
                })
        if release_date is None:
            release_date = container.find('div', attrs={
                'data-attrid': 'kc:/film/film:release date'
            })
        if release_date is None:
            return ''
        return release_date.findAll('span')[1].text

    def getCountry(self, container):
        return ""

    def getLanguage(self, container):
        return ""

    def getTrailerLink(self, container):
        if container is None:
            return ''
        title_link_el = container.select_one('a[data-attrid="title_link"]')
        if title_link_el is None:
            return ''
        return title_link_el['href']

    def scrapMovie(self, title):
        if len(title) > 100:
            return None, None, 'Title Length cannot be larger than 100'
        headers = {"user-agent": self.DESKTOP_USER_AGENT}
        url = MovieScrapping.urlBuilder(title)
        print(url)
        resp = requests.get(url, headers=headers)
        movie_dict = {
            'title': '',
            'year': 0,
            'genre': '',
            'duration': 0,
            'description': '',
            'rating': float(0),
            'release_date': '',
            'country': '',
            'language': '',
            'trailer_id': ''
        }

        if resp.status_code == 200:
            cleanner = self.cleanner
            html = resp.content
            soup = BeautifulSoup(html.decode('UTF-8'), "html.parser")

            container = soup.find('body').select_one("#wp-tabs-container")

            subtitleText = self.getSubtitleText(container)
            description = self.getDescription(container)
            rating = self.getRating(container)
            releaseDateRaw = self.getReleaseDate(container)
            language = self.getLanguage(container)
            trailer_id = self.getTrailerLink(container)

            movie_dict['title'] = title

            year, genre, duration = cleanner.getCleanSubTitle(subtitleText)

            movie_dict['year'], movie_dict['genre'], movie_dict['duration'] = year, genre, duration
            movie_dict.update({'year': year, 'genre': genre, 'duration': duration})
            movie_dict['description'] = cleanner.getCleanDescription(description)
            movie_dict['rating'] = cleanner.getCleanRating(rating)
            releaseDate, country = cleanner.getCleanReleaseDate(releaseDateRaw)
            movie_dict['release_date'] = releaseDate
            movie_dict['country'] = country
            movie_dict['language'] = cleanner.getCleanLanguage(language)
            movie_dict['trailer_id'] = cleanner.getCleanTrailerId(trailer_id)
            return movie_dict, resp.status_code, 'Successful'
        else:
            return movie_dict, resp.status_code, 'Error Occurred'
