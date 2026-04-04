from datetime import datetime
from os import listdir as ldr
from os.path import exists as ext, getctime as gct
from time import mktime as mkt, sleep
from typing import Literal

from pypinyin import slug

from book_struct import BankedBook, BookLuxury, HmzedBook
from config import CONFIG, confirm_name, read_json, find_hmz, save_json
from netwk import get_fullinfo
from prg_export import save_as_rmz as savermz

BANK_PATH = CONFIG['BANK_PATH']
RMZ_EXPORT_PATH = CONFIG['RMZ_EXPORT_PATH']
SIMPLE_BANK_FILE = CONFIG['SIMPLE_BANK_FILE']


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


def getTimeStringFromStamp(timestamp: int | float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y/%m/%d %H:%M:%S")


def read_hmz_par(hmzpath: str) -> HmzedBook:
    def update_hmz():
        numname = hmzpath[:-4].split('/')[-1]
        print(f"Update Required! Auto updating {numname}...")
        hmzbook = get_fullinfo(numname, return_type=1)
        hmzbook.save_at(hmzpath)
        print("Updated!")
        sleep(0.2)
        return hmzbook

    if not ext(hmzpath):
        return update_hmz()

    hmzedfile = read_json(hmzpath)
    try:
        hmzedbook = HmzedBook(**hmzedfile)
    except Exception as e:
        print(e)
        return update_hmz()

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


def save_as_bank(bank: list[BankedBook]):
    bank_dict = [i.toDict() for i in bank]
    return save_json('bank.json', bank_dict, format_=1 - SIMPLE_BANK_FILE)


def read_bank_file():
    if not ext('bank.json'):
        generate_book_bank()
    bookbank = read_json('bank.json')
    newbookbank = [BankedBook(**i) for i in bookbank]
    return newbookbank


def getBookFromNumname(numname: str) -> BankedBook | None:
    bank = read_bank_file()
    for i in bank:
        if numname == i.numname:
            return i
    print('Book not found!')
    return None


def add_to_bank(new_book: BankedBook, force_cover: bool = False):
    """
    Add a new book to bank.
    If a book has changed its name, all luxury info will be deleted.
    :param force_cover:
    :param new_book: 'BankedBook'
    :return:
    """
    bank = read_bank_file()
    for i in bank:
        if i.name == new_book.name:
            if not force_cover:
                return 0
            bank.remove(i)
            break
        if i == new_book:
            print(f'Bookname of {i.numname} changed from {i.name} to {new_book.name}, Luxury info will be auto saved '
                  f'as rmz and deleted from bank.')
            savermz(1, i.toDict(), RMZ_EXPORT_PATH)
            bank.remove(i)
            break

    if new_book.directory == BANK_PATH and SIMPLE_BANK_FILE:
        new_book.directory = ''

    bank.append(new_book)
    save_as_bank(bank)
    return 0


def filter_bank(constraint: tuple[str, str]):
    """
    To get specific book object from bw_list.
    :param constraint: tuple[order, item], as the {item} of the {order}.
    :return: bookbank-like object
    """
    order, item = constraint
    bank = read_bank_file()
    return [i for i in bank if item == i[order]]


def filter_bw(constraint: tuple, bw_list: list) -> list:
    """
    To get specific book object from bw_list.
    :param bw_list: list[bookwidget].
    :param constraint: tuple[order, item], as the {item} of the {order}.
    :return: list[bookwidget]
    """
    if not constraint or not constraint[1]:
        return bw_list
    order, item = constraint
    return [i for i in bw_list if item in i.bankinfo[order]]


def filter_liked_bw(liked: int, bw_list: list) -> list:
    if liked is None:
        return bw_list

    rt = []
    for i in bw_list:
        if i.bankinfo.lux.fav and liked == 1:
            rt.append(i)
        if not i.bankinfo.lux.fav and liked == 2:
            rt.append(i)
    return rt


def order_bw_ranked(reverse: bool, bw_list: list) -> list:
    pre = []
    for i in bw_list:
        lux_i = i.bankinfo.lux
        if not lux_i.rtg:
            pre.append((i, 0))
            continue
        pre.append((i, sum(lux_i.rtg.values()) / len(lux_i.rtg)))
    rt = sorted(pre, key=lambda bk: bk[1], reverse=reverse)
    return [i[0] for i in rt]


def order_bank(constraint: tuple, bank: list['BankedBook'] = None):
    """
    To order the bw_list as constraint ordered.
    :param bank: the bw_list-like object to order, whole bookbank by default.
    :param constraint: tuple[order, sgn], point out the order. 'sgn' indicates the start with "+" and "-".
    :return:
    """
    if bank is None:
        bank = read_bank_file()

    order = constraint[0]
    sgn = True if constraint[1] == '-' else False

    if not order or order == 3:
        return sorted(bank, key=lambda bk: (int(bk.numname), bk.name), reverse=sgn)
    elif order == 1:
        return sorted(bank, key=lambda bk: (slug(bk.name, separator=''), int(bk.numname)), reverse=sgn)
    else:
        return sorted(bank, key=lambda bk: (bk[order], int(bk.numname)), reverse=sgn)


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

    order = constraint[0]
    sgn = True if constraint[1] == '-' else False

    if order == 0:
        return sorted(bw_list, key=lambda bk: (int(bk.bankinfo.numname), bk.bankinfo.name), reverse=sgn)
    elif order == 1:
        return sorted(bw_list, key=lambda bk: (slug(bk.bankinfo.name, separator=''), int(bk.bankinfo.numname)),
                      reverse=sgn)
    elif order == 2:
        return sorted(bw_list, key=lambda bk: (int(bk.bankinfo.addtime), bk.bankinfo.name), reverse=sgn)
    else:
        return sorted(bw_list, key=lambda bk: (bk.bankinfo[order], int(bk.bankinfo.numname)), reverse=sgn)


def search_bank(keyword: str = '', bank=None):
    if not bank:
        return []
    rett = []
    lazy_info = [i[0] + slug(i[1] + i[2], separator='') for i in bank]
    for y, i in enumerate(bank):
        if keyword in lazy_info[y]:
            rett.append(i)
    return rett


def search_bw(keyword: str = '', bw_list=None):
    if not bw_list:
        return None
    rett = []
    lazy_info = [(f'{i.bankinfo[0]}'
                  f'{slug(f'{i.bankinfo[1]}{i.bankinfo[2]}', separator='')}'
                  f'{i.bankinfo[1]}{i.bankinfo[2]}') for i in bw_list]
    for y, i in enumerate(bw_list):
        if keyword in lazy_info[y]:
            rett.append(i)
    return rett


def get_all_info():
    bank = read_bank_file()
    pre_g = []
    pre_b = []
    for i in bank:
        pre_g += i['genre']
        pre_b.append(i['bunko'])
    return sorted(list(set(pre_g))), sorted(list(set(pre_b)))


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


def refresh_hmz():
    bank = read_bank_file()
    for i in bank:
        hmzpath = f'{i.directory}/{i.name}/{i.numname}.hmz'
        old_hmz = read_json(hmzpath)
        new_hmz = HmzedBook(numname=old_hmz['numname'], name=old_hmz['name'], writer=old_hmz['writer'],
                            allname=old_hmz['allname'], allnet=old_hmz['allnet'], description=old_hmz['discription'])
        new_hmz.save_at(hmzpath)


def update():
    update_to_date()
    post_process()
    refresh_hmz()


if __name__ == '__main__':
    pass
    # refresh_hmz()
    # update_to_date()
    # post_process()
    # generate_book_bank()
    # update()
