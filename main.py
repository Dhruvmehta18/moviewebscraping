from logging import error
import os
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from requests import status_codes
import csv
import re
import time
import random

from testlocation import get_test_location
from MovieScrapping import MovieScrapping
from DocumentScrapping.DocScrap import DocScrap

test_location = get_test_location()

csv_file_regex = re.compile('.csv$')

_min_sleep_time = 5


class AvailableType:
    FILE = 'file'

    def __init__(self):
        pass

    def type_list(self):
        return [self.FILE]

    def type_list_str(self):
        return ', '.join(map(str, self.type_list()))


def write_dic_csv(movie_dict_list: []):
    # name of csv file
    filename = input("Enter the file name with which you want to save\n")
    absolute_file_path = os.path.join(os.path.expanduser('~'), 'Documents', filename)
    if absolute_file_path is None:
        absolute_file_path = filename
    # TODO: make a check to the entered csv file
    fieldnames = ['title', 'description', 'duration', 'rating', 'release_date', 'year', 'country',
                  'language', 'total_reviews', 'genre', 'card_photo', 'cover_photos', 'trailer_id'
                  ]
    # writing to csv file
    with open(absolute_file_path, 'w') as csv_file:
        # creating a csv writer object
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(movie_dict_list)
    print("file created")


def startScrap(dataframe):
    titles = dataframe['title'].to_list()
    webScraping = MovieScrapping()
    movies_dict_list = []
    for title in titles:
        print(title)
        movie_dict, status_codes, errorMessage = webScraping.scrapMovie(f'{title} movie')
        print(movie_dict)
        movies_dict_list.append(movie_dict)
        _sleep_time = random.randint(_min_sleep_time, 2 * _min_sleep_time)
        time.sleep(_sleep_time)

    write_dic_csv(movies_dict_list)


def get_from_file():
    file_path = input("Enter file path you want to use\n")
    if file_path is None or file_path is str():
        file_path = test_location

    dataframe = DocScrap(file_path).read()
    print(dataframe['title'])
    startScrap(dataframe)


def main(type: str):
    if type is AvailableType.FILE:
        get_from_file()
    else:
        error('Type = {type} not supported')


def start():
    print('Available type are from {0} '.format(AvailableType().type_list_str()))
    main(AvailableType.FILE)


start()
