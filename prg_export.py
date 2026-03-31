import json
from re import match as rmatch
from os.path import exists as ext
from datetime import datetime
from typing import Literal

from book_struct import BankedBook
from config import CONFIG

RMZ_EXPORT_PATH = CONFIG['RMZ_EXPORT_PATH']
RMZ_FILENAME_FORMAT = CONFIG['RMZ_FILENAME_FORMAT']
RMZ_FILENAME_SUFFIX = CONFIG['RMZ_FILENAME_SUFFIX']


def tag_replace(tag: str, _data: BankedBook):
    pattern = r'^([A-Z]+)(?:\[(-?\d+)\])?$'
    mrt = rmatch(pattern, tag)
    if not mrt:
        return ''
    match_list = [mrt.group(1), None if mrt.group(2) is None else int(mrt.group(2))]
    match match_list:
        case ['TMSTAMP', num]:
            string = str(int(datetime.now().timestamp()))
        case ['NUMNAME', num]:
            string = _data.numname
        case ['BKNAME', num]:
            string = _data.name
        case ['DATETIME', num]:
            string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        case _:
            return ''

    return string if num is None else string[:num] if num > 0 else string[num:]


def parse_rmz_format(_format: str, _data: BankedBook) -> str:
    i = 0
    component = 0
    goal = ''
    temp = ''
    while i < len(_format):
        if _format[i] == '%' and not component:
            component = 1
            i += 1
            continue
        if _format[i] == '%' and component:
            replacement = tag_replace(temp, _data)
            if not replacement:
                goal += f'%{temp}%'
            else:
                goal += replacement
            temp = ''
            component = 0
            i += 1
            continue
        if component:
            temp += _format[i]
            i += 1
            continue

        goal += _format[i]
        i += 1
    return goal


def save_as_rmz(_type: Literal[1, 2, 3], _data: BankedBook, path, filename: str = None) -> str:
    """
    Export bank data as (.rmz) files. Numname and name must be given.
    :param path: the path data exported to.
    :param filename: the rmz filename. Default is int(time() * 1000)
    :param _type: indicate the type of data received.
                  1 -> whole bank entry; 2 -> luxury data; 3 -> 'prg' and 'rtg' data.
    :param _data: data to be exported.
    :return: None.
    """
    if filename is None:
        filename = str(int(datetime.now().timestamp()))
    filename = parse_rmz_format(filename, _data)

    suffix = 0

    perisuffix = RMZ_FILENAME_SUFFIX.split('%NUM%')
    if not perisuffix[0]:
        perisuffix = ['(', ')']
    if len(perisuffix) < 2:
        perisuffix = perisuffix * 2
    if len(perisuffix) > 2:
        perisuffix[1] = '%NUM%'.join(perisuffix[1:])

    pfilename = filename
    while ext(f'{path}/{pfilename}.rmz'):
        suffix += 1
        pfilename = f'{filename}{perisuffix[0]}{suffix}{perisuffix[1]}'

    type_byte = None
    if _type == 1:
        type_byte = b'BANK'
    if _type == 2:
        type_byte = b'LUXU'
    if _type == 3:
        type_byte = b'PRRT'
    with open(f'{path}/{pfilename}.rmz', 'wb') as f:
        f.write(b'RHMZ')
        f.write(type_byte)
        f.write(json.dumps(_data.toDict()).encode('utf-8'))
    return filename


def read_from_rmz(filename) -> tuple[list, int]:
    _type = 0
    with open(filename, 'rb') as f:
        f.read(4)
        tp = f.read(4)
        if tp == b'BANK':
            _type = 1
        if tp == b'LUXU':
            _type = 2
        if tp == b'PRRT':
            _type = 3
        content = f.read().decode('utf-8')
    return json.loads(content), _type


if __name__ == '__main__':
    pass
