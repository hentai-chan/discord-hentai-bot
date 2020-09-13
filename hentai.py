from datetime import datetime
from enum import Enum, unique
from typing import List
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


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
    _HOME = "https://nhentai.net/" 
    _URL = urljoin(_HOME, '/g')
    _API = urljoin(_HOME, '/api/gallery')

    # sleep time in-between failures = backoff_factor * (2 ** (total - 1))
    _retry_strategy = Retry(total = 5, status_forcelist = [413, 429, 500, 502, 503, 504], backoff_factor = 1)

    _assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()

    _session = requests.Session()
    _session.mount("https://", HTTPAdapter(max_retries = _retry_strategy))
    _session.hooks['response'] = [_assert_status_hook]
    _session.headers.update({
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51"
    })

    @staticmethod
    def _call_api(url: str, timeout: int) -> dict:
        response = Hentai._session.get(url)
        response.encoding = 'utf-8'
        return response.json()

    def __init__(self, id: int, timeout:int = 0):
        self.id = id
        self.timeout = timeout
        self.url = urljoin(Hentai._URL, str(self.id))
        self.api = Hentai._call_api(urljoin(Hentai._API, str(self.id)), self.timeout)      

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
        response = Hentai._session.get(urljoin(Hentai._HOME, 'random'))
        return int(urlparse(response.url).path[3:-1])
