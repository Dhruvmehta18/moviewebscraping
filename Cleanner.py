import re
from collections import defaultdict
import datetime
from typing import Tuple
import urllib.parse as urlparse
from urllib.parse import parse_qs
from unicodedata import normalize


def isDuration(subtitle):
    return bool(re.match(r'^(\d{1,2}\s*hours)|(\d{1,2}\s*(min)|m)|((\d{1,2}\s*h\s*)(\d{1,2}\s*m)?)$', subtitle))


def isYear(subtitle):
    try:
        int(subtitle)
        return True
    except ValueError:
        return False


class Cleanner():
    """For Cleaning the data that is coming from google search
    """

    releaseDateRegex = re.compile(r'(\d{1,2})\s(\D{3,12})\s(\d{4})')
    countryRegex = re.compile(r'.+\s\((\D+)\)$')
    ratingRegex = re.compile(r'^(\d.\d)/10$')

    @staticmethod
    def convertTextToMinutes(duration: str) -> int:
        """To convert a given human text to minutes

        Args:
            duration (str): String representation of the time in human words 
            E.g convert 2h 20m to 140 

        Returns:
            [int]: number of minutes
        """
        d = {
            'w': 7 * 24 * 60,
            'week': 7 * 24 * 60,
            'weeks': 7 * 24 * 60,
            'd': 24 * 60,
            'day': 24 * 60,
            'days': 24 * 60,
            'h': 60,
            'hr': 60,
            'hour': 60,
            'hours': 60,
        }
        mult_items = defaultdict(lambda: 1).copy()
        mult_items.update(d)

        parts = re.search(r'^(\d+)([^\d]*)', duration.lower().replace(' ', ''))
        if parts:
            return int(parts.group(1)) * mult_items[parts.group(2)] \
                   + Cleanner.convertTextToMinutes(re.sub(r'^(\d+)([^\d]*)', '', duration.lower()))
        else:
            return 0

    @staticmethod
    def normalized_data(text: str) -> str:
        return normalize("NFKD", text)

    def getCleanSubTitle(self, subtitle: str) -> Tuple[int, str, int]:
        if not subtitle:
            return self.getCleanYear(''), self.getCleanGenre(''), Cleanner.convertTextToMinutes('')
        normalized_subtitle = Cleanner.normalized_data(subtitle)
        subtitleArray = normalized_subtitle.split(sep=' ‧ ', maxsplit=3)
        year = 0
        genre = ''
        duration = 0
        for sub in subtitleArray:
            if isYear(sub):
                year = self.getCleanYear(sub)
            elif isDuration(sub):
                duration = Cleanner.convertTextToMinutes(sub)
            else:
                genre = self.getCleanGenre(sub)

        return year, genre, duration

    def getCleanDescription(self, description: str) -> str:
        if not description:
            return ''
        return Cleanner.normalized_data(description.strip()).replace('... MORE', '')

    def getCleanRating(self, ratingStr: str) -> float:
        if not ratingStr:
            return float(0)
        normalized_rating = Cleanner.normalized_data(ratingStr)
        ratingRegexObj = self.ratingRegex.search(normalized_rating)
        if ratingRegexObj is None or ratingRegexObj.lastindex != 1:
            return float(0)
        return float(ratingRegexObj.group(1))

    def getCleanReleaseDate(self, releaseDateFromWeb: str) -> Tuple[str, str]:
        if not releaseDateFromWeb:
            return '', ''
        normalized_releaseDate = Cleanner.normalized_data(releaseDateFromWeb)
        groups = self.releaseDateRegex.search(normalized_releaseDate)
        if groups is None or groups.lastindex != 3:
            return '', ''

        day, month, year = int(groups.group(1)), groups.group(2), int(groups.group(3))
        datetimeObj = datetime.datetime.strptime(month, "%B")
        releaseDateObj = datetime.datetime(year=year, month=datetimeObj.month, day=day)
        releaseDateStr = releaseDateObj.strftime('%Y-%m-%d')
        country = self.getCleanCountry(normalized_releaseDate)
        return releaseDateStr, country

    def getCleanCountry(self, country: str) -> str:
        if not country:
            return ''
        groups = self.countryRegex.search(Cleanner.normalized_data(country.strip()))
        if groups is None or groups.lastindex != 1:
            return ''
        country_txt = groups.group(1)
        return country_txt

    def getCleanLanguage(self, language: str) -> str:
        if not language:
            return ''
        return Cleanner.normalized_data(language.strip())

    def getCleanGenre(self, genre: str) -> str:
        if not genre:
            return ''
        return Cleanner.normalized_data(genre.strip()).replace("/", ",")

    def getCleanTrailerId(self, trailer_link: str) -> str:
        if not trailer_link:
            return ''
        parsed = urlparse.urlparse(Cleanner.normalized_data(trailer_link.strip()))
        trailer_id = parse_qs(parsed.query)['v']
        if len(trailer_id) < 0:
            return ''
        return trailer_id[0]

    def getCleanYear(self, year: str) -> int:
        if not year:
            return 0
        return int(Cleanner.normalized_data(year.strip()))

    def getCleanTitle(self, title: str) -> str:
        if not title:
            return ''
        return Cleanner.normalized_data(title.strip())
