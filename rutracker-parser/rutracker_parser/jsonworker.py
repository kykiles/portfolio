import json
import os.path


class JsonWorker(object):
    @staticmethod
    def dict_to_json(path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def json_to_dict(path):
        if not os.path.isfile(path):
            JsonWorker.dict_to_json(path, {})
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def new_torrent_topics(path, data):
        result = {}
        films_db = JsonWorker.json_to_dict(path)
        for key, value in data.items():
            if key not in films_db:
                result[key] = value
        return result

    @staticmethod
    def update_dict_in_json(path, data):
        if not data:
            return
        films_db = JsonWorker.json_to_dict(path)
        films_db.update(data)
        JsonWorker.dict_to_json(path, films_db)

    @staticmethod
    def sub_json(path_1, path_2):
        json_1_codes = set(JsonWorker.json_to_dict(path_1).keys())
        json_2_codes = set(JsonWorker.json_to_dict(path_2).keys())
        result = list(json_2_codes.difference(json_1_codes))
        return result

    @staticmethod
    def search_by(keys):
        """Поиск в json по ключевым словам"""
        path = os.path.dirname(os.path.abspath(__file__))
        if not keys:
            print('Введена пустая строка')
            return
        if not os.path.isfile(os.path.join(path, 'files\\films_db.json')):
            print('Обновите базу данных(команда update)')
            return
        _result = {}
        data = JsonWorker.json_to_dict(os.path.join(path, 'files\\films_db.json'))
        # actors = JsonWorker.json_to_dict(os.path.join(path, 'files\\actors.json'))
        for code, value in data.items():
            # actor = actors.get(code)
            _flag = True
            for key in keys:
                if key.lower() not in value.get('Description').lower():# + actor.lower():
                    _flag = False
            if _flag:
                _result[code] = value
        return _result