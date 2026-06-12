from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from os.path import exists as ext

import requests as rq

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


def rlm_line_fit(x, y, max_iter=50, tol=1e-8):
    n = len(x)

    def median(arr):
        sorted_arr = sorted(arr)
        m = len(sorted_arr)
        if m % 2 == 1:
            return sorted_arr[m // 2]
        else:
            return (sorted_arr[m // 2 - 1] + sorted_arr[m // 2]) / 2.0

    def mad_scale(residuals_):
        """中位数绝对偏差 * 1.4826"""
        med = median(residuals_)
        abs_dev = [abs(r - med) for r in residuals_]
        mad_val = median(abs_dev)
        if mad_val == 0:
            return 1e-10
        return mad_val * 1.4826

    def huber_weights(resid_std_, c=1.345):
        weights_ = []
        for r in resid_std_:
            r_abs = abs(r)
            weights_.append(1.0 if r_abs <= c else c / (r_abs * r_abs))
        return weights_

    def weighted_line_fit(x_, y_, weights_):
        n_ = len(x_)
        sum_w = sum(weights_)
        sum_wx = 0.0
        sum_wy = 0.0
        sum_wx2 = 0.0
        sum_wxy = 0.0

        for i in range(n_):
            w = weights_[i]
            xi = x_[i]
            yi = y_[i]
            sum_wx += w * xi
            sum_wy += w * yi
            sum_wx2 += w * xi * xi
            sum_wxy += w * xi * yi

        denom = sum_w * sum_wx2 - sum_wx * sum_wx

        if abs(denom) < 1e-15:
            b = 0.0
            a = sum_wy / sum_w if sum_w != 0 else 0.0
            return a, b

        b = (sum_w * sum_wxy - sum_wx * sum_wy) / denom
        a = (sum_wy - b * sum_wx) / sum_w
        return a, b

    def calc_residuals(x_, y_, slope_, intercept_):
        residuals_ = []
        for i in range(len(x_)):
            residuals_.append(y_[i] - (intercept_ + slope_ * x_[i]))
        return residuals_

    init_weights = [1.0] * n
    intercept, slope = weighted_line_fit(x, y, init_weights)
    residuals = calc_residuals(x, y, slope, intercept)
    scale = mad_scale(residuals)

    for iteration in range(max_iter):
        resid_std = [r / scale for r in residuals]

        weights = huber_weights(resid_std)

        new_intercept, new_slope = weighted_line_fit(x, y, weights)

        param_change = max(abs(new_intercept - intercept), abs(new_slope - slope))

        intercept, slope = new_intercept, new_slope
        residuals = calc_residuals(x, y, slope, intercept)
        scale = mad_scale(residuals)

        if param_change < tol:
            break

    return {
        'slope': slope,
        'intercept': intercept
    }


def save_history(html_num: int):
    global history, BREAKPOINT
    history[f'{html_num}'] = BREAKPOINT
    save_json('srhistory.json', history, 0)


def save_history_on_exception(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:  # NOQA
            save_history(kwargs['html_num'])
    return wrapper


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
    dd = rlm_line_fit(*zip(*fillter(pos, num)))
    evaluation = num * dd['slope'] + dd['intercept']
    print([dd['slope'], dd['intercept']], '\n', f'Anticipation: {evaluation}')
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
    seq = [0, 1] + [i*0.003 for i in range(-5, 6) if i]

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


if __name__ == '__main__':
    fitting(84933)
