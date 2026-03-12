import time

head_ = 'random head'


def measure_time(func, *args, **kwargs):
    a = time.perf_counter()
    r = func(*args, **kwargs)
    b = time.perf_counter()
    return b - a, r


def pre_r(head, con_text0):
    if con_text0.startswith('\n本文来自 轻小说文库(http://www.wenku8.com)\n因版权问题，文库不再提供该小说的阅读！'):
        return 11
    con_text = con_text0.strip().split('\r\n')
    con_text[0] = con_text[0].split('\xa0')[-1]
    clear_con = [i.strip('\xa0') for i in con_text]
    clear_con[-1] = clear_con[-1].split('\n')[0]
    whole_con = ''.join(clear_con)
    res = head + '\n' + whole_con
    return res


def change(num, base):
    l = []
    while num > 0:
        l.append(num % base)
        num //= base
    return l


def new_r(head, con_text0):
    if con_text0.startswith('\n本文来自 轻小说文库(http://www.wenku8.com)\n因版权问题，文库不再提供该小说的阅读！'):
        return 11
    con_text = con_text0.strip()[38:-50].replace('\r\n\xa0\xa0\xa0\xa0', '')
    res = head + '\n' + con_text
    return res


if __name__ == '__main__':
    pass

