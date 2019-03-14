from engine import ParserFilms
from jsonworker import JsonWorker
import os.path
from multiprocessing import Pool, cpu_count


class ActorsParser(object):
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self._data = JsonWorker.json_to_dict(os.path.join(self.path, 'files\\actors_list.json'))

    def actors(self, code):
        parser = ParserFilms()
        _temp = []
        _page = parser.get_html_topic(code)
        _page = ParserFilms.page_text(_page)

        for actor in self._data:
            if actor in _page:
                _temp.append(actor)
        return code, ', '.join(_temp)

    @staticmethod
    def echo_new_films(codes, data):
        result = {}
        for code in codes:
            result[code] = data[code]
        return result

    def parse_actors(self):
        new_actor_codes = JsonWorker.sub_json(self.path + '\\files\\actors.json', self.path + '\\files\\films_db.json')
        new_torrents = None
        if new_actor_codes:
            new_torrents = ActorsParser.echo_new_films(new_actor_codes,
                                                       JsonWorker.json_to_dict(self.path + '\\files\\films_db.json'))
        print('Добавлено новых раздач:', len(new_actor_codes), sep=' ')
        data = JsonWorker.json_to_dict(os.path.join(self.path, 'files\\actors.json'))
        with Pool(cpu_count()) as pool:
            actors = pool.map(self.actors, new_actor_codes)
        for actor in actors:
            data[actor[0]] = actor[1]
        JsonWorker.dict_to_json(os.path.join(self.path, 'files\\actors.json'), data)
        return new_torrents