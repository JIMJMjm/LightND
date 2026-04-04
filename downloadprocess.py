from datetime import datetime
from os.path import exists as ext
from os import listdir as ldr, remove
from concurrent.futures import ThreadPoolExecutor

from winsound import PlaySound

from book_struct import HmzedBook, BankedBook, BookLuxury
from netwk import GetRq, get_fullinfo
from bookbank import add_to_bank
from config import CONFIG, confirm_name, LANG, ordered_ldr, makedir

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/127.0.0.0 '
                        'Safari/537.36'}

MAX_WAORKERS = CONFIG["MAX_THREAD_WORKER"]
AUDD = CONFIG["ALWAYS_USE_DEFAULT_DOWNLOAD"]
IRST = CONFIG["ILLUSTRATION_REQUEST_SLEEP_TIME"]
TRST = CONFIG["TEXT_REQUEST_SLEEP_TIME"]
MAX_VOL_WORKERS = CONFIG["MAX_VOLUME_THREAD_WORKER"]
BANK_PATH = CONFIG["BANK_PATH"]


def get_img(numname, iis=False):
    if ext(f'images/thumbnails/{numname}.jpg'):
        return f'images/thumbnails/{numname}.jpg'
    url = f'https://img.wenku8.com/image/{int(numname) // 1000}/{numname}/{numname}s.jpg'
    m = GetRq(url).run('m')
    with open(f'images/thumbnails/{numname}.jpg', 'wb') as f:
        f.write(m)
    if iis:
        return f'images/thumbnails/{numname}.jpg'
    return m


def succeeded(info='Successful!'):
    print(info)
    PlaySound('dlcp.wav', 1)


def save_file(content, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return 0


def save_img(img: bytes, path):
    with open(path, 'wb') as f:
        f.write(img)
    return 0


class DownloadTask(object):
    def __init__(self, numname: str, state=2, mode=0, merging=False, g_dir=BANK_PATH,
                 update: bool | list[str] | tuple[str, str] = False):
        if not numname:
            print('Not A Numname!')
            return

        if numname == '-2':
            print('Testing Task Object!')
            return

        self.state = state
        self.mode = mode
        self.merging = merging

        if update:
            self.rname = g_dir + '/' + update[1]
            self.numname = update[0]
            self.thisurl = f'https://www.wenku8.cc/novel/{int(update[0]) // 1000}/{update[0]}/'
            self.state = 0
            return

        self.numname = numname
        self.g_dir = g_dir

        modl = numname[0] if len(numname) > 3 else '0'
        self.thisurl = f'https://www.wenku8.cc/novel/{modl}/{numname}/'

        _, name, writer, allnet, allname, descrp, genre, bunko, cprt = get_fullinfo(numname, return_type=0).values()
        name = confirm_name(name)

        self.hmzbook = HmzedBook(numname=numname, name=name, writer=writer,
                                 allnet=allnet, allname=allname, description=descrp)

        self.bankbook = BankedBook(numname=numname, name=name, writer=writer,
                                   bunko=bunko, genre=genre, directory=g_dir,
                                   lux=BookLuxury(), addtime=int(datetime.now().timestamp()))

        self.cprt = cprt
        self.rname = self.hmzbook.name
        if self.g_dir != '':
            self.rname = f'{g_dir}/{self.hmzbook.name}'

        self.__warning = None
        self.progress: int = 0

    def read_page(self, volumeName: str, url: str, fileIndex: int):
        text = GetRq(url).run('t')
        save_file(text, f'{self.rname}/{volumeName}/{fileIndex}.txt')
        return 1

    def illu_page(self, volumeName, url):
        dirnamr = f'{self.rname}/{volumeName}/插图'
        makedir(dirnamr)

        img_list = GetRq(url).run('f')
        for y, i in enumerate(img_list):
            save_img(i, f'{dirnamr}/{y + 1}.jpg')

        return 1

    def process_page(self, i: int, j: int, alllists=None):
        if alllists is None:
            allnet = self.hmzbook.allnet
            allname = self.hmzbook.allname
        else:
            allnet = alllists[0]
            allname = alllists[1]
        url = self.thisurl + allnet[i][j]
        chapter_name = allname[i][j]
        volume_name = allname[i][0]

        if chapter_name == '插图':
            if self.state == 2:
                return 0
            return self.illu_page(volume_name, url)
        if self.state == 1:
            return 0
        return self.read_page(volume_name, url, j)

    def check_current_folder(self, adr, _type=-1):
        if _type == -1:
            volumes = [i[0] for i in self.hmzbook.allnet]
            for i in volumes:
                if i not in ldr(adr):
                    return max(volumes.index(i), 1)
        ord_ = ordered_ldr(adr)
        return len(ord_[0]) + ord_[1]

    def download_volume(self, volume: int):
        dirname = f'{self.rname}/{self.hmzbook.allnet[volume][0]}'
        makedir(dirname)

        with ThreadPoolExecutor(max_workers=MAX_WAORKERS) as executor:
            futures = []
            for j in range(1, len(self.hmzbook.allnet[volume])):
                future = executor.submit(self.process_page, volume, j)
                futures.append(future)

            for future in futures:
                future.result()
        return dirname

    def detailedDownload(self):
        makedir(self.rname)
        self.hmzbook.save_at(f'{self.rname}/{self.numname}.hmz')

        start = self.check_current_folder(self.rname) - 1 if self.mode == 0 else 0
        for i in range(start, len(self.hmzbook.allnet)):
            dirname = self.download_volume(i)

            current_progress = i + 1 - start
            total_tasks = len(self.hmzbook.allnet) - start
            filled_length = int(30 * current_progress // total_tasks)
            bar = '=' * filled_length + ' ' * (30 - filled_length)
            print(f"DL: [{bar}] {(current_progress / total_tasks) * 100:.2f}% ({current_progress}/{total_tasks})",
                  end='\r')

            if self.merging:
                self.mergeToVol(dirname, self.hmzbook.allnet[i][0])
        if self.merging == 2:
            self.mergeToSeries()
        print(LANG['DL_Finished'])

    def default_download(self):
        print('Using "Default Download"... No progress indicators.')
        makedir(self.rname)

        newurl = f'https://dl.wenku8.com/down.php?type=txt&node=2&id={self.numname}'
        tx = GetRq(newurl).run('w')

        save_file(tx, f'{self.rname}/{self.hmzbook.name}.txt')
        self.hmzbook.save_at(f'{self.rname}/{self.numname}.hmz')

        print('Download Finished.')

    @staticmethod
    def mergeToVol(folder, output):
        file_all = ldr(folder)
        if file_all[-1][-4:] != '.txt':
            file_all.pop()

        out = f'{folder}/{output}.txt'
        if ext(out):
            remove(out)

        f = open(out, 'a', encoding='utf-8')
        for i in range(len(file_all)):
            if ext(fn := f'{folder}/{str(i + 1)}.txt'):
                adding = open(fn, encoding='utf-8')
                f.write(adding.read())
                f.write('\n')
        f.close()

    def mergeToSeries(self):
        out = f'{self.rname}/{self.hmzbook.name}.txt'
        if ext(out):
            remove(out)
        f = open(out, 'a', encoding='utf-8')
        for i in range(len(self.hmzbook.allnet)):
            if ext(fn := f'{self.rname}/{self.hmzbook.allnet[i][0]}/{self.hmzbook.allnet[i][0]}.txt'):
                adding = open(fn, encoding='utf-8')
                f.write(adding.read())
                f.write('\n')
        f.close()

    def txt_split(self):
        fileplace = f'{self.rname}/{self.hmzbook.name}.txt'
        with open(fileplace, 'r', encoding='utf-8') as f:
            content = f.readlines()[2:-2]
        true_content = [i.strip(' ') for i in content]

        intervals = []
        for i in self.hmzbook.allname:
            for j in i[1:]:
                chapname = f'{i[0]} {j}'
                curind = content.index(chapname + '\n')
                content[curind] = ''
                intervals.append(curind)
                if j == '插图':
                    true_content[curind] = ''
                    true_content[curind + 1] = ''
                    intervals.pop()

        intervals.append(len(content))

        chapcnt = 0
        for i in self.hmzbook.allname:
            filecount = 1
            setname = f'{self.rname}/{i[0]}'
            makedir(setname)
            cp_in_v = len(i) - 2 if '插图' in i else len(i) - 1
            for j in range(cp_in_v):
                save_file(''.join(true_content[intervals[chapcnt]:intervals[chapcnt + 1]]),
                          f'{setname}/{filecount}.txt')
                filecount += 1
                chapcnt += 1

    def pre_download(self):
        if not ext(fn := f'images/thumbnails/{self.numname}.jpg'):
            tmr = GetRq(f'https://img.wenku8.com/image/{int(self.numname) // 1000}{f'/{self.numname}' * 2}s.jpg').run(
                'm')
            save_img(tmr, fn)
        addbankBool = add_to_bank(BankedBook(numname=self.numname, name=self.hmzbook.name, writer=self.hmzbook.writer,
                                             genre=self.bankbook.genre, bunko=self.bankbook.bunko, lux=None,
                                             addtime=int(datetime.now().timestamp())))
        if addbankBool:
            self.__warning = 'ADDBANK'

    def download(self):
        self.pre_download()

        if not self.cprt:
            self.__warning = 'COPYRIGHT'
            self.default_download()
            self.txt_split()
            return None

        if AUDD:
            self.default_download()
            self.txt_split()
            if self.state != 2:
                self.get_image_from_vol()
            return None

        self.detailedDownload()
        return None

    def downloadslice(self, ind):
        self.pre_download()

        makedir(self.rname)
        self.hmzbook.save_at(f'{self.rname}/{self.numname}.hmz')

        if not self.cprt:
            self.__warning = 'COPYRIGHT'
            self.default_download()
            self.txt_split()
            return 11

        if AUDD:
            self.default_download()
            self.txt_split()
            if self.state != 2:
                self.get_image_from_vol(ind)
            return 11

        partial_allnet = []
        for i in range(len(ind)):
            if ind[i]:
                partial_allnet.append(i)
        for y, i in enumerate(partial_allnet):
            current_progress = y + 1
            total_tasks = len(partial_allnet)
            filled_length = int(30 * current_progress // total_tasks)
            bar = '=' * filled_length + ' ' * (30 - filled_length)
            print(f"DL: [{bar}] {(current_progress / total_tasks) * 100:.2f}% ({current_progress}/{total_tasks})",
                  end='\r')

            self.download_volume(i)
        print(LANG['DL_Finished'])
        return None

    def download_volumes_from_allnet(self, volnets, volnames):
        for y, vol in enumerate(volnets):
            curprogress = y + 1
            totaltasks = len(volnets)
            filled_length = int(30 * curprogress // totaltasks)
            bar = '=' * filled_length + ' ' * (30 - filled_length)
            print(f"DL: [{bar}] {(curprogress / totaltasks) * 100:.2f}% ({curprogress}/{totaltasks})", end='\r')

            dirname = f'{self.rname}/{vol[0]}'
            makedir(dirname)

            with ThreadPoolExecutor(max_workers=MAX_WAORKERS) as executor:
                futures = []
                for j in range(1, len(vol)):
                    future = executor.submit(self.process_page, y, j, (volnets, volnames))
                    futures.append(future)

                for future in futures:
                    future.result()
        hmz = get_fullinfo(self.numname, 1)
        hmz.save_at(f'{self.rname}/{self.numname}.hmz')

        succeeded()

    def get_image_from_vol(self, slice_ind: None | list = None):
        if slice_ind is None:
            post_allname = self.hmzbook.allname
            post_allnet = self.hmzbook.allnet
        else:
            post_allname = [self.hmzbook.allname[i] for i in slice_ind if i]
            post_allnet = [self.hmzbook.allnet[i] for i in slice_ind if i]
        for vol in range(len(post_allname)):
            for a, b in zip(post_allnet[vol], post_allname[vol]):
                if b == '插图':
                    self.illu_page(post_allname[vol][0], self.thisurl + a)

    def getWarning(self):
        return self.__warning


if __name__ == '__main__':
    pass
