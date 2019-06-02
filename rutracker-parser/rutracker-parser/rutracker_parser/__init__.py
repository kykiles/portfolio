import os
from datetime import datetime
from terminaltables import AsciiTable
import click

from engine import ParserFilms
from jsonworker import JsonWorker
from threads import ParserThread
from pic_url_parser import pic_url_parser

# from actors import ActorsParser
from config import ConfigWorker

parser = ParserFilms()  # Экземпляр класса ParserFilms
config = ConfigWorker()  # Экземпляр класса ConfigWorker
path = os.path.dirname(os.path.abspath(__file__))  # Путь до директории


def test_time(func):
    """Декоратор для тестирования времени выполнения кода"""
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        total = end - start
        print('Время выполнения:', total, sep=' ')
        return result
    return wrapper


def sort_dict_by_value(data):
    temp = {}
    result = {}
    for key, value in data.items():
        downloads = value.get('Downloads')
        if downloads in temp:
            temp[downloads].append(key)
        else:
            temp[downloads] = [key,]
    for key in sorted(temp.keys(), reverse=True):
        values = temp.get(key)
        for value in values:
            result[value] = data.get(value)
    return result


def films_echo(result):
    if not result:
        return
    data = [
        ('Code', 'Description'),
        *((k, v['Description']) for k, v in result.items())
    ]

    table = AsciiTable(data, title='Список торрент топиков')
    print(table.table)
    print('Найдено:', len(data) - 1, 'записей', sep=' ')


def update_db_in_ram():
    """Загрузка спарсенных данных в ОП"""
    topics = config.get_ini_dict('Topics').keys()
    workers = []
    data = {}
    for f in topics:
        thread = ParserThread(f, parser)
        thread.daemon = False
        thread.start()
        workers.append(thread)
    for t in workers:
        t.join()
        data.update(t.get_result())
        print('Обновленно')

    new_torrent = JsonWorker.new_torrent_topics(os.path.join(path, 'files\\films_db.json'), data)
    updated_data = pic_url_parser(data=new_torrent)
    films_echo(updated_data)
    JsonWorker.dict_to_json(os.path.join(path, 'files\\new_torrent.json'), updated_data)
    JsonWorker.update_dict_in_json(os.path.join(path, 'files\\films_db.json'), updated_data)


@click.group()
def cli():
    """uparser 1.0.0: при первом запуске сделайте update"""
    pass


@click.command(name='info', help='Выводит описание фильма по введенному code')
@click.argument('code')
def get_description(code):
    # Выводит описание фильма по введенному code
    _html = parser.get_html_topic(code)
    _page_text = ParserFilms.page_text(_html)
    _target = r'Описание:+(.*)Качество видео:+'
    _description = ParserFilms.searcher(_page_text, _target)
    _target = r'В ролях:+(.*)Описание:+'
    _actors = ParserFilms.searcher(_page_text, _target)
    if not _description:
        _description = 'Описание отсутсвует'
    if not _actors:
        _actors = 'Актёрский состав не найден'
    print('Code:', code, sep=' ')
    _temp = ('Описание: ' + _description).split('.')
    print('В ролях:', _actors, sep=' ')
    for line in _temp:
        if line:
            print(line.strip() + '.')


@click.command(name='update', help='Обновление базы данных фильмов и актёров')
@test_time
def update_db():
    # Обновление базы данных фильмов
    click.echo('Обновление базы данных, подождите это займёт несколько минут...')

    # data = main()
    # print(f'Всего раздач {len(data)}')
    # JsonWorker.dict_to_json(os.path.join(path, 'files\\films_db.json'), data)
    # JsonWorker.dict_to_json(os.path.join(path, 'files\\films_db.json'), update_db_in_ram())

    update_db_in_ram()
    print('Сортировка ...')
    data = JsonWorker.json_to_dict(os.path.join(path, 'files\\films_db.json'))
    print('Всего раздач:', len(data), sep=' ')
    JsonWorker.dict_to_json(os.path.join(path, 'files\\films_db.json'), sort_dict_by_value(data))
    # parser_a = ActorsParser()
    # new_torrents = parser_a.parse_actors()
    # if new_torrents:
    #     films_echo(new_torrents)


@click.command(name='fopen')
def open_torrent_dir():
    """Открывает папку с торрент файлами"""
    os.startfile(os.path.join(path, 'torrent_files'))


@click.command(name='clear')
def clear_torrent_dir():
    """Очищает папку с торрент файлами"""
    click.echo('Удаление всех торрент файлов...')
    os.system('erase ' + os.path.join(path, 'torrent_files\\'))
    click.echo('Успешно')


@click.command(name='download')
@click.option('codes', '-c', multiple=True, help='Загружает -c ключ фильма')
@click.option('_all', '-all', is_flag=True, help='Сохраняет все файлы с последнего поиска')
def download_torrent_file(codes, _all):
    """Загружает торрент файлы по ключам"""
    if _all:
        data = JsonWorker.json_to_dict(os.path.join(path, 'files\\temp.json'))
        if not data:
            print('Файл temp.json пуст')
            return
        codes = data.keys()
    else:
        data = JsonWorker.json_to_dict(os.path.join(path, 'files\\films_db.json'))

    with click.progressbar(codes, label='Сохранение torrent файлов', empty_char='.') as bar:
        for code in bar:
            if code not in data.keys():
                print('Фильма с ключом:', code, 'нет в базе данных', sep=' ')
                return
            parser.download_torrent_file(code, data.get(code)['Description'])

    JsonWorker.dict_to_json(os.path.join(path, 'files\\temp.json'), None)
    click.echo('Загрузка файлов успешно завершена')


@click.command(name='search', help='Поиск по ключевым словам')
@click.option('keys', '-k', multiple=True, help='Выводит результат поиска по -k Ключ')
@test_time
def echo_search_by_keys(keys):
    """Поиск по ключевым словам"""
    result = JsonWorker.search_by(keys)
    if not result:
        return
    films_echo(result)
    JsonWorker.dict_to_json(os.path.join(path, 'files\\temp.json'), result)


cli.add_command(update_db)
cli.add_command(download_torrent_file)
cli.add_command(echo_search_by_keys)
cli.add_command(open_torrent_dir)
cli.add_command(clear_torrent_dir)
cli.add_command(get_description)