import json
from os.path import exists as ext, getctime as gct
from os import listdir as ldr
from datetime import datetime
from time import mktime as mkt, sleep
from typing import Literal

from pypinyin import slug

from book_struct import BankedBook, BookLuxury, HmzedBook
from netwk import get_fullinfo
from config import save_json, CONFIG, confirm_name, read_json, find_hmz
from prg_export import save_as_rmz as savermz

NUMNAME, NAME, WRITER, GENRE, BUNKO = 0, 1, 2, 3, 4
BANK_PATH = CONFIG['BANK_PATH']
RMZ_EXPORT_PATH = CONFIG['RMZ_EXPORT_PATH']


def getCreateTime(file: str, return_type: Literal[0, 1] = 1):
    """

    :param file:
    :param return_type: 1 for int time stamp; 0 for time string.
    :return:
    """
    if return_type == 1:
        return int(gct(file))
    return datetime.fromtimestamp(getCreateTime(file)).strftime("%Y/%m/%d %H:%M:%S")


def getTimeStampFromString(timestr: str) -> int:
    big = timestr.split(' ')
    ymd = [int(i) for i in big[0].split('/')]
    hms = [int(i) for i in big[1].split(':')]
    time_tpl = (*ymd, *hms, 0, 0, 0)
    return int(mkt(time_tpl))  # NOQA


def read_hmz_par(hmzpath: str) -> HmzedBook:
    numname = hmzpath[:-4].split('/')[-1]
    print(f"Update Required! Auto updating {numname}...")
    hmzedbook = get_fullinfo(numname, return_type=1)
    hmzedbook.save_at(hmzpath)
    print("Updated!")
    sleep(0.2)
    return hmzedbook


def generate_book_bank():
    folders = [item for item in ldr(BANK_PATH) if '.' not in item]
    pre_books = []
    for item in folders:
        folder_path = f'{BANK_PATH}/{item}'
        hmz_file = find_hmz(folder_path)
        if hmz_file is not None:
            pre_books.append(read_hmz_par(f'{folder_path}/{hmz_file}'))
    save_as_bank(pre_books)


def save_as_bank(bank: list[BankedBook], simple_mode=False):
    bank_dict = [i.toDict() for i in bank]
    with open('bank.json', 'w', encoding='utf-8') as f:
        if simple_mode:
            json.dump(bank_dict, f, ensure_ascii=False, separators=(',', ':'))
        else:
            json.dump(bank_dict, f, indent=2, ensure_ascii=False)
    return 0


def read_bank_file():
    if not ext('bank.json'):
        generate_book_bank()
    bookbank = read_json('bank.json')
    newbookbank = [BankedBook(**i) for i in bookbank]
    return newbookbank


def add_to_bank(new_book: BankedBook):
    """
    Add a new book to bank.
    If a book has changed its name, all luxury info will be deleted.
    :param new_book: 'BankedBook'
    :return:
    """
    bank = read_bank_file()
    for i in bank:
        if i.name == new_book.name:
            return 0
        if i == new_book:
            print(f'Bookname of {i.numname} changed from {i.name} to {new_book.name}, Luxury info will be auto saved '
                  f'as rmz and deleted from bank.')
            savermz(1, i.toDict(), RMZ_EXPORT_PATH)
            bank.remove(i)
            break
    if new_book.directory == BANK_PATH:
        new_book.directory = ''
    bank.append(new_book)
    save_as_bank(bank)
    return 0


def filter_bank(constraint: tuple):
    """
    To get specific book object from bw_list.
    :param constraint: tuple[order, item], as the {item} of the {order}.
    :return: bookbank-like object
    """
    order, item = constraint
    bank = read_bank_file()
    return [i for i in bank if item in i[order]]


def filter_bw(constraint: tuple, bw_list: list) -> list:
    """
    To get specific book object from bw_list.
    :param bw_list: list[bookwidget].
    :param constraint: tuple[order, item], as the {item} of the {order}.
    :return: list[bookwidget]
    """
    order, item = constraint
    return [i for i in bw_list if item in i.bankinfo[order]]


def filter_liked_bw(liked: int, bw_list: list) -> list:
    if liked is None:
        return bw_list

    rt = []
    for i in bw_list:
        if len(i.bankinfo) < 6:
            continue
        if i.bankinfo[5]['fav'] and liked == 1:
            rt.append(i)
        if not i.bankinfo[5]['fav'] and liked == 2:
            rt.append(i)
    return rt


def order_bank_ranked(reverse: bool, bw_list: list) -> list:
    pre = []
    for i in bw_list:
        if len(i.bankinfo) < 6:
            pre.append((i, 0))
            continue
        if not i.bankinfo[5]['rtg']:
            pre.append((i, 0))
            continue
        pre.append((i, sum(i.bankinfo[5]['rtg'].values()) / len(i.bankinfo[5]['rtg'])))
    rt = sorted(pre, key=lambda bk: bk[1], reverse=reverse)
    return [i[0] for i in rt]


def order_bank(constraint: tuple, bank=None):
    """
    To order the bw_list as constraint ordered.
    :param bank: the bw_list-like object to order, whole bookbank by default.
    :param constraint: tuple[order, sgn], point out the order. 'sgn' indicates the start with "+" and "-".
    :return:
    """
    if bank is None:
        bank = read_bank_file()
    order, sgn = constraint
    if sgn == '+':
        sgn = 1
    else:
        sgn = -1
    if not order or order == 3:
        def key(x):
            return int(x[0]) * sgn, x[1]
    elif order == 1:
        def key(x):
            return slug(x[1], separator=''), int(x[0]) * sgn
    else:
        def key(x):
            return x[order], int(x[0]) * sgn
    return sorted(bank, key=key)


def order_bw(constraint: tuple | None, bw_list: list) -> list:
    """
    To order the bank as constraint ordered.
    :param bw_list: the bank-like object to order, whole bookbank by default.
    :param constraint: tuple[order, sgn], point out the order. 'sgn' indicates the start with "+" and "-".
    :return: Ordered bw_list.
    """
    if not bw_list:
        return []
    if constraint is None:
        return bw_list
    order, sgn = constraint
    if sgn == '+':
        sgn = 1
    else:
        sgn = -1
    if not order or order == 3:
        def key(x):
            return int(x.bankinfo[0]), x.bankinfo[1]
    elif order == 1:
        def key(x):
            return slug(x.bankinfo[1], separator=''), int(x.bankinfo[0]) * sgn
    else:
        def key(x):
            return x.bankinfo[order], int(x.bankinfo[0]) * sgn
    return sorted(bw_list, key=key, reverse=True if sgn == -1 else False)


def search_bank(keyword: str = '', bank=None):
    rett = []
    lazy_info = [slug(i[0] + i[1] + i[2], separator='') for i in bank]
    for y, i in enumerate(bank):
        if keyword in lazy_info[y]:
            rett.append(i)
    return rett


def search_bw(keyword: str = '', bw_list=None):
    if not bw_list:
        return None
    rett = []
    lazy_info = [i.bankinfo[0] + slug(i.bankinfo[1] + i.bankinfo[2], separator='') + i.bankinfo[1] + i.bankinfo[2] for i in bw_list]
    for y, i in enumerate(bw_list):
        if keyword in lazy_info[y]:
            rett.append(i)
    return rett


def get_all_info():
    bank = read_bank_file()
    pre_g = []
    pre_b = []
    for i in bank:
        pre_g += i[GENRE]
        pre_b.append(i[BUNKO])
    return sorted(list(set(pre_g))), sorted(list(set(pre_b)))


def luxury_bankinfo_manage(**kwargs):
    """
    Create the 'luxury' info list as [progress: list[str | list], ratings: dict, favorite: int[0|1]]
    :param kwargs: Existed luxury info.
    :return: LUX_LIST.
    """
    lux_bank = kwargs
    prg = lux_bank.get('progress', 0)
    rtg = lux_bank.get('ratings', 0)
    fav = lux_bank.get('favorite', 0)
    return [prg, rtg, fav]


def get_bookinfo_from(numname, bookbank=None):
    if bookbank is None:
        bookbank = read_bank_file()
    for i in range(len(bookbank)):
        if bookbank[i][0] == numname:
            return i, bookbank
    return None


def lux_transform():
    new_bank = []
    bank: list = read_bank_file()
    for i in bank:
        new_book = i[:5]
        if len(i) > 5:
            if not i[5][1] and not i[5][2] and not i[5][0]:
                new_bank.append(new_book)
                continue
            prg, rtg, fav = i[5]
            luxdict = {'prg': prg, 'rtg': rtg, 'fav': fav, 'lck': None}
            new_book.append(luxdict)
        new_bank.append(new_book)
    save_as_bank(new_bank)


def activate():
    print(order_bank((NUMNAME, '+'), filter_bank((BUNKO, "MF文库J"))))


def update_to_date():
    bank = read_json('bank.json')
    new_bank = []
    for i in bank:
        if len(i) < 6:
            new_lux = BookLuxury()
        else:
            new_lux = i[5]
            new_lux['lck'] = getTimeStampFromString(new_lux['lck']) if new_lux['lck'] else None
            new_lux = BookLuxury(**new_lux)

        new_book = BankedBook(numname=i[0], name=i[1], writer=i[2], genre=i[3], bunko=i[4], lux=new_lux,
                              addtime=getCreateTime(f'D:/ACGN/Novel/{confirm_name(i[1])}/{i[0]}.hmz'),
                              directory="D:/ACGN/Novel")
        new_bank.append(new_book)
    save_as_bank(new_bank)


def post_process():
    bank = read_bank_file()
    for i in bank:
        if i.directory == BANK_PATH:
            i.directory = ''
    save_as_bank(bank)


if __name__ == '__main__':
    post_process()
    # generate_book_bank()
