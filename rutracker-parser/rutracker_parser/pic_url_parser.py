from multiprocessing import Pool, cpu_count

from engine import ParserFilms


def pic_url_parser(data=None):
    if not data:
        return
    parser = ParserFilms()
    keys = data.keys()

    with Pool(cpu_count()) as pool:
        pic_urls = pool.map(parser.get_pic_url, keys)

    for code, url in pic_urls:
        data[code]['pic_url'] = url
    return data


if __name__ == '__main__':
    pic_url_parser()