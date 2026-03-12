from line_fit import packed as fitting
import requests as rq

from concurrent.futures import ThreadPoolExecutor, as_completed

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 '
                  'Safari/537.36'}
DONE = False


def check_crite(inpu, numname: str, html_num: int):
    global DONE
    if DONE:
        return False
    module = int(numname)//1000
    print(inpu)
    url = f'https://pic.777743.xyz/{module}/{numname}/{html_num}/{inpu}.jpg'
    r1 = rq.get(url, headers=header)
    cont = r1.content
    if cont != b'\xbd\xfb\xd6\xb9\xb7\xc3\xce\xca':
        DONE = True
        return True
    return False


def download_t(inpu, numname: str, html_num: int, adr):
    module = int(numname)//1000
    url = f'https://pic.777743.xyz/{module}/{numname}/{html_num}/{inpu}.jpg'
    r1 = rq.get(url, headers=header)
    cont = r1.content
    if cont != b'\xbd\xfb\xd6\xb9\xb7\xc3\xce\xca':
        with open(adr, 'wb') as f:
            f.write(cont)
        return True
    return False


def process_srh(anchor, numname, html_num, /, limits=2000, bpoint: int = 0):
    depth = 0
    for i in range(1, 12):
        if 2**i * 2 >= 2*limits + 1:
            depth = i
            break

    c = generate_sequence(depth)
    sequence = [int(round(anchor+(2*limits+1)*i, 0)) for i in c][bpoint:]

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_i = {executor.submit(check_crite, i, numname, html_num): i for i in sequence}

        for future in as_completed(future_to_i):
            if future.result():
                executor.shutdown(wait=False)
                return future_to_i[future]

    return -1


def generate_sequence(depth):
    init = [0, 1]
    res = [0, 1]
    for i in range(depth):
        cur = [(init[i]+init[i+1])/2 for i in range(len(init)-1)]
        init += cur
        res += cur
        init.sort()
    return res


def search_for(htm_num: int, numname: str):
    eva_num = fitting(htm_num)
    result = process_srh(int(round(eva_num, 0)), numname, htm_num)
    if result == -1:
        return 'Failed'

    print(result)
    download_t(result, numname, htm_num, f'images/dt/{result}.jpg')
    imglist = [result]
    cur = result
    lcount = 3
    rcount = 3

    while lcount > 0:
        print(cur)
        if not download_t(cur-1, numname, htm_num, f'images/dt/{cur-1}.jpg'):
            lcount -= 1
            continue
        lcount = 3
        imglist.append(cur-1)
        cur -= 1

    cur = result
    while rcount > 0:
        print(cur)
        if not download_t(cur + 1, numname, htm_num, f'images/dt/{cur+1}.jpg'):
            rcount -= 1
            continue
        rcount = 3
        imglist.append(cur + 1)
        cur += 1

    imglist.sort()
    return imglist


if __name__ == '__main__':
    print(search_for(65640, '1861'))
