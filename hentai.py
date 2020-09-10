from urllib.parse import urlparse

from requests_html import HTMLSession


class Hentai:
    def __init__(self, id):
        self.id = id
        self.url = f"https://nhentai.net/g/{self.id}/"
        
    @property
    def _session(self):
        return HTMLSession().get(self.url)

    @property
    def html(self):
        return self._session.html

    @property
    def favorites(self):
        return self.html.find('.nobold', first = False)[1].text.strip('(').strip(')')

    @property
    def title(self):
        return self.html.find('h1.title', first = True).text

    @property
    def pretty(self):
        return self.html.find('span.pretty', first = True).text

    @property
    def cover(self):
        return self.html.find('.lazyload', first = True).attrs['data-src']

    @staticmethod
    def get_random_id():
        random_url = HTMLSession().get("https://nhentai.net/random").url
        return int(urlparse(random_url).path[3:-1])
