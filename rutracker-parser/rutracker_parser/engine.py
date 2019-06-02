import os.path
import requests
from lxml import html
import re

from parser_exception import ParserException
from config import ConfigWorker


class ParserFilms(object):
    def __init__(self):
        ParserFilms.make_dirs()  # Создание директорий для торрент файлов если она не сущ.
        self._session = requests.Session()
        self._config = ConfigWorker()
        self._HEADERS = self._config.get_ini_dict('User-Agent')

    @staticmethod
    def make_dirs():
        _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '\\torrent_files')
        if not os.path.isdir(_path):
            os.makedirs(_path)

    @staticmethod
    def get_list_pages_codes(last_page):
        """Формирует список из параметров всех страниц с первой по последнию"""
        if not last_page:
            return
        return [n * 50 for n in range(last_page)]

    @staticmethod
    def get_last_page_number(text):
        """Возвращает номер последней страницы из html кода, если не существует возвращает 1 - lxml"""
        if not text:
            raise ParserException('Данные из html страницы не загрузились')
        tree = html.fromstring(text)
        pages = tree.xpath('//a[@class="pg"]')
        if not pages:
            return 1
        return int(pages[-2].text)

    def get_html_by_url(self, f, start=None):
        """f: кодовый параметр категории фильмов, start: атрибут отвечающий за номер страницы"""
        _url = self._config.get_ini_option('Url', 'url_viewforum')
        response = requests.get(_url, headers=self._HEADERS, params={'f': f, 'start': str(start)})
        return response.text

    def get_html_topic(self, t):
        """Получает код html страницы топика с фильмом"""
        _url = self._config.get_ini_option('Url', 'url_viewtopic')
        response = requests.get(_url, headers=self._HEADERS, params={'t': str(t)})
        return response.text

    @staticmethod
    def page_text(html_page):
        """Формирует строку текста со странички с фильмом"""
        if not html_page:
            raise ParserException('Данные из html страницы не загрузились')
        tree = html.fromstring(html_page)
        description = tree.xpath('//div[@class="post_body"]')
        if not description:
            return
        description = description[0].text_content().split('\n')
        return ' '.join(description)

    @staticmethod
    def searcher(html_text, regex):
        """Ищет регуляркой строку"""
        result = re.search(regex, html_text)
        if result is None:
            return
        return result.group(1).strip()

    @staticmethod
    def get_pic_href(html_page):
        tree = html.fromstring(html_page)
        href = tree.xpath('//var[@class="postImg postImgAligned img-right"]')
        if not href:
            return
        return href[0].get('title')

    def get_pic_url(self, code):
        html_page = self.get_html_topic(code)
        url = ParserFilms.get_pic_href(html_page)
        if not url:
            return code, 'https://t3.ftcdn.net/jpg/01/01/89/46/240_F_101894688_RVSZUtDfPR6Cr5eBDQI7Qo5pZ01jmyK3.jpg'
        return code, url

    @staticmethod
    def get_keys_descriptions_ratings(text):
        """Возвращает словарь {'параметр-ссылка на топик': 'Описание'} - lxml вариант"""
        if not text:
            raise ParserException('Данные из html страницы не загрузились')
        _temp = {}
        tree = html.fromstring(text)
        data = tree.xpath('//tr[@class="hl-tr"]')
        for id_topic in data:
            code = id_topic.get('data-topic_id')
            _description = tree.xpath('//a[@id="tt-' + code + '"]')[0].text_content().strip()
            _rating = tree.xpath('//tr[@data-topic_id="' + code + '"]//p[@title="Торрент скачан"]/b/text()')
            _seeders = tree.xpath('//tr[@data-topic_id="' + code + '"]//span[@title="Seeders"]/b/text()')
            _leechers = tree.xpath('//tr[@data-topic_id="' + code + '"]//span[@title="Leechers"]/b/text()')
            _gb = tree.xpath('//tr[@data-topic_id="' + code + '"]//a[@class="small f-dl dl-stub"]/text()')
            if _rating:
                _rating = _rating[0].strip().replace(',', '')
                _params = {
                    'Description': _description,
                    'Downloads': int(_rating),
                    'Seeders': _seeders[0],
                    'Leechers': _leechers[0],
                    'GB': _gb[0]
                }
                _temp[code] = _params
        return _temp

    @staticmethod
    def name_splitter(name):
        name = re.sub(r'[\\/:*?"<>|]', ' ', str(name))
        return ' '.join(name.split())

    def download_torrent_file(self, film_code, file_name):
        """Сохраняет torrent файл по ключу топика фильма с именем filename в папку torrent_files"""
        _user = {
            'login_username': self._config.get_ini_option('User', 'login_username'),
            'login_password': self._config.get_ini_option('User', 'login_password'),
            'login': self._config.get_ini_option('User', 'login')
        }
        _url_login = self._config.get_ini_option('Url', 'url_login')
        self._session.post(_url_login, headers=self._HEADERS, data=_user)

        _url_download = self._config.get_ini_option('Url', 'url_download')
        response = self._session.get(_url_download, stream=True, headers=self._HEADERS,
                                     params={'t': film_code})

        file_name = film_code + '_' + ParserFilms.name_splitter(file_name).split('[', 1)[0]
        path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(path, 'torrent_files\\' + file_name + '.torrent'), 'bw') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)


if __name__ == '__main__':
    parser = ParserFilms()
    html = parser.get_html_by_url('1950')
    print(ParserFilms.get_keys_descriptions_ratings(html))