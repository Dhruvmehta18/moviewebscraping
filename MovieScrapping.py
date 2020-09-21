from typing import Any, Type, TypeVar
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from bs4 import element
import requests
import ssl

from Cleanner import Cleanner

beautifulSoup = TypeVar('beautifulSoup', BeautifulSoup, None)

#TODO break the chaining functions


class MovieScrapping:
    # desktop user-agent
    DESKTOP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

    def __init__(self):
        self.movie_dict = {}
        self.cleanner = Cleanner()

    @staticmethod
    def urlBuilder(movie_title: str):
        movie_tokens = movie_title.split(" ")
        movie_tokens_concat = "+".join(movie_tokens)
        return f'https://www.google.com/search?hl=en&q={movie_tokens_concat}&oq={movie_tokens_concat}'

    def getSubtitleText(self, container):
        if container is None:
            return ''

        return container.select_one('div[data-attrid="subtitle"]').find('span').text

    def getDescription(self, container):
        if container is None:
            return ''
        return container.select_one('div[data-attrid="description"]').find('span').text

    def getRating(self, container):
        if container is None:
            return ''
        return container.select_one('div[data-attrid="kc:/film/film:reviews"]').find('span').text

    def getReleaseDate(self, container):
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
            return ''
        return release_date.findAll('span')[1].text

    def getCountry(self, container):
        return ""

    def getLanguage(self, container):
        return ""

    def getTrailerLink(self, container):
        if container is None:
            return ''
        return container.select_one('a[data-attrid="title_link"]')['href']

    def scrapMovie(self, title):
        if len(title) > 30:
            return None
        headers = {"user-agent": self.DESKTOP_USER_AGENT}
        URL = MovieScrapping.urlBuilder(title)
        print(URL)
        resp = requests.get(URL, headers=headers)
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
            soup = BeautifulSoup(html, "html.parser")

            container = soup.find('body').select_one("#wp-tabs-container")

            subtitleText = self.getSubtitleText(container)
            description = self.getDescription(container)
            print(description)
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
            movie_dict['country'] = cleanner.getCleanCountry(country)
            movie_dict['language'] = cleanner.getCleanLanguage(language)
            movie_dict['trailer_id'] = cleanner.getCleanTrailerId(trailer_id)
            return movie_dict, resp.status_code, 'Successful'
        else:
            return None, resp.status_code, 'Error Occurred'
