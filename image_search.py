from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from os.path import exists as ext

import requests as rq
import statsmodels.api as sm

from config import makedir, succeeded, read_json, CONFIG, save_json
from netwk import GetRq

BORDER_TOLERANCE = CONFIG['BORDER_TOLERANCE']
SEARCH_RANGE = CONFIG['SEARCH_RANGE']
RLM_NEIGHBOR_RANGE = CONFIG['RLM_NEIGHBOR_RANGE']

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 '
                  'Safari/537.36'}
DONE = False
BREAKPOINT = 0
INTERVAL = (22284, 27476, 103972, 105781)
pos = []
if not ext('srhistory.json'):
    save_json('srhistory.json', {}, 0)
history = read_json('srhistory.json')


def save_history(html_num: int):
    global history, BREAKPOINT
    history[f'{html_num}'] = BREAKPOINT
    save_json('srhistory.json', history, 0)


def save_history_on_exception(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            save_history(kwargs['html_num'])
    return wrapper


def curve(x, y):
    X = sm.add_constant(x)
    model = sm.RLM(y, X).fit()
    slope = model.params[1]
    intercept = model.params[0]
    return slope, intercept


def fillter(pots, barrier, loose=RLM_NEIGHBOR_RANGE):
    re = []
    le, ri = barrier - loose, barrier + loose
    for i in INTERVAL:
        if le < i < barrier:
            le = i
        if barrier < i < ri:
            ri = i

    for pot in pots:
        if le <= pot[0] <= ri:
            re.append(pot)
    return re


def fitting(num):
    global pos, history
    if not pos:
        pos = read_json('samples.json')
    dd = curve(*zip(*fillter(pos, num)))
    evaluation = num * dd[0] + dd[1]
    print([float(i) for i in dd], '\n', f'Anticipation: {evaluation}')
    return evaluation


@save_history_on_exception
def check_crite(inpu, numname: str, html_num: int):
    global DONE, BREAKPOINT
    if DONE:
        return False
    print(inpu, end='/')
    url = f'https://pic.777743.xyz/{int(numname)//1000}/{numname}/{html_num}/{inpu}.jpg'
    r1 = rq.head(url, headers=header)
    sleep(0.05)
    BREAKPOINT += 1
    if r1:
        DONE = True
        return bool(r1)
    return False


@save_history_on_exception
def download_t(inpu, numname: str, html_num: int, adr):
    url = f'https://pic.777743.xyz/{int(numname)//1000}/{numname}/{html_num}/{inpu}.jpg'
    r1 = rq.get(url, headers=header)
    cont = r1.content
    if r1:
        with open(adr, 'wb') as f:
            f.write(cont)
        return True
    return False


@save_history_on_exception
def process_srh(anchor, numname: str, html_num: int, /, limits=SEARCH_RANGE):
    global history, BREAKPOINT
    depth = 0
    for i in range(1, 12):
        if 2**i * 2 >= 2*limits + 1:
            depth = i
            break

    BREAKPOINT = history.get(f'{html_num}', 0)
    if BREAKPOINT:
        print(f'Continue the search for {html_num} at the {BREAKPOINT}th attempt.')
    c = generate_sequence(depth)
    sequence = [int(round(anchor+(2*limits+1)*(i-0.5), 0)) for i in c][max(0, BREAKPOINT-10):]

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_i = {executor.submit(check_crite, i, numname, html_num): i for i in sequence}

        for future in as_completed(future_to_i):
            if future.result():
                executor.shutdown(wait=False, cancel_futures=True)
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


@save_history_on_exception
def search_for(html_num: int, numname: str, gaol_folder='images/dt'):
    global DONE, history, BREAKPOINT
    trial = GetRq(f'https://www.wenku8.cc/novel/{int(numname)//1000}/{numname}/{html_num}.htm').run('r')
    if not isinstance(trial, int):
        makedir(gaol_folder)
        for y, i in enumerate(trial):
            with open(f'{gaol_folder}/{y+1}.jpg', 'wb') as f:
                f.write(i)
        return True

    eva_num = fitting(html_num)
    result = process_srh(int(round(eva_num, 0)), numname, html_num)

    history[f'{html_num}'] = BREAKPOINT
    save_json('srhistory.json', history, 0)
    DONE = False
    if result == -1:
        print(1)
        return 'Failed'

    makedir(gaol_folder)
    print('\nFirst Image Found!', result)
    download_t(result, numname, html_num, f'{gaol_folder}/{result}.jpg')
    imglist = [result]

    cur = result
    tolerance = BORDER_TOLERANCE
    while tolerance > 0:
        if not download_t(cur-1, numname, html_num, f'{gaol_folder}/{cur - 1}.jpg'):
            tolerance -= 1
            cur -= 1
            continue
        print(cur, end=' ')
        tolerance = BORDER_TOLERANCE
        imglist.append(cur-1)
        cur -= 1

    cur = result
    tolerance = BORDER_TOLERANCE
    while tolerance > 0:
        if not download_t(cur + 1, numname, html_num, f'{gaol_folder}/{cur + 1}.jpg'):
            tolerance -= 1
            cur += 1
            continue
        print(cur, end=' ')
        tolerance = BORDER_TOLERANCE
        imglist.append(cur + 1)
        cur += 1

    imglist.sort()
    print('\n', imglist)
    succeeded()
    return imglist
