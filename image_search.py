from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

import requests as rq

from line_fit import packed as fitting
from config import CONFIG, makedir, succeeded
from netwk import GetRq

BORDER_TOLERANCE = CONFIG['BORDER_TOLERANCE']
SEARCH_RANGE = CONFIG['SEARCH_RANGE']

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 '
                  'Safari/537.36'}
DONE = False


def check_crite(inpu, numname: str, html_num: int):
    global DONE
    if DONE:
        return False
    module = int(numname)//1000
    print(inpu, end='/')
    url = f'https://pic.777743.xyz/{module}/{numname}/{html_num}/{inpu}.jpg'
    r1 = rq.head(url, headers=header)
    sleep(0.05)
    if r1:
        DONE = True
    return bool(r1)


def download_t(inpu, numname: str, html_num: int, adr):
    url = f'https://pic.777743.xyz/{int(numname)//1000}/{numname}/{html_num}/{inpu}.jpg'
    r1 = rq.get(url, headers=header)
    cont = r1.content
    if r1:
        with open(adr, 'wb') as f:
            f.write(cont)
        return True
    return False


def process_srh(anchor, numname, html_num, /, limits=SEARCH_RANGE, bpoint: int = 0):
    depth = 0
    for i in range(1, 12):
        if 2**i * 2 >= 2*limits + 1:
            depth = i
            break

    c = generate_sequence(depth)
    sequence = [int(round(anchor+(2*limits+1)*(i-0.5), 0)) for i in c][bpoint:]

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_i = {executor.submit(check_crite, i, numname, html_num): i for i in sequence}

        for future in as_completed(future_to_i):
            if future.result():
                executor.shutdown(wait=False)
                return future_to_i[future]

    return -1


def generate_sequence(depth: int):
    seq = [0, 1]

    for d in range(1, depth + 1):
        denominator = 2 ** d
        candidates = [k / denominator for k in range(1, denominator, 2)]
        candidates.sort(key=lambda x: (abs(x - 0.5), x))
        seq.extend(candidates)

    return seq


def search_for(htm_num: int, numname: str, gaol_folder='images/dt'):
    trial = GetRq(f'https://www.wenku8.cc/novel/{int(numname)//1000}/{numname}/{htm_num}.htm').run('r')
    if not isinstance(trial, int):
        makedir(gaol_folder)
        for y, i in enumerate(trial):
            with open(f'{gaol_folder}/{y+1}.jpg', 'wb') as f:
                f.write(i)
        return True

    eva_num = fitting(htm_num)
    result = process_srh(int(round(eva_num, 0)), numname, htm_num)
    if result == -1:
        return 'Failed'

    makedir(gaol_folder)
    print('\nFirst Image Found!', result)
    download_t(result, numname, htm_num, f'{gaol_folder}/{result}.jpg')
    imglist = [result]

    cur = result
    tolerance = BORDER_TOLERANCE
    while tolerance > 0:
        print(cur,  end=' ')
        if not download_t(cur-1, numname, htm_num, f'{gaol_folder}/{cur-1}.jpg'):
            tolerance -= 1
            continue
        tolerance = BORDER_TOLERANCE
        imglist.append(cur-1)
        cur -= 1

    cur = result
    tolerance = BORDER_TOLERANCE
    while tolerance > 0:
        print(cur, end=' ')
        if not download_t(cur + 1, numname, htm_num, f'{gaol_folder}/{cur+1}.jpg'):
            tolerance -= 1
            continue
        tolerance = BORDER_TOLERANCE
        imglist.append(cur + 1)
        cur += 1

    imglist.sort()
    print('\n', imglist)
    succeeded()
    return imglist


if __name__ == '__main__':
    print(search_for(65640, '1861'))
