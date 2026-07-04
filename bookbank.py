from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from os import listdir as ldr
from os.path import exists as ext, getctime as gct
from time import mktime as mkt, sleep
from typing import Literal

from pypinyin import slug

from book_struct import BankedBook, BookLuxury, HmzedBook
from config import CONFIG, confirm_name, read_json, find_hmz, save_json, makedir, modify_global_settings
from netwk import get_fullinfo
from prg_export import save_as_rmz as savermz

BANK_PATH = CONFIG['BANK_PATH']
RMZ_EXPORT_PATH = CONFIG['RMZ_EXPORT_PATH']
SIMPLE_BANK_FILE = CONFIG['SIMPLE_BANK_FILE']
ADVANCED_SEARCH_TRIGGER = CONFIG['ADVANCED_SEARCH_TRIGGER']
ENABLE_BANK = CONFIG['ENABLE_BANK']
BANK_UPDATE = CONFIG['BANK_UPDATE']
HMZ_UPDATE = CONFIG['HMZ_UPDATE']
makedir('novel')


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


def generate_book_bank():
    folders = [item for item in ldr(BANK_PATH) if '.' not in item]
    pre_books = []
    for item in folders:
        folder_path = f'{BANK_PATH}/{item}'
        hmz_file = find_hmz(folder_path)
        if hmz_file is not None:
            pre_books.append(read_hmz_par(f'{folder_path}/{hmz_file}'))
    save_as_bank(pre_books)


def read_bank_file():
    if not ext('bank.json'):
        generate_book_bank()
    bookbank = read_json('bank.json')
    newbookbank = [BankedBook(**i) for i in bookbank]
    return newbookbank


def update_hmz(hmzpath):
    numname = hmzpath[:-4].split('/')[-1]
    print(f"Update Required! Auto updating {numname}...")
    hmzbook = get_fullinfo(numname, return_type=1)
    hmzbook.save_at(hmzpath)
    print("Updated!")
    sleep(0.2)
    return hmzbook


def read_hmz_par(hmzpath: str, force_refresh=False, init=False) -> HmzedBook:
    if not force_refresh and HMZFILES.get(hmzpath) is not None:
        return HMZFILES[hmzpath]

    if not ext(hmzpath):
        hmzbook = update_hmz(hmzpath)
        update_hmzfiles(hmzpath, hmzbook)
        return hmzbook

    hmzedfile = read_json(hmzpath)
    try:
        hmzedbook = HmzedBook(**hmzedfile)
    except Exception as e:
        print(e)
        hmzedbook = update_hmz(hmzpath)
        return hmzedbook

    if not init:
        update_hmzfiles(hmzpath, hmzedbook)
    return hmzedbook


def save_as_bank(bank: list[BankedBook]):
    bank_dict = [i.toDict() for i in bank]
    return save_json('bank.json', bank_dict, format_=1 - SIMPLE_BANK_FILE)


def read_file_as_bank(filename):
    bookbank = read_json(filename)
    newbookbank = [BankedBook(**i) for i in bookbank]
    return newbookbank


def get_global_hmzfiles():
    bank = read_bank_file()
    if not bank:
        return {}
    with ThreadPoolExecutor(max_workers=min(len(bank), 16)) as executor:
        futures = []
        for b in bank:
            path = f'{b.directory}/{b.name}/{b.numname}.hmz'
            ft = executor.submit(read_hmz_par, path, force_refresh=True, init=True)
            futures.append((path, ft))
    return {i[0]: i[1].result() for i in futures}


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

    def get_avg_rtg(bankinfo):
        rtg = bankinfo.lux.rtg
        if not rtg:
            return 0.0
        return sum(rtg.values()) / len(rtg)

    if not order or order == 3:
        return sorted(bank, key=lambda bk: (int(bk.numname), bk.name), reverse=sgn)
    elif order == 1:
        return sorted(bank, key=lambda bk: (slug(bk.name, separator=''), int(bk.numname)), reverse=sgn)
    elif order == -1:
        return sorted(bank, key=get_avg_rtg, reverse=sgn)
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

    def get_avg_rtg(bw):
        rtg = bw.bankinfo.lux.rtg
        if not rtg:
            return 0.0
        avg_w = sum(i[1] for i in rtg.values()) / len(rtg)
        return sum(i[0] * i[1] / avg_w for i in rtg) / len(rtg)

    order = constraint[0]
    sgn = not constraint[1]

    if order == 0:
        return sorted(bw_list, key=lambda bk: (int(bk.bankinfo.numname), bk.bankinfo.name), reverse=sgn)
    elif order == 1:
        return sorted(bw_list, key=lambda bk: (slug(bk.bankinfo.name, separator=''), int(bk.bankinfo.numname)),
                      reverse=sgn)
    elif order == 2:
        return sorted(bw_list, key=lambda bk: (int(bk.bankinfo.addtime), bk.bankinfo.name), reverse=sgn)
    elif order == -1:
        return sorted(bw_list, key=get_avg_rtg, reverse=sgn)
    else:
        return sorted(bw_list, key=lambda bk: (bk.bankinfo[order], int(bk.bankinfo.numname)), reverse=sgn)


def parse_srh_unit(unit_str: str) -> tuple | str:
    if '>=' in unit_str:
        cons_pair = unit_str.split('>=')[:2] + ['>=']
    elif '<=' in unit_str:
        cons_pair = unit_str.split('<=')[:2] + ['<=']
    elif '=' in unit_str:
        cons_pair = unit_str.split('=')[:2] + ['==']
    elif '>' in unit_str:
        cons_pair = unit_str.split('>')[:2] + ['>']
    elif '<' in unit_str:
        cons_pair = unit_str.split('<')[:2] + ['<']
    else:
        return unit_str

    if cons_pair[0].strip().lower() == 'liked':
        try:
            cons_vl = int(cons_pair[1].strip())
        except ValueError:
            return unit_str
        if cons_vl == 1 or cons_vl == 0:
            return 'liked', cons_vl, cons_pair[-1]
        return unit_str

    if cons_pair[0].strip().lower() == 'bunko' and cons_pair[-1] == '==':
        return 'bunko', cons_pair[1], cons_pair[-1]

    if cons_pair[0].strip().lower() == 'writer' and cons_pair[-1] == '==':
        return 'writer', cons_pair[1], cons_pair[-1]

    if cons_pair[0].strip().lower() == 'tag' and cons_pair[-1] == '==':
        return 'tag', cons_pair[1], cons_pair[-1]

    if cons_pair[0].strip().lower() == 'numname':
        try:
            cons_vl = int(cons_pair[1].strip())
        except ValueError:
            return unit_str
        return 'numname', cons_vl, cons_pair[-1]

    if cons_pair[0].strip().lower() == 'star':
        try:
            cons_vl = float(cons_pair[1].strip())
        except ValueError:
            return unit_str
        return 'star', cons_vl, cons_pair[-1]

    return unit_str


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
        return []

    if not keyword.startswith(ADVANCED_SEARCH_TRIGGER):
        return [i for i in bw_list if keyword in i.search_str]

    keyword = keyword[len(ADVANCED_SEARCH_TRIGGER):]

    units = keyword.split(' ')
    params_ = []
    keywords = []
    for unit in units:
        uts = parse_srh_unit(unit)
        if isinstance(uts, tuple):
            params_.append(uts)
            continue
        keywords.append(unit)

    for i in params_:
        if i[0] == 'numname':
            bw_list = [bk for bk in bw_list if eval(f'{bk.bankinfo.numname}{i[2]}{i[1]}')]
        if i[0] == 'star':
            bw_list = [bk for bk in bw_list
                       if eval(f'{round(sum(bk.lux_info.rtg.values()) / max(len(bk.lux_info.rtg.values()), 1), 0)}'
                               f'{i[2]}{i[1]}')]
        if i[0] == 'liked':
            bw_list = [bk for bk in bw_list if eval(f'{bk.bankinfo.lux.fav}{i[2]}{i[1]}')]
        if i[0] == 'tag':
            bw_list = [bk for bk in bw_list if i[1] in bk.bankinfo.genre]
        if i[0] == 'bunko':
            bw_list = [bk for bk in bw_list if i[1] in bk.bankinfo.bunko]
        if i[0] == 'writer':
            bw_list = [bk for bk in bw_list if i[1] in bk.bankinfo.writer]

    return [i for i in bw_list if ' '.join(keywords) in i.search_str]


def get_all_info():
    bank = read_bank_file()
    pre_g = []
    pre_b = []
    for i in bank:
        pre_g += i['genre']
        pre_b.append(i['bunko'])
    return sorted(list(set(pre_g))), sorted(list(set(pre_b)))


def refresh_hmz():
    bank = read_bank_file()
    for i in bank:
        hmzpath = f'{i.directory}/{i.name}/{i.numname}.hmz'
        hmzinfo = read_json(hmzpath)
        HMZ_parser(hmzinfo, save=hmzpath)


class HMZ_parser:
    def __init__(self, hmzinfo: dict, save: str | Literal[False] = False):
        self.hmzinfo = hmzinfo
        if hmzinfo.get('discription'):
            version = 0
        elif hmzinfo.get('description'):
            version = 1
        else:
            version = -1

        self.version = version
        self.result = self.parse()
        if save is not False:
            self.result.save_at(save)

    def parse(self):
        if self.version == 0:
            return HmzedBook(numname=self.hmzinfo['numname'], name=self.hmzinfo['name'], writer=self.hmzinfo['writer'],
                             allname=self.hmzinfo['allname'], allnet=self.hmzinfo['allnet'],
                             description=self.hmzinfo['discription'])
        if self.version == 1:
            return HmzedBook(numname=self.hmzinfo['numname'], name=self.hmzinfo['name'], writer=self.hmzinfo['writer'],
                             allname=self.hmzinfo['allname'], allnet=self.hmzinfo['allnet'],
                             description=self.hmzinfo['description'])
        return 0


class BANK_parser:
    def __init__(self, bank: list, save: bool = False):
        self.bank = bank

        if not bank:
            self.result = []
            if save:
                save_as_bank([])
            return

        book1 = self.bank[0]
        version = -1
        if isinstance(book1, list):
            version = 0
        if isinstance(book1, dict):
            version = 1
            if not book1.get('lux'):
                version = -1

        self.version = version
        self.result = self.parse()
        if save:
            save_as_bank(self.result)

    def parse(self):
        if not self.bank:
            return []
        if self.version == 0:
            banked_list = []
            for i in self.bank:
                if len(i) < 6:
                    new_lux = BookLuxury()
                else:
                    new_lux = i[5]
                    new_lux['lck'] = getTimeStampFromString(new_lux['lck']) if new_lux['lck'] else None
                    new_lux = BookLuxury(**new_lux)

                new_book = BankedBook(numname=i[0], name=i[1], writer=i[2], genre=i[3], bunko=i[4], lux=new_lux,
                                      addtime=getCreateTime(f'{BANK_PATH}/{confirm_name(i[1])}/{i[0]}.hmz'),
                                      directory=f"{BANK_PATH}")
                banked_list.append(new_book)
            return banked_list

        if self.version == 1:
            banked_list = []
            for i in self.bank:
                rtg = i['lux']['rtg']
                if not rtg:
                    continue
                value1 = list(rtg.values())[0]
                if isinstance(value1, list):
                    self.version = 2
                    break
            for i in self.bank:
                if self.version == 2:
                    break
                rtg = i['lux']['rtg']
                i['lux']['rtg'] = {i: [rtg[i], 1] for i in rtg.keys()}
                banked_list.append(BankedBook(**i))
            return banked_list

        return []


def update():
    if BANK_UPDATE:
        BANK_parser(read_json('bank.json'), save=True)
        CONFIG['BANK_UPDATE'] = False
        modify_global_settings(CONFIG)
    if HMZ_UPDATE:
        refresh_hmz()
        CONFIG['HMZ_UPDATE'] = False
        modify_global_settings(CONFIG)


update()
HMZFILES = get_global_hmzfiles()


def update_hmzfiles(path=None, hmzbook=None):
    global HMZFILES
    if path:
        HMZFILES[path] = hmzbook
        return
    HMZFILES = get_global_hmzfiles()


def remove_from_bank(numname: str) -> bool:
    """Remove a book from bank.json by numname. Returns True if removed."""
    bank = read_bank_file()
    for i, book in enumerate(bank):
        if book.numname == numname:
            bank.pop(i)
            save_as_bank(bank)
            return True
    return False


def delete_book_files(book: BankedBook) -> bool:
    """Delete a book's directory and thumbnail from disk."""
    from shutil import rmtree
    book_dir = f'{book.directory}/{confirm_name(book.name)}'
    thumbnail = f'images/thumbnails/{book.numname}.jpg'
    deleted = False
    if ext(book_dir):
        rmtree(book_dir)
        deleted = True
    if ext(thumbnail):
        from os import remove as rm
        rm(thumbnail)
        deleted = True
    return deleted


def compare_banks(old_bank: list[BankedBook], new_bank_data: list[BankedBook]) -> tuple[list, list]:
    """Compare two bank lists by numname. Returns (added_dicts, removed_BankedBooks)."""
    old_names = set(old_bank)
    new_names = set(new_bank_data)
    added = new_names - old_names
    removed = old_names - new_names
    return added, removed


if __name__ == '__main__':
    if CONFIG['HMZ_UPDATE']:
        refresh_hmz()
