from datetime import datetime
from enum import Enum, unique
from typing import List
from urllib.parse import urljoin, urlparse

import requests


@unique
class Format(Enum):
    English = 'english'
    Japanese = 'japanese'
    Pretty = 'pretty'

@unique
class Extension(Enum):
    JPG = 'j'
    PNG = 'p'
    GIF = 'g'

class Hentai(object):
    _url = lambda id: urljoin("https://nhentai.net/api/gallery/", str(id))

    def __init__(self, id: int):
        self.id = id
        self.url = urljoin("https://nhentai.net/g/", str(self.id))
        self.api = Hentai._call_api(Hentai._url(self.id))      
        
    @staticmethod
    def _call_api(url) -> dict:
        _response = requests.get(url)
        _response.encoding = 'utf-8'
        if _response.status_code != 200:
            raise requests.ConnectionError(f"Expected status code 200, but got {_response.status_code}")
        else:
            return _response.json()

    @property
    def media_id(self) -> int:
        return self.api['media_id']

    def title(self, format: Format) -> str:
        return self.api['title'].get(format.value)

    @property
    def cover(self) -> str:
        cover_ext = Extension(self.api['images']['cover']['t']).name.lower()
        return f"https://t.nhentai.net/galleries/{self.media_id}/cover.{cover_ext}"

    @property
    def thumbnail(self) -> str:
        thumb_ext = Extension(self.api['images']['thumbnail']['t']).name.lower()
        return f"https://t.nhentai.net/galleries/{self.media_id}/thumb.{thumb_ext}"

    @property
    def upload_date(self) -> datetime:
        return datetime.fromtimestamp(self.api['upload_date'])

    _name = lambda self, type: [tag['name'] for tag in self.api['tags'] if tag['type'] == type]

    @property
    def tags(self) -> List[str]:
        return Hentai._name(self, 'tag')

    @property
    def language(self) -> List[str]:
        return Hentai._name(self, 'language')

    @property
    def artist(self) -> str:
        return Hentai._name(self, 'artist')[0]

    @property
    def category(self) -> List[str]:
        return Hentai._name(self, 'category')

    @property
    def num_pages(self) -> int:
        return self.api['num_pages']

    @property
    def num_favorites(self) -> int:
        return self.api['num_favorites']

    _extension = lambda self: Extension(self.api['images']['pages'][0]['t']).name.lower()

    @property
    def image_urls(self) -> List[str]:
        page_url = lambda num: f"https://i.nhentai.net/galleries/{self.media_id}/{num}.{Hentai._extension(self)}"
        return [page_url(num) for num in range(self.num_pages + 1)] 

    @staticmethod
    def random_id() -> int:
        _session = requests.get("https://nhentai.net/random/")
        return int(urlparse(_session.url).path[3:-1])
