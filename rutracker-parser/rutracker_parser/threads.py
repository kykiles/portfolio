from threading import Thread
from multiprocessing import Pool, cpu_count
import functools

from engine import ParserFilms


class ParserThread(Thread):
    """Потоковый парсинг"""

    def __init__(self, f, ParserFilms):
        """Инициализация потока"""
        Thread.__init__(self)
        self.f = f
        self.parser = ParserFilms
        self.result = {}

    def run(self):
        """Запуск потока"""
        with Pool(cpu_count()) as pool:
            _first_page_html = self.parser.get_html_by_url(self.f)  # html код первой страницы из категории
            _last_page_number = ParserFilms.get_last_page_number(_first_page_html)  # номер последней страницы lxml
            _temp = ParserFilms.get_list_pages_codes(_last_page_number)  # список кодов для параметра start
            _temp = pool.map(functools.partial(self.parser.get_html_by_url, self.f), _temp)  # хранение в ОП
            _temp = pool.map(ParserFilms.get_keys_descriptions_ratings, _temp)  # парсит данные lxml

        for info in _temp:
            self.result.update(info)

    def get_result(self):
        return self.result