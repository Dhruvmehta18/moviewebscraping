import re
from collections import defaultdict
import datetime
import urllib.parse as urlparse
from urllib.parse import parse_qs
from pandas.core.resample import g


class Cleanner():
    """For Cleaning the data that is coming from web or some file
    """

    releaseDateRegex = re.compile('(\d{1,2})\s(\D{3,12})\s(\d{4})\s\((\D+)\)')
    ratingRegex = re.compile('^(\d.\d)/10$')

    def __init__(self):
        pass

    def convertTextToMinutes(self, duration: str):
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
                   + self.convertTextToMinutes(re.sub(r'^(\d+)([^\d]*)', '', duration.lower()))
        else:
            return 0

    def getCleanSubTitle(self, subtitle: str):
        if subtitle is None:
            return ''
        year, genre, duration = subtitle.split(sep=" ‧ ")
        return self.getCleanYear(year), self.getCleanGenre(genre), self.convertTextToMinutes(duration)

    def getCleanDescription(self, description: str):
        if description is None:
            return ''
        return description.replace('… MORE', '')

    def getCleanRating(self, ratingStr: str):
        if ratingStr is None or ratingStr == "":
            return float(0)
        ratingRegexObj = self.ratingRegex.search(ratingStr)
        return float(ratingRegexObj.group(1))

    def getCleanReleaseDate(self, releaseDateFromWeb: str):
        if releaseDateFromWeb is None or releaseDateFromWeb == "":
            return "", ""
        groups = self.releaseDateRegex.search(releaseDateFromWeb)
        if groups is None or groups.lastindex != 4:
            return '', ''
        day, month, year, country = int(groups.group(1)), groups.group(2), int(groups.group(3)), groups.group(4),
        datetimeObj = datetime.datetime.strptime(month, "%B")
        releaseDateObj = datetime.datetime(year=year, month=datetimeObj.month, day=day)
        releaseDateStr = releaseDateObj.strftime('%Y-%m-%d')
        return releaseDateStr, self.getCleanCountry(country)

    def getCleanCountry(self, country: str):
        if country is None:
            return ''
        return country

    def getCleanLanguage(self, language: str):
        if language is None:
            return ''
        return language

    def getCleanGenre(self, genre: str):
        if not genre:
            return ''
        return genre.replace("/", ",")

    def getCleanTrailerId(self, trailer_link: str):
        if not trailer_link:
            return ''
        parsed = urlparse.urlparse(trailer_link)
        trailer_id = parse_qs(parsed.query)['v']
        if len(trailer_id) < 0:
            return ''
        return trailer_id[0]

    def getCleanYear(self, year: str):
        if year is None:
            return 0
        return int(year)

    def getCleanTitle(self, title: str):
        if title is None:
            return ''
        return title
